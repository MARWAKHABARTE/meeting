"""
Tâche de diagnostic de santé du worker Celery.
Permet de valider qu'un worker est en ligne et fonctionnel.
"""
import time
import logging
from app.workers.celery_app import celery_app

logger = logging.getLogger("meeting_ai")


@celery_app.task(
    name="workers.health_task",
    bind=True,
    max_retries=3,
    default_retry_delay=5,
)
def health_task(self) -> dict:
    """
    Tâche de santé : vérifie qu'un worker est opérationnel.
    Journalise son exécution et retourne un rapport de statut simple.

    :return: Dictionnaire de résultat contenant le statut et la version.
    """
    logger.info("[health_task] Démarrage de la tâche de diagnostic worker.")

    # Simulation d'un délai de traitement minimal
    time.sleep(0.1)

    result = {
        "status": "ok",
        "task": "health_task",
        "worker": "online",
    }

    logger.info(f"[health_task] Tâche terminée avec succès : {result}")
    return result
