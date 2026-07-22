import time
import logging
from app.ai.models.pyannote_model import PyannoteModelProvider
from app.ai.schemas.speaker import DiarizationResult, SpeakerSegment
from app.ai.exceptions import PyannoteException

logger = logging.getLogger("meeting_ai")

class DiarizationPipeline:
    """
    Pipeline orchestrant la diarisation (segmentation vocale) avec Pyannote.
    """

    def __init__(self):
        self._model_provider = PyannoteModelProvider

    def run(self, audio_path: str) -> DiarizationResult:
        """
        Exécute l'analyse acoustique pour identifier les locuteurs et leurs plages de parole.
        
        :param audio_path: Chemin d'accès local absolu vers le fichier audio.
        :return: Objet DiarizationResult validé.
        :raises PyannoteException: En cas de problème d'exécution ou de token Hugging Face.
        """
        logger.info(f"[Diarization Pipeline] Lancement de la diarisation pour le fichier : {audio_path}")
        start_time = time.time()

        try:
            # Chargement de la pipeline via le Singleton provider
            model = self._model_provider.get_model()

            # Rapatriement et formatage uniforme des segments
            from app.ai.models.pyannote_model import MockPyannoteModel
            if isinstance(model, MockPyannoteModel):
                raw_segments = model.diarize(audio_path)
            else:
                # Exécution sur la pipeline officielle Pyannote
                annotation = model(audio_path)
                raw_segments = []
                for turn, _, speaker in annotation.itertracks(properties=True):
                    raw_segments.append({
                        "speaker": str(speaker),
                        "start": float(turn.start),
                        "end": float(turn.end),
                        "confidence": 1.0
                    })

            # Instanciation des schémas Pydantic
            segments = []
            for seg in raw_segments:
                start = float(seg.get("start"))
                end = float(seg.get("end"))
                duration = max(0.0, end - start)
                segments.append(SpeakerSegment(
                    speaker=seg.get("speaker"),
                    start=start,
                    end=end,
                    duration=duration,
                    confidence=seg.get("confidence")
                ))

            result = DiarizationResult(segments=segments)
            logger.info(
                f"[Diarization Pipeline] Diarisation complétée en {time.time() - start_time:.2f}s. "
                f"Nombre de segments détectés : {len(segments)}"
            )
            return result

        except Exception as e:
            logger.error(f"[Diarization Pipeline] Échec de la diarisation Pyannote : {e}")
            raise PyannoteException(str(e))
