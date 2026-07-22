"""
Tâche Celery liée au traitement des réunions.
Prépare les paramètres pour les futures étapes de traitement IA
(transcription, diarisation, analyse NLP, etc.).
"""
import time
import logging
from app.workers.celery_app import celery_app

logger = logging.getLogger("meeting_ai")


@celery_app.task(
    name="workers.meeting_task",
    bind=True,
    max_retries=3,
    default_retry_delay=10,
)
def meeting_task(
    self,
    meeting_id: str,
    bucket_name: str | None = None,
    object_name: str | None = None,
) -> dict:
    """
    Tâche de traitement d'une réunion.
    Aucune logique métier n'est implémentée ici.
    Prépare l'infrastructure pour les étapes IA futures.

    :param meeting_id: Identifiant unique de la réunion à traiter.
    :param bucket_name: Nom du bucket MinIO contenant le fichier audio (futur usage).
    :param object_name: Clé de l'objet audio dans MinIO (futur usage).
    :return: Dictionnaire de résultat contenant l'ID de la réunion et le statut.
    """
    logger.info(
        f"[meeting_task] Démarrage pour meeting_id='{meeting_id}', "
        f"bucket='{bucket_name}', object='{object_name}'"
    )

    # Simulation du temps de traitement (sera remplacé par les appels IA)
    time.sleep(1)

    result = {
        "status": "ok",
        "task": "meeting_task",
        "meeting_id": meeting_id,
        "bucket_name": bucket_name,
        "object_name": object_name,
    }

    logger.info(f"[meeting_task] Tâche terminée avec succès pour meeting_id='{meeting_id}'.")
    return result
