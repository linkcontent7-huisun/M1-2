from fastapi import APIRouter, HTTPException

from app.schemas.conversation import ConversationCreate, ConversationDetail, ConversationListItem
from app.services import conversation_service

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


@router.post("", response_model=ConversationDetail)
def create_conversation(payload: ConversationCreate):
    return conversation_service.create_conversation(payload)


@router.get("", response_model=list[ConversationListItem])
def list_conversations():
    return conversation_service.list_conversations()


@router.get("/{conversation_id}", response_model=ConversationDetail)
def get_conversation(conversation_id: str):
    try:
        return conversation_service.get_conversation(conversation_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="대화를 찾을 수 없습니다.")


@router.delete("/{conversation_id}", status_code=204)
def delete_conversation(conversation_id: str):
    try:
        conversation_service.delete_conversation(conversation_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="대화를 찾을 수 없습니다.")
