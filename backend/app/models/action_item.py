import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, ForeignKey, Enum, DateTime
from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.meeting import Meeting

class ActionItemStatus(str, PyEnum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

class ActionItem(Base):
    """
    Tâche ou point d'action extrait de la réunion.
    """
    description: Mapped[str] = mapped_column(Text, nullable=False)
    assignee: Mapped[str | None] = mapped_column(String(255))
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[ActionItemStatus] = mapped_column(Enum(ActionItemStatus), default=ActionItemStatus.TODO)
    
    meeting_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("meeting.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Relations
    meeting: Mapped["Meeting"] = relationship("Meeting", back_populates="action_items")
