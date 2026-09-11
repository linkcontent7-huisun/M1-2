"""컨텍스트 주입 챗봇의 핵심 로직.

흐름: 데이터 요약 조회 → 시스템 프롬프트에 삽입 → 기존 대화 이력과 함께
GPT 호출(도구 정의 포함) → GPT가 도구 호출을 요청하면 실제 내부 함수를
실행해 결과를 돌려주고 재호출(최대 3회) → 최종 답변을 사용자/AI 메시지로
conversations에 저장.

보너스 과제 "AI 도구 호출(Function Calling)": 시스템 프롬프트에 이미
요약이 박혀 있지만, 중앙값·표준편차 같은 세부 통계나 특정 기간 조회처럼
매 대화마다 미리 넣어두기엔 아까운 정보는 GPT가 필요할 때만 도구로
가져오게 한다.
"""

import json

from app.config import settings
from app.openai_client import get_client
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.conversation import Message
from app.schemas.data import DataSummary
from app.services import conversation_service, data_service

SYSTEM_PROMPT_TEMPLATE = """당신은 데이터 분석 비서입니다.

[사용자 데이터 요약]
- 데이터 기간: {period}
- 총 레코드: {count}개
- 주요 지표: 합계 {total}, 평균 {average:.1f}, 최대 {max}, 최소 {min}
- 최근 트렌드: {trend}

위 데이터를 기반으로 맞춤형 답변을 제공하세요. 데이터에 없는 내용은
추측하지 말고 모른다고 답하세요. 중앙값·표준편차·전년 대비 증감률처럼
요약에 없는 세부 통계나 특정 기간의 수치가 필요하면 제공된 도구를
호출해서 확인한 뒤 답하세요."""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_data_statistics",
            "description": (
                "중앙값, 표준편차, 최근 12개월 평균, 전년 동기 대비 증감률 등 "
                "요약(summary)에 없는 세부 통계 지표를 조회한다."
            ),
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_data_by_period",
            "description": "YYYY-MM ~ YYYY-MM 기간의 실제 데이터 레코드를 조회한다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {"type": "string", "description": "조회 시작월, YYYY-MM"},
                    "end_date": {"type": "string", "description": "조회 종료월, YYYY-MM"},
                },
                "required": ["start_date", "end_date"],
            },
        },
    },
]


def _execute_tool(name: str, arguments: dict) -> dict:
    """GPT가 요청한 도구 이름에 맞는 내부 함수를 실행하고 결과를 dict로 반환한다."""
    if name == "get_data_statistics":
        return data_service.get_statistics().model_dump()

    if name == "search_data_by_period":
        start, end = arguments.get("start_date", ""), arguments.get("end_date", "")
        rows = [row for row in data_service.list_data() if start <= row.date <= end]
        if not rows:
            return {"count": 0}

        values = [row.value for row in rows]
        # gpt-5-mini(추론 모델)가 토큰을 아끼도록 원본 레코드를 다 넣지 않고
        # 요약 통계 + 대표 값(최신 6개)만 돌려준다.
        return {
            "count": len(rows),
            "average": sum(values) / len(values),
            "max": max(values),
            "min": min(values),
            "sample_records": [row.model_dump() for row in rows[-6:]],
        }

    return {"error": f"알 수 없는 도구입니다: {name}"}


def _build_system_prompt(summary: DataSummary) -> str:
    return SYSTEM_PROMPT_TEMPLATE.format(
        period=summary.period,
        count=summary.count,
        total=summary.metrics.total,
        average=summary.metrics.average,
        max=summary.metrics.max,
        min=summary.metrics.min,
        trend=summary.trend,
    )


def get_ai_reply(request: ChatRequest) -> ChatResponse:
    summary = data_service.get_summary()
    conversation = conversation_service.get_or_create(request.conversation_id)

    api_messages = [{"role": "system", "content": _build_system_prompt(summary)}]
    api_messages += [m.model_dump() for m in conversation.messages]
    api_messages.append({"role": "user", "content": request.message})

    client = get_client()
    completion = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=api_messages,
        tools=TOOLS,
        tool_choice="auto",
        max_tokens=settings.OPENAI_MAX_TOKENS,
    )
    message = completion.choices[0].message

    # GPT가 도구 호출을 요청하면 실제로 실행하고 결과를 돌려준 뒤 재호출한다.
    # 무한 루프 방지를 위해 최대 4회로 제한한다.
    for _ in range(4):
        if not message.tool_calls:
            break

        # message.model_dump()를 그대로 넣으면 코디세이 API가 모르는 부가 필드
        # (refusal, annotations 등)까지 같이 전송되어 400(unsupported_feature)이
        # 난다. 표준 스펙에 필요한 필드만 추려서 넣는다.
        api_messages.append(
            {
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in message.tool_calls
                ],
            }
        )
        for tool_call in message.tool_calls:
            arguments = json.loads(tool_call.function.arguments or "{}")
            result = _execute_tool(tool_call.function.name, arguments)
            api_messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result, ensure_ascii=False, default=str),
                }
            )

        completion = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=api_messages,
            tools=TOOLS,
            tool_choice="auto",
            max_tokens=settings.OPENAI_MAX_TOKENS,
        )
        message = completion.choices[0].message

    # 루프 한도 안에 GPT가 도구 호출을 끝내지 못했다면(반복 호출 등),
    # tool_choice="none"으로 도구 없이 지금까지의 결과만으로 답하게 강제한다.
    if message.tool_calls:
        completion = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=api_messages,
            tool_choice="none",
            max_tokens=settings.OPENAI_MAX_TOKENS,
        )
        message = completion.choices[0].message

    reply = message.content or "죄송합니다. 답변을 생성하지 못했습니다."

    conversation_service.append_messages(
        conversation.id,
        [
            Message(role="user", content=request.message),
            Message(role="assistant", content=reply),
        ],
    )

    return ChatResponse(reply=reply, conversation_id=conversation.id)
