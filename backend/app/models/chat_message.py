import uuid
from enum import Enum as PyEnum
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Text, Enum, ForeignKey
from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.chat_conversation import ChatConversation

class MessageRole(str, PyEnum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ChatMessage(Base):
    """
    Message individuel au sein d'une conversation Chat.
    """
    role: Mapped[MessageRole] = mapped_column(Enum(MessageRole), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    conversation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("chat_conversation.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Relations
    conversation: Mapped["ChatConversation"] = relationship("ChatConversation", back_populates="messages")
