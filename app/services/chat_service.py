"""컨텍스트 주입 챗봇의 핵심 로직.

흐름: 데이터 요약 조회 → 시스템 프롬프트에 삽입 → 기존 대화 이력과 함께
GPT 호출 → 사용자/AI 메시지를 conversations에 저장.
"""

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
추측하지 말고 모른다고 답하세요."""


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
        max_tokens=settings.OPENAI_MAX_TOKENS,
    )
    reply = completion.choices[0].message.content

    conversation_service.append_messages(
        conversation.id,
        [
            Message(role="user", content=request.message),
            Message(role="assistant", content=reply),
        ],
    )

    return ChatResponse(reply=reply, conversation_id=conversation.id)
