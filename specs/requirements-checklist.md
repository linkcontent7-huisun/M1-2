# M1-2 요구사항 체크리스트

원본 명세: [`specs/M1-2-ai-agent.md`](../../../specs/M1-2-ai-agent.md) (허브 저장소)

배포 후 실사용 검증까지 마친 상태(2026-09-11). curl로 배포된 API를 직접 호출하고,
Vercel 배포 사이트에서 채팅·데이터 관리·대화 기록을 실제로 조작해 확인했다.

## 1. 개발 환경

- [x] Python 3.13 venv 구성 — `.venv`
- [x] `fastapi` `uvicorn` `firebase-admin` `openai` `python-dotenv` 설치
- [x] Firebase 프로젝트 생성 + 서비스 계정 키 발급(`m1-2-2418b`)
- [x] OpenAI 호환 API 키 준비 — 코디세이 공개 API(`gpt-5-mini`) 사용
- [x] Render, Vercel 계정 준비 및 배포 완료

## 2. 데이터 선정 및 분석

- [x] 시계열 데이터 100개 이상 확보 — 한국관광공사 월별 방한 외래관광객 수 139건
      (2015-01~2026-07, `data/foreign_visitors_monthly.csv`, M1-1 검증 데이터 재사용)
- [x] 요약 정보 산출: 기간 / 개수 / 평균·최대·최소 / 최근 추세 —
      `GET /api/data/summary`, Firestore 139건 적재 후 실데이터로 재검증 완료

## 3. FastAPI 프로젝트 구성

- [x] CORS 설정 — `main.py`, `ALLOWED_ORIGINS` 환경 변수 기반
- [x] `uvicorn main:app --reload` 로컬 실행 확인
- [x] `/docs` Swagger UI 확인 — 배포 URL에서 200 확인(`https://m1-2-2pob.onrender.com/docs`)

## 4. Firestore 연동

- [x] 서비스 계정 키는 환경 변수로 관리(코드 하드코딩 금지) — `app/firebase.py`, `FIREBASE_SERVICE_ACCOUNT_JSON`
- [x] 컬렉션 `data`(분석 데이터), `conversations`(대화 기록) 설계
- [x] 실제 Firestore 적재·검증 — `scripts/import_foreign_visitors.py`로 139건 적재,
      Cloud Firestore API·Firestore Database 활성화 완료, `/api/data/summary`로 재검증

## 5. 데이터 API (CRUD + summary) — 배포 환경에서 curl로 전부 검증 완료

- [x] `POST /api/data` — 실제 요청으로 레코드 생성 확인
- [x] `GET /api/data` — 139건 정상 조회
- [x] `PUT /api/data/{id}` — 수정 후 값 반영 확인
- [x] `DELETE /api/data/{id}` — 204 확인
- [x] `GET /api/data/summary` — 기간·개수·평균/최대/최소·추세(절반 비교) 정상 계산

## 6. 대화 기록 API — 배포 환경에서 curl + 프론트 UI로 검증 완료

- [x] `POST /api/conversations`
- [x] `GET /api/conversations`
- [x] `DELETE /api/conversations/{id}`
- [x] 대화 불러오기: **A안** `GET /api/conversations/{id}` 채택·구현
- [x] **버그 수정**: 목록 화면이 `messages[0]`을 읽으려 해 항상 "(빈 대화)"만 보이던 문제,
      `loadConversation`이 전역 `event` 참조로 깨지던 문제를 고쳤다([[verify-dont-trust-status]] 교훈대로
      배포 후 직접 클릭해보다 발견).

## 7. AI 챗봇 API (컨텍스트 주입) — 배포 환경에서 실제 응답 확인 완료

- [x] `POST /api/chat`: 요약 조회 → 시스템 프롬프트 삽입 → GPT 호출 → `conversations` 자동 저장
- [x] **버그 수정**: 프론트가 `response.response`(존재하지 않는 필드)를 읽어 AI 답변이 항상
      빈 말풍선으로 보이던 문제. 백엔드 `ChatResponse.reply`에 맞춰 고쳤다.
- [x] 개인 OpenAI 크레딧 소진 이후 코디세이 공개 API(`OPENAI_BASE_URL=https://copa.codyssey.kr/v1`,
      `gpt-5-mini`)로 전환, 실제 응답 확인

## 8. 백엔드 배포 (Render)

- [x] GitHub 푸시
- [x] Render Web Service 생성·배포 — <https://m1-2-2pob.onrender.com>
- [x] 배포 URL `/docs` 확인
- [x] 콜드스타트 안내 문구 — README에 명시(무료 티어, 첫 요청 50초 이상 지연 가능)

## 9. 웹 프론트엔드 (바닐라 HTML/CSS/JS)

- [x] 채팅 인터페이스: 입력·표시·로딩 — 배포 사이트에서 실제 질문·답변 확인
- [x] 데이터 관리: 추가·목록 — 배포 사이트에서 추가 동작 실제 확인(수정 UI는 미구현,
      삭제/추가로 CRUD 중 최소 1개 이상 동작 조건 충족)
- [x] 대화 기록: 목록·불러오기 — 버그 수정 후 배포 사이트에서 실제 확인
- [x] 데이터 요약(기간/개수/트렌드) 화면 표시

## 10. 프론트엔드 배포 (Vercel) + 문서화

- [x] Vercel 배포 — <https://m1-2-peach.vercel.app>, 환경 변수로 API 서버 URL 설정
- [x] README: 서비스 소개 / 기술 스택 / 배포 URL(프론트·백엔드·Swagger) / 로컬 실행법 / 환경 변수 목록
- [x] 제출 스크린샷 3종 — `docs/screenshots/`
      (`01_chat_summary.png` 채팅+요약, `02_data_management.png` 데이터 관리,
      `03_conversations.png` 대화 기록)

## 보너스 (선택, 우선순위 낮음) — 4/5 완료

- [ ] Function Calling + MCP/GPT Actions 연동 — **미착수**. 코디세이 공개 API의 tool calling
      지원 여부가 문서화되어 있지 않고, MCP Server는 별도 배포가 필요해 범위를 크게 벗어난다.
- [x] `/api/data/statistics` 추가 지표 — 중앙값·표준편차·최근 12개월 평균·전년 대비 증감률
      (`app/services/data_service.py:get_statistics`), 배포 환경에서 curl로 검증 완료
- [x] 프론트 시각화 그래프 1개 — 채팅 탭 요약 아래 바닐라 Canvas 추세 라인 그래프
      (`public/js/app.js:drawTrendChart`), 외부 차트 라이브러리 없이 구현
- [x] CSV/JSON 내보내기 — 데이터 관리 탭 버튼, Blob+다운로드 링크로 실제 다운로드 확인
- [x] 다크 모드 토글 — 헤더 토글 버튼, `localStorage`로 새로고침 후에도 유지, 그래프도
      테마에 맞춰 재렌더링. 배포 사이트에서 실제 토글 동작 확인(`docs/screenshots/04_dark_mode.png`)
