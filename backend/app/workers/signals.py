import logging
from celery.signals import task_prerun, task_postrun, task_failure
from app.services.websocket_service import WebSocketService
from app.websocket.events import WSEventType

logger = logging.getLogger("meeting_ai")

# Mapping des tâches Celery vers les types d'événements WS associés
TASK_EVENT_MAPPING = {
    "workers.transcription_task": {
        "start": WSEventType.TRANSCRIPTION_STARTED,
        "complete": WSEventType.TRANSCRIPTION_COMPLETED,
        "step_name": "Transcription & Diarisation"
    },
    "workers.summary_task": {
        "start": WSEventType.SUMMARY_STARTED,
        "complete": WSEventType.SUMMARY_COMPLETED,
        "step_name": "Résumé NLP"
    },
    "workers.embedding_task": {
        "start": WSEventType.EMBEDDING_STARTED,
        "complete": WSEventType.EMBEDDING_COMPLETED,
        "step_name": "Indexation Vectorielle"
    }
}


@task_prerun.connect
def on_task_prerun(sender=None, task_id=None, task=None, args=None, kwargs=None, **extra):
    """Signal interceptant le début d'une tâche pour notifier le frontend."""
    if not sender or not args:
        return

    task_name = sender.name
    if task_name in TASK_EVENT_MAPPING:
        mapping = TASK_EVENT_MAPPING[task_name]
        meeting_id = args[0]  # Par convention, le meeting_id est toujours le premier argument

        logger.info(f"[Celery Signal] Début de la tâche '{task_name}' pour le meeting '{meeting_id}'.")
        WebSocketService.publish_meeting_progress(
            meeting_id=meeting_id,
            event_type=mapping["start"],
            step=mapping["step_name"],
            percent=0,
            status="running",
            details=f"Début de l'étape : {mapping['step_name']}"
        )


@task_postrun.connect
def on_task_postrun(sender=None, task_id=None, task=None, args=None, kwargs=None, retval=None, state=None, **extra):
    """Signal interceptant la fin d'une tâche pour notifier le frontend."""
    if not sender or not args:
        return

    task_name = sender.name
    if task_name in TASK_EVENT_MAPPING:
        mapping = TASK_EVENT_MAPPING[task_name]
        meeting_id = args[0]

        if state == "SUCCESS":
            logger.info(f"[Celery Signal] Fin réussie de la tâche '{task_name}' pour le meeting '{meeting_id}'.")
            WebSocketService.publish_meeting_progress(
                meeting_id=meeting_id,
                event_type=mapping["complete"],
                step=mapping["step_name"],
                percent=100,
                status="completed",
                details=f"Étape terminée avec succès : {mapping['step_name']}"
            )

            # Si c'est la tâche finale d'indexation vectorielle ou de résumé, on peut mettre à jour la réunion
            WebSocketService.publish_meeting_progress(
                meeting_id=meeting_id,
                event_type=WSEventType.MEETING_UPDATED,
                step=mapping["step_name"],
                percent=100,
                status="completed",
                details="Le statut de la réunion a changé."
            )


@task_failure.connect
def on_task_failure(sender=None, task_id=None, exception=None, args=None, kwargs=None, traceback=None, **extra):
    """Signal interceptant l'échec d'une tâche pour notifier le frontend d'une erreur."""
    if not sender or not args:
        return

    task_name = sender.name
    if task_name in TASK_EVENT_MAPPING:
        mapping = TASK_EVENT_MAPPING[task_name]
        meeting_id = args[0]

        logger.error(f"[Celery Signal] Échec de la tâche '{task_name}' pour le meeting '{meeting_id}' : {exception}")
        WebSocketService.publish_meeting_progress(
            meeting_id=meeting_id,
            event_type=WSEventType.ERROR,
            step=mapping["step_name"],
            percent=0,
            status="failed",
            details=f"Erreur lors de l'étape '{mapping['step_name']}' : {str(exception)}"
        )
