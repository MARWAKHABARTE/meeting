import uuid
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey
from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.meeting import Meeting

class MeetingFile(Base):
    """
    Fichier (vidéo, audio, etc.) associé à une réunion pour analyse.
    """
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[int | None] = mapped_column(Integer)
    
    meeting_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("meeting.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Relations
    meeting: Mapped["Meeting"] = relationship("Meeting", back_populates="files")
