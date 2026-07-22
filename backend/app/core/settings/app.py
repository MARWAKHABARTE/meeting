from pydantic_settings import BaseSettings
from typing import Literal

class AppSettings(BaseSettings):
    """
    Configuration générale de l'application.
    """
    PROJECT_NAME: str = "Meeting AI Platform"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
