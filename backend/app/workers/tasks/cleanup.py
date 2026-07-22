"""
Tâche Celery dédiée au nettoyage des ressources temporaires.
Supprime les fichiers intermédiaires de MinIO et les données
transitoires de la base de données après le traitement d'une réunion.

Architecture future :
    1. Supprimer les fichiers temporaires de MinIO (ex: audio brut intermédiaire)
    2. Nettoyer les données de cache ou d'état temporaire dans Redis
    3. Archiver ou purger les anciens enregistrements selon la politique de rétention
"""
import time
import logging
from app.workers.celery_app import celery_app

logger = logging.getLogger("meeting_ai")


@celery_app.task(
    name="workers.cleanup_task",
    bind=True,
    max_retries=3,
    default_retry_delay=15,
)
def cleanup_task(
    self,
    meeting_id: str,
    bucket_name: str | None = None,
    object_name: str | None = None,
) -> dict:
    """
    Tâche de nettoyage des ressources temporaires d'une réunion.
    Prépare la politique de rétention et de purge future.

    Étapes futures :
        - Supprimer les fichiers audio temporaires dans MinIO
        - Purger les données de cache Redis associées à la tâche
        - Archiver les résultats selon la politique de rétention configurée

    :param meeting_id: Identifiant unique de la réunion.
    :param bucket_name: Bucket MinIO contenant les fichiers à nettoyer.
    :param object_name: Clé de l'objet à supprimer dans MinIO.
    :return: Dictionnaire de résultat confirmant le nettoyage.
    """
    logger.info(
        f"[cleanup_task] Démarrage du nettoyage pour meeting_id='{meeting_id}'. "
        f"Cible : bucket='{bucket_name}', object='{object_name}'"
    )

    # Simulation de la durée de nettoyage (sera remplacé)
    time.sleep(0.5)

    result = {
        "status": "ok",
        "task": "cleanup_task",
        "meeting_id": meeting_id,
        "bucket_name": bucket_name,
        "object_name": object_name,
        # Futur champ : "files_deleted": [],
        # Futur champ : "cache_keys_purged": 0,
    }

    logger.info(
        f"[cleanup_task] Nettoyage terminé avec succès pour meeting_id='{meeting_id}'."
    )
    return result
