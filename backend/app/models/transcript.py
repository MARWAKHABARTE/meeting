import uuid
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Text, ForeignKey
from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.meeting import Meeting
    from app.models.transcript_segment import TranscriptSegment

class Transcript(Base):
    """
    Transcription globale d'une réunion.
    """
    full_text: Mapped[str | None] = mapped_column(Text)
    
    meeting_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("meeting.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    # Relations
    meeting: Mapped["Meeting"] = relationship("Meeting", back_populates="transcript")
    segments: Mapped[list["TranscriptSegment"]] = relationship("TranscriptSegment", back_populates="transcript", cascade="all, delete-orphan")
