import uuid
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Text, Boolean, ForeignKey
from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.user import User

class Notification(Base):
    """
    Notification adressée à un utilisateur.
    """
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Relations unidirectionnelle
    user: Mapped["User"] = relationship("User")
