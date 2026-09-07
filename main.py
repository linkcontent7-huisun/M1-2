from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.routers import chat, conversations, data

app = FastAPI(
    title="M1-2 AI 비서",
    description="국내 성지 소재 지역 방문자 수 시계열을 기반으로 대화하는 AI 데이터 비서",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS or ["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(data.router)
app.include_router(conversations.router)
app.include_router(chat.router)


@app.exception_handler(RuntimeError)
def handle_missing_credentials(request: Request, exc: RuntimeError):
    """OPENAI_API_KEY / FIREBASE_SERVICE_ACCOUNT_JSON이 없을 때
    get_db()/get_client()가 던지는 RuntimeError를 503으로 통일해 응답한다."""
    return JSONResponse(status_code=503, content={"detail": str(exc)})


@app.get("/")
def health_check():
    return {"status": "ok"}
