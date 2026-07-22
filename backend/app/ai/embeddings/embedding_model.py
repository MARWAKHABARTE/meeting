"""
Singleton thread-safe du modèle d'embeddings sentence-transformers.
"""
import threading
import logging
from app.core.settings import settings
from app.ai.exceptions import EmbeddingException

logger = logging.getLogger("meeting_ai")


class EmbeddingModelProvider:
    """
    Singleton thread-safe gérant le chargement et le cache du modèle sentence-transformers.
    Le modèle n'est instancié qu'une seule fois (Lazy Loading) et conservé en mémoire.
    """
    _instance = None
    _lock = threading.Lock()

    @classmethod
    def get_model(cls):
        """
        Retourne l'instance unique du modèle sentence-transformers.
        Le modèle est chargé à la première demande (Lazy Loading).
        :raises EmbeddingException: En cas d'erreur de chargement.
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls._load_model()
        return cls._instance

    @classmethod
    def _load_model(cls):
        logger.info(
            f"[EmbeddingModelProvider] Chargement du modèle : '{settings.EMBEDDING_MODEL}'..."
        )
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer(settings.EMBEDDING_MODEL)
            logger.info("[EmbeddingModelProvider] Modèle d'embeddings chargé avec succès.")
            return model
        except Exception as e:
            logger.error(f"[EmbeddingModelProvider] Échec du chargement : {e}")
            raise EmbeddingException(f"Impossible de charger le modèle d'embeddings : {e}")

    @classmethod
    def encode(cls, texts: list[str]) -> list[list[float]]:
        """
        Encode une liste de textes en vecteurs d'embeddings.
        :param texts: Liste de chaînes à encoder.
        :return: Liste de vecteurs de dimension fixe.
        :raises EmbeddingException: En cas d'erreur d'encodage.
        """
        try:
            model = cls.get_model()
            vectors = model.encode(texts, convert_to_numpy=True)
            return vectors.tolist()
        except EmbeddingException:
            raise
        except Exception as e:
            logger.error(f"[EmbeddingModelProvider] Erreur d'encodage : {e}")
            raise EmbeddingException(f"Erreur lors de la vectorisation : {e}")
