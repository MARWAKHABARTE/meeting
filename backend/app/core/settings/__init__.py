import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from .app import AppSettings
from .database import DatabaseSettings
from .redis import RedisSettings
from .minio import MinioSettings
from .keycloak import KeycloakSettings
from .ai import AISettings
from .security import SecuritySettings
from .websocket import WebSocketSettings

# Détermination du chemin vers le fichier .env (racine du projet, 5 dossiers au-dessus)
ENV_FILE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))), 
    ".env"
)

class Settings(
    AppSettings,
    DatabaseSettings,
    RedisSettings,
    MinioSettings,
    KeycloakSettings,
    AISettings,
    SecuritySettings,
    WebSocketSettings,
):
    """
    Classe de configuration fusionnée héritant de chaque domaine.
    """
    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_ignore_empty=True,
        extra="ignore"
    )

# Instance de configuration globale importable
settings = Settings()
