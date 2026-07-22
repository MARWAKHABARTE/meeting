import uuid
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Text, ForeignKey
from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.meeting import Meeting

class Decision(Base):
    """
    Décision extraite d'une réunion.
    """
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    meeting_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("meeting.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Relations
    meeting: Mapped["Meeting"] = relationship("Meeting", back_populates="decisions")
