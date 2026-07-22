import uuid
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, ForeignKey
from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.meeting import Meeting
    from app.models.transcript_segment import TranscriptSegment

class Speaker(Base):
    """
    Intervenant détecté ou assigné dans une réunion.
    """
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    voice_signature: Mapped[str | None] = mapped_column(Text)
    
    meeting_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("meeting.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Relations
    meeting: Mapped["Meeting"] = relationship("Meeting", back_populates="speakers")
    transcript_segments: Mapped[list["TranscriptSegment"]] = relationship("TranscriptSegment", back_populates="speaker", cascade="all, delete-orphan")
