# M1-2 — AI Agent 개발: 나만의 AI 비서 구축

저장소: <https://github.com/linkcontent7-huisun/M1-2>

## 개요

국내 주요 성지 소재 지자체(명동성당·나바위성지 등)의 월별 방문자 수를 시계열로 분석하고,
요약 결과를 시스템 프롬프트에 주입해 대화하는 AI 데이터 비서. FastAPI + Firestore + GPT API로
백엔드를 구성하고, 바닐라 HTML/CSS/JS로 프론트엔드를 만들어 Render/Vercel에 배포한다.

이 과제는 [M1-1](https://github.com/linkcontent7-huisun/M1-1-tourism-trend)에서
검증한 한국관광 데이터랩 API를 재사용하며, 스키마는 향후 visitholykorea(가톨릭 성지순례 앱)
관리자용 AI 비서로, 나아가 코디세이 Final Project 캡스톤으로 이어지도록 설계했다.
자세한 근거는 [`specs/tech-stack-analysis.md`](specs/tech-stack-analysis.md) 참고.

## 요구사항 체크리스트

[`specs/requirements-checklist.md`](specs/requirements-checklist.md)

## 진행 상태

🚧 설계 완료, 구현 시작 전 — 2026-09-07

## 실행 방법

(구현 후 작성)

## 환경 변수

| 변수명 | 설명 |
|---|---|
| `OPENAI_API_KEY` | OpenAI API 키 |
| `FIREBASE_SERVICE_ACCOUNT_JSON` | Firebase 서비스 계정 키(JSON) |
| `API_BASE_URL` | 프론트엔드가 호출할 백엔드 주소 |
| `ALLOWED_ORIGINS` | CORS 허용 도메인 |

## 배포 URL

(배포 후 작성 — 프론트 / 백엔드 API / Swagger)
