import uuid
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Float, ForeignKey
from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.meeting import Meeting

class SentimentAnalysis(Base):
    """
    Analyse de sentiment pour une partie ou la globalité de la réunion.
    """
    sentiment_score: Mapped[float] = mapped_column(Float, nullable=False)
    label: Mapped[str] = mapped_column(String(50), nullable=False)
    
    meeting_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("meeting.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Relations
    meeting: Mapped["Meeting"] = relationship("Meeting", back_populates="sentiment_analyses")
