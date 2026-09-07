import json
import os
from functools import lru_cache

import firebase_admin
from firebase_admin import credentials, firestore

from app.config import settings


@lru_cache
def get_db():
    """Firestore 클라이언트를 최초 호출 시 한 번만 초기화해 재사용한다.

    앱을 import하는 시점(main.py 로드, /docs 접근)에는 Firebase 자격 증명이
    없어도 되고, 실제로 데이터를 읽고 쓰는 요청이 들어올 때만 초기화한다 —
    그래야 키를 아직 안 넣은 상태에서도 Swagger UI 확인 같은 로컬 개발이 가능하다.
    """
    raw = settings.FIREBASE_SERVICE_ACCOUNT_JSON
    if not raw:
        raise RuntimeError(
            "FIREBASE_SERVICE_ACCOUNT_JSON 환경 변수가 없습니다. "
            ".env에 서비스 계정 키(JSON 문자열 또는 파일 경로)를 설정하세요."
        )

    if not firebase_admin._apps:
        if os.path.isfile(raw):
            cred = credentials.Certificate(raw)
        else:
            cred = credentials.Certificate(json.loads(raw))
        firebase_admin.initialize_app(cred)

    return firestore.client()
