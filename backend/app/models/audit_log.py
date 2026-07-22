import uuid
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, JSON, ForeignKey
from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.user import User

class AuditLog(Base):
    """
    Journalisation des actions des utilisateurs.
    """
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(255), nullable=False)
    resource_id: Mapped[str] = mapped_column(String(255), nullable=False)
    details: Mapped[dict | None] = mapped_column(JSON)
    
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("user.id", ondelete="SET NULL"), index=True)
    
    # Relations unidirectionnelle
    user: Mapped["User | None"] = relationship("User")
