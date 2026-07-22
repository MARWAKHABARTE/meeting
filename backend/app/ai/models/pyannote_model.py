import threading
import logging
from app.core.settings import settings
from app.ai.exceptions import PyannoteException

logger = logging.getLogger("meeting_ai")

class MockPyannoteModel:
    """
    Modèle de substitution Pyannote (Mock) pour éviter les requêtes Hugging Face et CUDA en dev local.
    """
    def diarize(self, audio_path: str) -> list[dict]:
        """
        Retourne des segments de locuteurs simulés.
        """
        logger.info(f"[Mock Pyannote] Diarisation simulée pour le fichier : {audio_path}")
        return [
            {"speaker": "Speaker 1", "start": 0.0, "end": 2.8, "confidence": 0.98},
            {"speaker": "Speaker 2", "start": 2.8, "end": 8.8, "confidence": 0.95},
            {"speaker": "Speaker 1", "start": 8.8, "end": 15.0, "confidence": 0.97}
        ]


class PyannoteModelProvider:
    """
    Singleton thread-safe gérant le chargement de la pipeline de diarisation Pyannote.
    """
    _instance = None
    _lock = threading.Lock()

    @classmethod
    def get_model(cls):
        """
        Récupère l'instance unique de la pipeline de diarisation (Lazy Loading).
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls._load_model()
        return cls._instance

    @classmethod
    def _load_model(cls):
        logger.info(f"[Pyannote Loader] Initialisation du modèle Pyannote (Model: {settings.PYANNOTE_MODEL})...")
        
        token = settings.pyannote_auth_token_to_use
        
        try:
            # Si pas de token Hugging Face ou si en mode développement / mock
            if settings.ENVIRONMENT == "development" or settings.PYANNOTE_MODEL == "mock" or not token:
                logger.info("[Pyannote Loader] Token manquant ou mode dev actif. Repli sur le Mock Pyannote.")
                return MockPyannoteModel()

            # Importation tardive de la bibliothèque pyannote
            from pyannote.audio import Pipeline
            raw_pipeline = Pipeline.from_pretrained(
                checkpoint_path=settings.PYANNOTE_MODEL,
                use_auth_token=token
            )
            
            if raw_pipeline is None:
                logger.warning("[Pyannote Loader] Hugging Face a retourné une pipeline vide. Repli sur le Mock.")
                return MockPyannoteModel()
                
            logger.info("[Pyannote Loader] Pipeline officielle Pyannote chargée avec succès.")
            return raw_pipeline
        except ImportError:
            logger.warning(
                "[Pyannote Loader] Bibliothèque 'pyannote.audio' indisponible. "
                "Repli sur le Mock Pyannote."
            )
            return MockPyannoteModel()
        except Exception as e:
            logger.error(f"[Pyannote Loader] Échec d'instanciation de Pyannote : {e}")
            raise PyannoteException(f"Impossible d'initialiser le modèle Pyannote : {e}")
