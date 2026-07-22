"""
Package des tâches Celery.
Expose les tâches publiques de chaque domaine fonctionnel.
"""
from app.workers.tasks.health import health_task
from app.workers.tasks.meeting import meeting_task
from app.workers.tasks.transcription import transcription_task
from app.workers.tasks.report import summary_task
from app.workers.tasks.embeddings import embedding_task
from app.workers.tasks.cleanup import cleanup_task

__all__ = [
    "health_task",
    "meeting_task",
    "transcription_task",
    "summary_task",
    "embedding_task",
    "cleanup_task",
]
