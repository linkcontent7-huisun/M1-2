from typing import Literal

from pydantic import BaseModel


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ConversationCreate(BaseModel):
    title: str | None = None
    messages: list[Message] = []


class ConversationListItem(BaseModel):
    id: str
    title: str
    created_at: str
    message_count: int


class ConversationDetail(BaseModel):
    id: str
    title: str
    created_at: str
    messages: list[Message]
