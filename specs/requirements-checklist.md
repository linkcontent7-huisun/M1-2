# M1-2 요구사항 체크리스트

원본 명세: [`specs/M1-2-ai-agent.md`](../../../specs/M1-2-ai-agent.md) (허브 저장소)

## 1. 개발 환경

- [ ] Python 3.10+ venv 구성
- [ ] `fastapi` `uvicorn` `firebase-admin` `openai` `python-dotenv` 설치
- [ ] Firebase 프로젝트 생성 + 서비스 계정 키 발급
- [ ] OpenAI API 키 발급
- [ ] Render, Vercel 계정 준비

## 2. 데이터 선정 및 분석

- [ ] 시계열 데이터 100개 이상 확보 — **국내 주요 성지 소재 지자체 월별 방문자 수**
      (한국관광 데이터랩, [[m1-1-tourism-trend]] 방식 재사용)
- [ ] 요약 정보 산출: 기간 / 개수 / 평균·최대·최소 / 최근 추세

## 3. FastAPI 프로젝트 구성

- [ ] CORS 설정
- [ ] `uvicorn main:app --reload` 로컬 실행 확인
- [ ] `/docs` Swagger UI 확인

## 4. Firestore 연동

- [ ] 서비스 계정 키는 환경 변수로 관리(코드 하드코딩 금지)
- [ ] 컬렉션 `data`(분석 데이터), `conversations`(대화 기록) 설계

## 5. 데이터 API (CRUD + summary)

- [ ] `POST /api/data`
- [ ] `GET /api/data`
- [ ] `PUT /api/data/{id}`
- [ ] `DELETE /api/data/{id}`
- [ ] `GET /api/data/summary`

## 6. 대화 기록 API

- [ ] `POST /api/conversations`
- [ ] `GET /api/conversations`
- [ ] `DELETE /api/conversations/{id}`
- [ ] 대화 불러오기: (A) `GET /api/conversations/{id}` 또는 (B) 목록 응답에 messages 포함 — **A안 채택 예정**

## 7. AI 챗봇 API (컨텍스트 주입)

- [ ] `POST /api/chat`: 요약 조회 → 시스템 프롬프트 삽입 → GPT 호출 → `conversations` 자동 저장

## 8. 백엔드 배포 (Render)

- [ ] GitHub 푸시
- [ ] Render Web Service 생성·배포
- [ ] 배포 URL `/docs` 확인
- [ ] 콜드스타트 안내 문구/대응 준비

## 9. 웹 프론트엔드 (바닐라 HTML/CSS/JS)

- [ ] 채팅 인터페이스: 입력·표시·로딩
- [ ] 데이터 관리: 추가·목록, CRUD 중 최소 1개 화면에서 동작 확인
- [ ] 대화 기록: 목록·불러오기
- [ ] 데이터 요약(기간/개수/트렌드) 화면 표시

## 10. 프론트엔드 배포 (Vercel) + 문서화

- [ ] Vercel 배포, 환경 변수로 API 서버 URL 설정
- [ ] README: 서비스 소개 / 기술 스택 / 배포 URL(프론트·백엔드·Swagger) / 로컬 실행법 / 환경 변수 목록
- [ ] 제출 스크린샷 3종(채팅+요약, 데이터 관리, 대화 기록) — **보조 자료**, 본문 설명은 `.md`로 별도 작성([[codyssey-submission-checklist-habit]])

## 보너스 (선택, 우선순위 낮음)

- [ ] Function Calling + MCP/GPT Actions 연동
- [ ] `/api/data/statistics` 추가 지표
- [ ] 프론트 시각화 그래프 1개
- [ ] CSV/JSON 내보내기
- [ ] 다크 모드 토글
