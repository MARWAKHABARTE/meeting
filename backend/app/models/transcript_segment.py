import uuid
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Text, Float, ForeignKey
from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.transcript import Transcript
    from app.models.speaker import Speaker
    from app.models.meeting import Meeting

class TranscriptSegment(Base):
    """
    Segment temporel de transcription, potentiellement associé à un intervenant.
    """
    start_time: Mapped[float] = mapped_column(Float, nullable=False)
    end_time: Mapped[float] = mapped_column(Float, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    
    transcript_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("transcript.id", ondelete="CASCADE"), nullable=False, index=True)
    speaker_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("speaker.id", ondelete="SET NULL"), index=True)
    meeting_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("meeting.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Relations
    transcript: Mapped["Transcript"] = relationship("Transcript", back_populates="segments")
    speaker: Mapped["Speaker"] = relationship("Speaker", back_populates="transcript_segments")
    
    # La relation meeting est unidirectionnelle depuis TranscriptSegment vers Meeting pour 
    # la commodité des requêtes, ou bidirectionnelle si ajoutée sur le modèle Meeting.
    meeting: Mapped["Meeting"] = relationship("Meeting")
