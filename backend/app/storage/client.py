import threading
from minio import Minio
from app.core.settings import settings
from app.core.logger import logger
from app.storage.exceptions import StorageException

class MinioClientProvider:
    """
    Fournisseur de client MinIO implémentant le pattern Singleton.
    Garantit une instance de connexion unique et thread-safe.
    Initialisation différée (lazy-loading) pour éviter des blocages au démarrage.
    """
    _instance: Minio | None = None
    _lock = threading.Lock()

    @classmethod
    def get_client(cls) -> Minio:
        """
        Retourne l'instance unique du client MinIO.
        Initialise la connexion de manière thread-safe si elle n'existe pas déjà.
        
        :raises StorageException: En cas de mauvaise configuration ou d'échec de création du client
        :return: L'instance Minio configurée
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    try:
                        logger.info(
                            f"Initialisation du client unique MinIO sur l'endpoint : {settings.MINIO_ENDPOINT} "
                            f"(Secure: {settings.MINIO_SECURE}, Region: {settings.MINIO_REGION})"
                        )
                        cls._instance = Minio(
                            endpoint=settings.MINIO_ENDPOINT,
                            access_key=settings.MINIO_ACCESS_KEY,
                            secret_key=settings.MINIO_SECRET_KEY,
                            secure=settings.MINIO_SECURE,
                            region=settings.MINIO_REGION
                        )
                        logger.info("Le client unique MinIO a été initialisé avec succès.")
                    except Exception as e:
                        logger.error(f"Échec de configuration du client MinIO : {e}")
                        raise StorageException(f"Erreur de configuration du client de stockage MinIO : {e}")
        return cls._instance
