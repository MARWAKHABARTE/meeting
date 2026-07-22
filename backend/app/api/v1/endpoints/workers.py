"""
Endpoints FastAPI de gestion et de diagnostic de l'infrastructure Celery.

Endpoints exposés :
    GET  /api/v1/workers/health        → Vérifie la connexion au broker et la présence de workers
    POST /api/v1/workers/test          → Soumet une tâche de démonstration et retourne l'ID de tâche
    GET  /api/v1/workers/tasks/{id}    → Consulte l'état d'avancement d'une tâche Celery
"""
import logging
from fastapi import APIRouter, HTTPException, status
from celery.result import AsyncResult
from app.workers.celery_app import celery_app
from app.workers.tasks.health import health_task

logger = logging.getLogger("meeting_ai")
router = APIRouter()


@router.get("/health", response_model=dict)
def workers_health():
    """
    Vérifie l'état de santé de l'infrastructure Celery.
    - Vérifie la connexion au broker Redis via ping
    - Détecte la présence d'au moins un worker actif

    :return: {"worker": "online"|"offline", "broker": "connected"|"unreachable"}
    """
    broker_status = "unreachable"
    worker_status = "offline"

    try:
        # Ping direct du broker Redis via l'inspecteur Celery
        inspector = celery_app.control.inspect(timeout=2.0)
        active_workers = inspector.active()

        broker_status = "connected"
        worker_status = "online" if active_workers else "offline"

        logger.info(
            f"[workers/health] Statut — broker: {broker_status}, workers: {worker_status}"
        )
    except Exception as e:
        logger.error(f"[workers/health] Échec du diagnostic de l'infrastructure Celery : {e}")

    return {
        "worker": worker_status,
        "broker": broker_status,
    }


@router.post("/test", response_model=dict, status_code=status.HTTP_202_ACCEPTED)
def submit_test_task():
    """
    Soumet une tâche Celery de démonstration dans la file d'attente Redis.
    Ne bloque pas en attendant le résultat. Retourne immédiatement l'ID de tâche.

    :return: {"task_id": "...", "status": "queued"}
    """
    try:
        task = health_task.delay()
        logger.info(f"[workers/test] Tâche de démonstration soumise avec l'ID : {task.id}")
        return {
            "task_id": task.id,
            "status": "queued",
        }
    except Exception as e:
        logger.error(f"[workers/test] Échec de la soumission de la tâche de démonstration : {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Impossible de soumettre la tâche au broker Celery : {str(e)}"
        )


@router.get("/tasks/{task_id}", response_model=dict)
def get_task_status(task_id: str):
    """
    Retourne l'état d'avancement et le résultat d'une tâche Celery par son ID.

    États possibles :
        - PENDING  → La tâche est en attente d'un worker.
        - STARTED  → Un worker a pris en charge la tâche.
        - SUCCESS  → La tâche s'est terminée avec succès.
        - FAILURE  → La tâche a échoué.
        - RETRY    → La tâche est en cours de réessai.

    :param task_id: Identifiant unique de la tâche Celery.
    :return: Dictionnaire contenant l'état et le résultat éventuel.
    """
    try:
        task_result = AsyncResult(task_id, app=celery_app)
        response = {
            "task_id": task_id,
            "status": task_result.state,
        }

        if task_result.state == "SUCCESS":
            response["result"] = task_result.result
        elif task_result.state == "FAILURE":
            response["error"] = str(task_result.result)
        elif task_result.state == "RETRY":
            response["info"] = str(task_result.info)

        logger.info(f"[workers/tasks/{task_id}] Statut consulté : {task_result.state}")
        return response

    except Exception as e:
        logger.error(f"[workers/tasks/{task_id}] Erreur lors de la consultation de la tâche : {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Impossible de récupérer le statut de la tâche '{task_id}' : {str(e)}"
        )
