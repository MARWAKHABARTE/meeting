import logging
import uuid
from celery.result import AsyncResult
from app.workers.celery_app import celery_app
from app.workers.tasks.transcription import transcription_task
from app.db.session import SessionLocal
from app.models.transcript import Transcript
from app.models.speaker import Speaker
from app.models.transcript_segment import TranscriptSegment

logger = logging.getLogger("meeting_ai")

class AIService:
    """
    Service d'orchestration IA.
    Responsable uniquement du déclenchement des tâches Celery et de l'interrogation
    du statut et des résultats, sans exécuter de calculs IA locaux.
    """

    def start_transcription(self, meeting_id: str, bucket_name: str, object_name: str) -> str:
        """
        Soumet la tâche de transcription à Celery.
        
        :param meeting_id: Identifiant unique de la réunion.
        :param bucket_name: Nom du bucket MinIO contenant l'audio.
        :param object_name: Clé de l'objet audio MinIO.
        :return: Identifiant unique de la tâche Celery (task_id).
        """
        logger.info(
            f"[AI Service] Lancement asynchrone du pipeline pour la réunion '{meeting_id}' "
            f"(bucket: '{bucket_name}', object: '{object_name}')"
        )
        task = transcription_task.delay(meeting_id, bucket_name, object_name)
        return task.id

    def get_task_status(self, task_id: str) -> str:
        """
        Interroge le broker Celery pour récupérer le statut brut de la tâche.
        
        :param task_id: Identifiant de la tâche Celery.
        :return: Le statut (PENDING, STARTED, SUCCESS, FAILURE, RETRY).
        """
        task_result = AsyncResult(task_id, app=celery_app)
        logger.info(f"[AI Service] Consultation du statut de la tâche '{task_id}' : {task_result.state}")
        return task_result.state

    def get_task_result(self, task_id: str) -> dict | None:
        """
        Récupère le résultat consolidé de la transcription depuis la base PostgreSQL
        une fois la tâche Celery terminée avec succès.
        
        :param task_id: Identifiant de la tâche Celery.
        :return: Dictionnaire contenant le texte complet, les segments et locuteurs, ou None.
        """
        task_result = AsyncResult(task_id, app=celery_app)
        
        if not task_result.ready():
            logger.info(f"[AI Service] La tâche '{task_id}' n'est pas encore terminée.")
            return None

        if task_result.state == "SUCCESS":
            meta = task_result.result
            meeting_id = meta.get("meeting_id")
            if not meeting_id:
                logger.error(f"[AI Service] Impossible de récupérer l'ID de réunion pour la tâche '{task_id}'.")
                return None

            # Recherche des résultats persistés dans PostgreSQL
            db = SessionLocal()
            try:
                db_transcript = db.query(Transcript).filter(
                    Transcript.meeting_id == uuid.UUID(meeting_id)
                ).first()

                if not db_transcript:
                    logger.warning(f"[AI Service] Aucun transcript trouvé en base pour la réunion '{meeting_id}'.")
                    return None

                # Mise en forme des segments
                segments_list = []
                for seg in db_transcript.segments:
                    segments_list.append({
                        "id": str(seg.id),
                        "start_time": seg.start_time,
                        "end_time": seg.end_time,
                        "text": seg.text,
                        "speaker": seg.speaker.name if seg.speaker else "Unknown Speaker"
                    })

                logger.info(
                    f"[AI Service] Résultat complet extrait de la DB pour la réunion '{meeting_id}' "
                    f"({len(segments_list)} segments)."
                )

                return {
                    "full_text": db_transcript.full_text,
                    "language": meta.get("language", "fr"),
                    "duration": meta.get("duration_seconds", 0.0),
                    "segments": segments_list
                }
            finally:
                db.close()
                
        return None
