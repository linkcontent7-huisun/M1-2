from functools import lru_cache

from openai import OpenAI

from app.config import settings


@lru_cache
def get_client() -> OpenAI:
    """OpenAI 클라이언트도 Firestore와 같은 이유로 지연 초기화한다."""
    if not settings.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY 환경 변수가 없습니다.")
    if settings.OPENAI_BASE_URL:
        return OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
    return OpenAI(api_key=settings.OPENAI_API_KEY)
