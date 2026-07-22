import threading
import logging
from app.core.settings import settings
from app.ai.exceptions import WhisperException

logger = logging.getLogger("meeting_ai")

class MockWhisperModel:
    """
    Modèle de substitution Whisper (Mock) pour le développement local et les tests.
    Évite de télécharger plusieurs gigaoctets de poids de modèles en local.
    """
    def transcribe(self, audio_path: str) -> dict:
        """
        Simule la transcription d'un fichier audio en retournant un dictionnaire S3/Whisper compatible.
        """
        logger.info(f"[Mock Whisper] Traitement simulé du fichier audio : {audio_path}")
        return {
            "text": "Bonjour à tous. Bienvenue dans la réunion de suivi du projet Meeting AI. Aujourd'hui nous validons le Sprint 8.",
            "language": "fr",
            "segments": [
                {"start": 0.5, "end": 2.2, "text": "Bonjour à tous.", "confidence": 0.99},
                {"start": 3.0, "end": 8.5, "text": "Bienvenue dans la réunion de suivi du projet Meeting AI.", "confidence": 0.96},
                {"start": 9.0, "end": 14.5, "text": "Aujourd'hui nous validons le Sprint 8.", "confidence": 0.94}
            ],
            "duration": 15.0
        }


class WhisperModelProvider:
    """
    Singleton thread-safe assurant le cache mémoire et l'initialisation unique de Whisper.
    """
    _instance = None
    _lock = threading.Lock()

    @classmethod
    def get_model(cls):
        """
        Récupère l'instance unique chargée en mémoire du modèle Whisper (Lazy Loading).
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls._load_model()
        return cls._instance

    @classmethod
    def _load_model(cls):
        logger.info(
            f"[Whisper Loader] Initialisation du modèle Whisper (Model: {settings.WHISPER_MODEL}, "
            f"Device: {settings.WHISPER_DEVICE}, Compute: {settings.WHISPER_COMPUTE_TYPE})"
        )
        try:
            # Force l'utilisation du Mock en développement ou si spécifié
            if settings.ENVIRONMENT == "development" or settings.WHISPER_MODEL == "mock":
                logger.info("[Whisper Loader] Chargement du modèle de substitution (Mock Whisper).")
                return MockWhisperModel()

            # Importation tardive pour ne pas ralentir le démarrage de l'app si non utilisé
            import whisper
            model = whisper.load_model(
                name=settings.WHISPER_MODEL,
                device=settings.WHISPER_DEVICE
            )
            logger.info("[Whisper Loader] Modèle officiel Whisper chargé avec succès.")
            return model
        except ImportError:
            logger.warning(
                "[Whisper Loader] Bibliothèque 'whisper' non disponible dans l'environnement. "
                "Repli automatique sur le Mock Whisper."
            )
            return MockWhisperModel()
        except Exception as e:
            logger.error(f"[Whisper Loader] Erreur critique lors de l'instanciation de Whisper : {e}")
            raise WhisperException(f"Impossible d'initialiser le modèle Whisper : {e}")
