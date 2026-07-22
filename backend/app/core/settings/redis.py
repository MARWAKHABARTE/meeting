from pydantic_settings import BaseSettings

class RedisSettings(BaseSettings):
    """
    Configuration de la connexion Redis (utilisée pour Celery et le cache).
    """
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str | None = None

    # Variables spécifiques à Celery
    CELERY_BROKER_URL: str | None = None
    CELERY_RESULT_BACKEND: str | None = None
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_RESULT_SERIALIZER: str = "json"
    CELERY_ACCEPT_CONTENT: list[str] = ["json"]
    CELERY_TIMEZONE: str = "UTC"
    CELERY_ENABLE_UTC: bool = True

    @property
    def redis_url(self) -> str:
        """
        Génère l'URL de connexion Redis.
        """
        password_part = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{password_part}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @property
    def celery_broker_url_to_use(self) -> str:
        """
        Retourne l'URL du broker Celery, avec repli sur redis_url.
        """
        return self.CELERY_BROKER_URL or self.redis_url

    @property
    def celery_result_backend_to_use(self) -> str:
        """
        Retourne l'URL du backend de résultat Celery, avec repli sur redis_url.
        """
        return self.CELERY_RESULT_BACKEND or self.redis_url
