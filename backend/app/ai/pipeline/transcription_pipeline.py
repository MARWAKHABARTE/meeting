import time
import logging
from app.ai.models.whisper_model import WhisperModelProvider
from app.ai.schemas.transcription import TranscriptionResult, TranscriptionSegment
from app.ai.exceptions import WhisperException

logger = logging.getLogger("meeting_ai")

class TranscriptionPipeline:
    """
    Pipeline orchestrant le processus de transcription avec le modèle Whisper.
    """

    def __init__(self):
        self._model_provider = WhisperModelProvider

    def run(self, audio_path: str) -> TranscriptionResult:
        """
        Lance la transcription du fichier audio spécifié.
        
        :param audio_path: Chemin d'accès local absolu vers le fichier audio.
        :return: Objet TranscriptionResult validé par Pydantic.
        :raises WhisperException: En cas de panne ou d'exception du décodeur.
        """
        logger.info(f"[Transcription Pipeline] Lancement de la transcription pour le fichier : {audio_path}")
        start_time = time.time()

        try:
            # Récupération lazy-loaded du singleton
            model = self._model_provider.get_model()
            
            # Lancement de la transcription
            raw_result = model.transcribe(audio_path)

            # Traitement et mise en forme des segments
            segments = []
            for seg in raw_result.get("segments", []):
                segments.append(TranscriptionSegment(
                    start=float(seg.get("start")),
                    end=float(seg.get("end")),
                    text=seg.get("text", "").strip(),
                    confidence=seg.get("confidence")
                ))

            # Extraction des métadonnées
            full_text = raw_result.get("text", "").strip()
            detected_language = raw_result.get("language", "fr")
            audio_duration = float(raw_result.get("duration", 0.0))

            # Calcul de la confiance moyenne
            valid_confidences = [s.confidence for s in segments if s.confidence is not None]
            mean_confidence = sum(valid_confidences) / len(valid_confidences) if valid_confidences else 1.0

            result = TranscriptionResult(
                text=full_text,
                language=detected_language,
                duration=audio_duration,
                segments=segments,
                confidence=mean_confidence
            )

            logger.info(
                f"[Transcription Pipeline] Transcription complétée en {time.time() - start_time:.2f}s. "
                f"Langue: '{detected_language}', Durée: {audio_duration}s, Confiance moyenne: {mean_confidence:.2%}"
            )
            return result

        except Exception as e:
            logger.error(f"[Transcription Pipeline] Échec du traitement Whisper : {e}")
            raise WhisperException(str(e))
