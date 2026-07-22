import uuid
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey
from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.meeting import Meeting
    from app.models.chat_message import ChatMessage

class ChatConversation(Base):
    """
    Session de chat associée à une réunion.
    """
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    
    meeting_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("meeting.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Relations
    meeting: Mapped["Meeting"] = relationship("Meeting", back_populates="chat_conversations")
    messages: Mapped[list["ChatMessage"]] = relationship("ChatMessage", back_populates="conversation", cascade="all, delete-orphan")
