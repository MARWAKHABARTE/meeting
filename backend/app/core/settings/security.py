from pydantic_settings import BaseSettings
from typing import List
import json
from pydantic import field_validator

class SecuritySettings(BaseSettings):
    """
    Configuration de sécurité (JWT, CORS, etc.).
    """
    JWT_SECRET_KEY: str = "supersecretjwtkeyforlocaldevelopment"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS Origins : supporte les formats CSV ou tableau JSON
    BACKEND_CORS_ORIGINS: str | List[str] = ["http://localhost:3000", "http://localhost:8000"]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, str) and v.startswith("["):
            return json.loads(v)
        return v
