"""M1-2 데이터 비서를 MCP(Model Context Protocol) 서버로도 노출한다.

보너스 과제 "AI 도구 호출 + 멀티채널 연동" 요구사항 중 두 번째 조건 —
"동일 기능을 MCP Server 또는 GPT Actions 중 1개 방식으로도 연동해
(외부 채널/클라이언트) 호출 흐름을 검증한다" — 를 위한 것이다.

app/services/chat_service.py의 Function Calling에서 쓰는 것과 같은
내부 함수(data_service)를 그대로 재사용해, Claude Desktop 같은 MCP
클라이언트에서도 동일한 세 가지 도구를 호출할 수 있게 한다.

로컬 실행:
    pip install "mcp[cli]"
    python mcp_server.py

Claude Desktop 등록 예 (claude_desktop_config.json):
    {
      "mcpServers": {
        "m1-2-data-assistant": {
          "command": "python",
          "args": ["C:/Users/.../M1-2/mcp_server.py"]
        }
      }
    }
"""

from mcp.server.mcpserver import MCPServer

from app.services import data_service

mcp = MCPServer("m1-2-data-assistant")


@mcp.tool()
def get_data_summary() -> dict:
    """한국 방한 외래관광객 월별 시계열의 요약(기간/개수/평균/최대/최소/최근 추세)을 반환한다."""
    return data_service.get_summary().model_dump()


@mcp.tool()
def get_data_statistics() -> dict:
    """요약(summary)에 없는 세부 통계 — 중앙값, 표준편차, 최근 12개월 평균,
    전년 동기 대비 증감률(%) — 을 반환한다."""
    return data_service.get_statistics().model_dump()


@mcp.tool()
def search_data_by_period(start_date: str, end_date: str) -> dict:
    """YYYY-MM ~ YYYY-MM 기간의 실제 데이터 레코드를 조회한다.

    Args:
        start_date: 조회 시작월, YYYY-MM 형식
        end_date: 조회 종료월, YYYY-MM 형식
    """
    rows = [
        row.model_dump()
        for row in data_service.list_data()
        if start_date <= row.date <= end_date
    ]
    return {"count": len(rows), "records": rows}


if __name__ == "__main__":
    mcp.run()
