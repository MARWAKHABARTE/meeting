import logging
from app.ai.schemas.transcription import TranscriptionResult, MergedSegment, PipelineResult
from app.ai.schemas.speaker import DiarizationResult
from app.ai.exceptions import PipelineException

logger = logging.getLogger("meeting_ai")

class MergePipeline:
    """
    Pipeline fusionnant les sorties temporelles de Whisper (textes)
    et de Pyannote (locuteurs) en se basant sur le taux de recouvrement temporel.
    """

    def run(self, transcription: TranscriptionResult, diarization: DiarizationResult) -> PipelineResult:
        """
        Fusionne la transcription brute et les segments locuteurs.
        
        :param transcription: Résultat de la transcription Whisper.
        :param diarization: Résultat de la diarisation Pyannote.
        :return: PipelineResult contenant la liste consolidée des segments enrichis.
        :raises PipelineException: En cas d'erreur de fusion.
        """
        logger.info("[Merge Pipeline] Début de la fusion des résultats de transcription et de diarisation...")
        try:
            merged_segments = []

            # Algorithme d'alignement temporel par recouvrement maximum
            for w_seg in transcription.segments:
                w_start = w_seg.start
                w_end = w_seg.end
                
                # Dictionnaire pour sommer la durée de parole chevauchante par locuteur
                overlap_durations = {}

                for p_seg in diarization.segments:
                    # Calcul du recouvrement entre le segment Whisper et le segment Pyannote
                    overlap_start = max(w_start, p_seg.start)
                    overlap_end = min(w_end, p_seg.end)
                    overlap_duration = max(0.0, overlap_end - overlap_start)

                    if overlap_duration > 0:
                        overlap_durations[p_seg.speaker] = (
                            overlap_durations.get(p_seg.speaker, 0.0) + overlap_duration
                        )

                # Si aucun chevauchement n'est détecté, on attribue un locuteur par défaut
                if overlap_durations:
                    assigned_speaker = max(overlap_durations, key=overlap_durations.get)
                else:
                    assigned_speaker = "Unknown Speaker"

                merged_segments.append(MergedSegment(
                    speaker=assigned_speaker,
                    start=w_start,
                    end=w_end,
                    text=w_seg.text,
                    confidence=w_seg.confidence
                ))

            # Consolidation finale du résultat
            result = PipelineResult(
                full_text=transcription.text,
                language=transcription.language,
                duration=transcription.duration,
                segments=merged_segments
            )

            logger.info(
                f"[Merge Pipeline] Fusion terminée avec succès. "
                f"Nombre de segments fusionnés : {len(merged_segments)}"
            )
            return result

        except Exception as e:
            logger.error(f"[Merge Pipeline] Échec lors de la fusion temporelle : {e}")
            raise PipelineException(f"Impossible de fusionner les timelines IA : {str(e)}")
