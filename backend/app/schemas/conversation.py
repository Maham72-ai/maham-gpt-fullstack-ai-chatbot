from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class CreateConversationRequest(BaseModel):
    title: Optional[str] = Field(default="New Chat", max_length=200)

class RenameConversationRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)

class ConversationResponse(BaseModel):
    id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    last_message_at: datetime

class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    created_at: datetime

class ConversationWithMessagesResponse(BaseModel):
    conversation: ConversationResponse
    messages: List[MessageResponse]

class SendMessageRequest(BaseModel):
    content: str = Field(min_length=1, max_length=10000)

class SendMessageResponse(BaseModel):
    user_message: MessageResponse
    assistant_message: MessageResponse
    retrieved_context: Optional[List[dict]] = None
