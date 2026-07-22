import uuid
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey
from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.meeting import Meeting

class Embedding(Base):
    """
    Référence à un vecteur stocké dans une base de données vectorielle (RAG).
    """
    vector_id: Mapped[str] = mapped_column(String(255), nullable=False)
    content_ref: Mapped[str] = mapped_column(String(500), nullable=False)
    
    meeting_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("meeting.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Relations
    meeting: Mapped["Meeting"] = relationship("Meeting", back_populates="embeddings")
