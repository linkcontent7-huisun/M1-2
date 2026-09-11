"""mcp_server.py가 실제로 MCP 클라이언트에서 호출 가능한지 검증한다.

stdio로 서버 프로세스를 띄우고, 표준 MCP 클라이언트 세션으로
1) 도구 목록을 조회하고 2) 각 도구를 실제로 호출해 결과를 확인한다.
"""

import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    params = StdioServerParameters(command=sys.executable, args=["mcp_server.py"])

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("=== 등록된 도구 ===")
            for t in tools.tools:
                print(f"- {t.name}: {t.description}")

            print("\n=== get_data_summary 호출 ===")
            result = await session.call_tool("get_data_summary", {})
            print(result.content[0].text)

            print("\n=== get_data_statistics 호출 ===")
            result = await session.call_tool("get_data_statistics", {})
            print(result.content[0].text)

            print("\n=== search_data_by_period 호출 (2020-03~2020-06) ===")
            result = await session.call_tool(
                "search_data_by_period", {"start_date": "2020-03", "end_date": "2020-06"}
            )
            print(result.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())
