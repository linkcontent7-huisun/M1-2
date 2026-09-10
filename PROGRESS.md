# M1-2 진행 현황 (2026-09-09)

## 현재 상태

| 항목 | 완료도 | 상태 |
|---|---|---|
| 개발 환경 | ✅ 100% | Python 3.13, venv, 패키지 설치 완료 |
| 데이터 선정·분석 | ✅ 100% | 139개 CSV (2015-01~2026-07), 요약 계산 로직 구현 |
| FastAPI 스캐폴딩 | ✅ 100% | 9개 엔드포인트, 라우터/서비스/스키마 분리, Swagger UI 확인 |
| Firestore 설계 | ✅ 100% | 컬렉션(data, conversations) 설계, 스키마 정의 |
| 데이터 적재 스크립트 | ✅ 100% | `scripts/import_foreign_visitors.py` 준비 완료 |
| **Firebase/Firestore 실제 적재** | ❌ 0% | Console에서 API/DB 활성화 + 139건 적재 필요 |
| 데이터 API 실제 테스트 | ❌ 0% | Firestore 적재 후 검증 |
| AI 채팅 API 실제 테스트 | ❌ 0% | OpenAI/Firestore 키로 테스트 필요 |
| **프론트엔드 (HTML/CSS/JS)** | ❌ 0% | 채팅·데이터관리·대화기록 전체 미개발 |
| Render 배포 | ❌ 0% | GitHub 푸시 후 진행 |
| Vercel 배포 | ❌ 0% | 프론트엔드 완성 후 진행 |
| 문서화 (배포 URL, 스크린샷) | ❌ 0% | 배포 후 작성 |
| GitHub 푸시 | ❌ 0% | 준비 중 |

## 실행 가능한 엔드포인트 (로컬 테스트용)

```
POST   /api/data              데이터 추가 (실 Firestore 미연결)
GET    /api/data              데이터 목록 조회
PUT    /api/data/{id}         데이터 수정
DELETE /api/data/{id}         데이터 삭제
GET    /api/data/summary      요약 정보 (하드코딩된 샘플 데이터 반환)

POST   /api/conversations     대화 저장
GET    /api/conversations     대화 목록 조회
DELETE /api/conversations/{id} 대화 삭제
GET    /api/conversations/{id} 특정 대화 불러오기

POST   /api/chat              AI 채팅 (컨텍스트 주입) - OpenAI/Firestore 미연결
```

## 사용자가 준비해야 할 것

- [ ] Firebase Console에서 **Cloud Firestore API** 활성화
- [ ] Firebase Console에서 **Firestore 데이터베이스** 활성화 (시작 모드 또는 프로덕션)
- [ ] `.env` 파일에 `FIREBASE_SERVICE_ACCOUNT_JSON` (서비스 계정 키 경로 또는 JSON 문자열) 입력
- [ ] `.env` 파일에 `OPENAI_API_KEY` 입력
- [ ] `python scripts/import_foreign_visitors.py --dry-run` 으로 검증
- [ ] `python scripts/import_foreign_visitors.py` 로 139건 적재
- [ ] Render 계정 준비 (배포용)
- [ ] Vercel 계정 준비 (배포용)

## 다음 단계

### 1. 로컬 변경사항 커밋 (즉시)
```bash
cd "C:\Users\noh hui sun\codyssey\assignments\M1-2"
git add -A
git commit -m "feat: 데이터 적재 스크립트 추가, README 업데이트"
```

### 2. 프론트엔드 개발 (3-4시간)
- `public/index.html` + `public/css/style.css` + `public/js/app.js` 작성
- 채팅 인터페이스 (입력 폼, 메시지 표시, 로딩 표시)
- 데이터 관리 화면 (추가·목록 최소)
- 대화 기록 화면 (목록·불러오기)
- 데이터 요약 표시 섹션

### 3. Render 배포 (0.5시간)
- GitHub에 푸시
- Render에서 Web Service 생성
- 환경변수 설정
- 배포 URL 확인

### 4. Vercel 배포 (0.5시간)
- `public/` 또는 `frontend/` 폴더를 별도 저장소 또는 Vercel 설정으로 배포
- 환경 변수 `VITE_API_URL` 또는 `REACT_APP_API_URL` 설정
- 배포 URL 확인

### 5. 문서 최종화 (0.5시간)
- README에 배포 URL 작성
- 제출 스크린샷 3장 추가 (채팅+요약, 데이터 관리, 대화 기록)

### 6. 최종 푸시
```bash
git add -A
git commit -m "feat: 프론트엔드 + 배포 완료"
git push origin main
```

## 참고
- 로컬에서 `uvicorn main:app --reload` 로 FastAPI 테스트 가능 (http://localhost:8000/docs)
- Firebase 키가 없어도 서버는 뜨지만, API 호출 시 `503` 에러로 어떤 환경변수가 빠졌는지 알려줌
- 개발 중 OpenAI 과금 주의 — `max_tokens` 제한 필수
