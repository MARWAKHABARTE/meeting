from pydantic_settings import BaseSettings

class MinioSettings(BaseSettings):
    """
    Configuration de la connexion au serveur de stockage MinIO.
    """
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_SECURE: bool = False
    MINIO_BUCKET_NAME: str = "meetings"
    MINIO_BUCKET: str | None = None
    MINIO_REGION: str = "us-east-1"

    @property
    def minio_bucket_to_use(self) -> str:
        """
        Retourne le nom du bucket configuré, avec repli sur MINIO_BUCKET_NAME.
        """
        return self.MINIO_BUCKET or self.MINIO_BUCKET_NAME
