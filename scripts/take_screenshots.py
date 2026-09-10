"""제출용 스크린샷 3종을 배포된 사이트에서 직접 캡처한다.

1. 채팅 화면 (질문+답변+데이터 요약)
2. 데이터 관리 화면 (데이터 추가 동작 확인)
3. 대화 기록 화면 (대화 목록+불러오기)
"""
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

URL = "https://m1-2-peach.vercel.app"
OUT_DIR = Path(__file__).resolve().parent.parent / "docs" / "screenshots"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1000, "height": 900})
        page.goto(URL, wait_until="networkidle")
        page.wait_for_timeout(1500)

        # 1) 채팅 화면: 질문 입력 -> 전송 -> AI 응답 대기 -> 캡처
        page.fill('input[placeholder*="질문을 입력하세요"]', "최근 방한객 수 트렌드를 한 문장으로 요약해줘")
        page.click('button[type="submit"]:has-text("전송")')
        page.wait_for_selector(".message.assistant", timeout=60000)
        page.wait_for_timeout(1000)
        page.screenshot(path=str(OUT_DIR / "01_chat_summary.png"), full_page=True)
        print("saved 01_chat_summary.png")

        # 2) 데이터 관리 화면: 탭 이동 -> 새 데이터 추가 -> 목록 반영 확인 -> 캡처
        page.click('button[data-tab="data"]')
        page.wait_for_timeout(1000)
        page.fill("#data-date", "2026-09")
        page.fill("#data-value", "1234567")
        page.fill("#data-memo", "제출 스크린샷용 샘플 데이터")
        page.once("dialog", lambda d: d.accept())
        page.click('#data-form button[type="submit"]')
        page.wait_for_timeout(2000)
        new_item = page.query_selector(".data-item:has-text('제출 스크린샷용 샘플 데이터')")
        if new_item:
            new_item.scroll_into_view_if_needed()
            page.wait_for_timeout(500)
        page.screenshot(path=str(OUT_DIR / "02_data_management.png"), full_page=True)
        print("saved 02_data_management.png")

        # 방금 추가한 샘플 데이터 정리(삭제) - 실제 139건 데이터만 남긴다
        if new_item:
            page.once("dialog", lambda d: d.accept())
            new_item.query_selector(".btn-delete").click()
            page.wait_for_timeout(1500)

        # 3) 대화 기록 화면: 탭 이동 -> 목록에서 첫 대화 클릭(불러오기) -> 캡처
        page.click('button[data-tab="conversations"]')
        page.wait_for_timeout(1500)
        first_conv = page.query_selector(".conversation-item")
        if first_conv:
            first_conv.click()
            page.wait_for_timeout(1000)
        page.screenshot(path=str(OUT_DIR / "03_conversations.png"), full_page=True)
        print("saved 03_conversations.png")

        browser.close()


if __name__ == "__main__":
    run()
