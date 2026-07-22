from pydantic_settings import BaseSettings

class DatabaseSettings(BaseSettings):
    """
    Configuration de la base de données PostgreSQL.
    """
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "securepassword"
    POSTGRES_DB: str = "meeting_ai"

    @property
    def database_url(self) -> str:
        """
        Génère l'URL de connexion SQLAlchemy.
        """
        return f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
