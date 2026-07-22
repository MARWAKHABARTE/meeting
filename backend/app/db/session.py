from typing import Generator
from sqlalchemy.orm import sessionmaker, Session
from .engine import engine

# Factory de sessions pour créer des sessions individuelles
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db() -> Generator[Session, None, None]:
    """
    Dépendance FastAPI pour injecter la session de base de données.
    Assure la libération propre des ressources à la fin du traitement.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
