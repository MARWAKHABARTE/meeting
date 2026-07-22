import uuid
import re
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr
from .metadata import metadata

class Base(DeclarativeBase):
    """
    Classe de base déclarative pour tous les modèles de l'application.
    Configure automatiquement le nom des tables et injecte les colonnes de base.
    """
    metadata = metadata

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """
        Génère automatiquement le nom de la table au format snake_case.
        Ex: MeetingSpeaker -> meeting_speaker
        """
        name = cls.__name__
        return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()

    # Identifiant unique UUID
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )

    # Horodatage de création
    created_at: Mapped[datetime] = mapped_column(
        default=func.now()
    )

    # Horodatage de dernière mise à jour
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(),
        onupdate=func.now()
    )
