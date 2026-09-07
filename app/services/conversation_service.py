"""`conversations` 컬렉션 CRUD와, 챗봇이 대화 맥락을 읽고 쓰는 헬퍼를 담당한다."""

from datetime import datetime, timezone

from firebase_admin import firestore

from app.firebase import get_db
from app.schemas.conversation import ConversationCreate, ConversationDetail, ConversationListItem, Message

COLLECTION = "conversations"


def _to_iso(value) -> str:
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat()
    return ""


def create_conversation(payload: ConversationCreate) -> ConversationDetail:
    db = get_db()
    doc_ref = db.collection(COLLECTION).document()
    doc_ref.set(
        {
            "title": payload.title or "새 대화",
            "messages": [m.model_dump() for m in payload.messages],
            "created_at": firestore.SERVER_TIMESTAMP,
        }
    )
    snapshot = doc_ref.get()
    data = snapshot.to_dict()
    return ConversationDetail(
        id=doc_ref.id,
        title=data["title"],
        created_at=_to_iso(data.get("created_at")),
        messages=[Message(**m) for m in data.get("messages", [])],
    )


def list_conversations() -> list[ConversationListItem]:
    db = get_db()
    docs = db.collection(COLLECTION).order_by(
        "created_at", direction=firestore.Query.DESCENDING
    ).stream()
    result = []
    for doc in docs:
        data = doc.to_dict()
        result.append(
            ConversationListItem(
                id=doc.id,
                title=data.get("title", "새 대화"),
                created_at=_to_iso(data.get("created_at")),
                message_count=len(data.get("messages", [])),
            )
        )
    return result


def get_conversation(conversation_id: str) -> ConversationDetail:
    db = get_db()
    snapshot = db.collection(COLLECTION).document(conversation_id).get()
    if not snapshot.exists:
        raise KeyError(conversation_id)
    data = snapshot.to_dict()
    return ConversationDetail(
        id=conversation_id,
        title=data.get("title", "새 대화"),
        created_at=_to_iso(data.get("created_at")),
        messages=[Message(**m) for m in data.get("messages", [])],
    )


def delete_conversation(conversation_id: str) -> None:
    db = get_db()
    doc_ref = db.collection(COLLECTION).document(conversation_id)
    if not doc_ref.get().exists:
        raise KeyError(conversation_id)
    doc_ref.delete()


def get_or_create(conversation_id: str | None) -> ConversationDetail:
    """채팅 API용 헬퍼. id가 있으면 기존 대화를, 없으면 새 대화를 반환한다."""
    if conversation_id:
        return get_conversation(conversation_id)
    return create_conversation(ConversationCreate(title=None, messages=[]))


def append_messages(conversation_id: str, new_messages: list[Message]) -> None:
    db = get_db()
    doc_ref = db.collection(COLLECTION).document(conversation_id)
    doc_ref.update(
        {"messages": firestore.ArrayUnion([m.model_dump() for m in new_messages])}
    )
