import uuid
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean
from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.workspace import Workspace

class User(Base):
    """
    Modèle utilisateur pour la plateforme.
    Un utilisateur peut gérer plusieurs espaces de travail (Workspace).
    """
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relations
    workspaces: Mapped[list["Workspace"]] = relationship(
        "Workspace",
        back_populates="user"
    )
