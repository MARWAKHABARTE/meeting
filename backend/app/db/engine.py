from sqlalchemy import create_engine
from ..core.settings import settings

# Création du moteur SQLAlchemy connecté à PostgreSQL
# pool_pre_ping=True vérifie la santé de la connexion avant chaque requête
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)
