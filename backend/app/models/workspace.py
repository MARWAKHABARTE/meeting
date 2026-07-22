import uuid
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, ForeignKey
from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.meeting import Meeting

class Workspace(Base):
    """
    Espace de travail regroupant plusieurs réunions.
    """
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    
    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"), nullable=False, index=True)
    
    # Relations
    user: Mapped["User"] = relationship("User", back_populates="workspaces")
    
    meetings: Mapped[list["Meeting"]] = relationship(
        "Meeting",
        back_populates="workspace"
    )
