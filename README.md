# M1-2 — AI Agent 개발: 나만의 AI 비서 구축

저장소: <https://github.com/linkcontent7-huisun/M1-2>

## 개요

한국관광공사의 **월별 방한 외래관광객 수**를 시계열로 분석하고, 요약 결과를 시스템 프롬프트에
주입해 대화하는 AI 데이터 비서. FastAPI + Firestore + GPT API로 백엔드를 구성하고,
바닐라 HTML/CSS/JS로 프론트엔드를 만들어 Render/Vercel에 배포한다.

이 과제는 [M1-1](https://github.com/linkcontent7-huisun/M1-1-tourism-trend)에서
검증한 한국관광 데이터랩 데이터를 재사용한다. 2015-01~2026-07의 139개 월별 관측치를 포함해
과제의 100건 이상 시계열 요건을 충족한다. 이 지표는 향후 visitholykorea(가톨릭 성지순례 앱)의
해외 이용자 저변을 가늠하는 참고 지표이며, 나아가 코디세이 Final Project 캡스톤으로 이어지도록
설계했다.
자세한 근거는 [`specs/tech-stack-analysis.md`](specs/tech-stack-analysis.md) 참고.

## 요구사항 체크리스트

[`specs/requirements-checklist.md`](specs/requirements-checklist.md)

## 진행 상태

🚧 FastAPI 스캐폴딩 완료(데이터 5개·대화 4개·채팅 1개 API, Swagger UI 확인), 139건 실데이터 CSV 포함 — Firebase 연결·Firestore 적재와 프론트엔드 미착수 — 2026-09-09

## 프로젝트 구조

```
main.py                  FastAPI 앱 생성, CORS, 라우터 연결, 공통 예외 처리
app/
├── config.py             환경 변수 로드
├── firebase.py           Firestore 클라이언트 (지연 초기화)
├── openai_client.py      OpenAI 클라이언트 (지연 초기화)
├── schemas/               Pydantic 요청/응답 모델
│   ├── data.py
│   ├── conversation.py
│   └── chat.py
├── services/               비즈니스 로직 (Firestore 읽기/쓰기, 통계, GPT 호출)
│   ├── data_service.py
│   ├── conversation_service.py
│   └── chat_service.py
└── routers/                 HTTP 엔드포인트만 담당(얇게 유지)
    ├── data.py
    ├── conversations.py
    └── chat.py
```

## 실행 방법

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # 값 채우기
uvicorn main:app --reload
```

`http://localhost:8000/docs`에서 Swagger UI 확인. Firebase/OpenAI 키가 없어도 서버는
뜨고 `/docs`는 보이지만, 실제 데이터 API를 호출하면 `503`으로 어떤 환경 변수가
빠졌는지 알려준다(코드 하드코딩 없이 지연 초기화하도록 설계).

## 실데이터 적재

[`data/foreign_visitors_monthly.csv`](data/foreign_visitors_monthly.csv)는 한국관광공사 관광데이터랩의
월별 방한 외래관광객 수 139건(2015-01~2026-07)이다. 먼저 CSV를 검증하고, Firebase 환경 변수를
연결한 후 Firestore에 적재한다.

```bash
python scripts/import_foreign_visitors.py --dry-run
python scripts/import_foreign_visitors.py
```

두 번째 명령은 동일한 월(`date`)이 이미 있으면 건너뛰므로 재실행해도 중복 적재하지 않는다.
첫 적재 전 Firebase Console에서 해당 프로젝트의 **Cloud Firestore API**와 Firestore 데이터베이스를
활성화해야 한다.

## 환경 변수

| 변수명 | 설명 |
|---|---|
| `OPENAI_API_KEY` | OpenAI API 키 |
| `FIREBASE_SERVICE_ACCOUNT_JSON` | Firebase 서비스 계정 키(JSON) |
| `API_BASE_URL` | 프론트엔드가 호출할 백엔드 주소 |
| `ALLOWED_ORIGINS` | CORS 허용 도메인 |

## 배포 URL

(배포 후 작성 — 프론트 / 백엔드 API / Swagger)
