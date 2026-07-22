"""
Module d'initialisation du package workers.
Expose l'application Celery pour utilisation dans les tâches et l'API.
"""
from app.workers.celery_app import celery_app

__all__ = ["celery_app"]
