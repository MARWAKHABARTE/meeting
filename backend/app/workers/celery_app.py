"""
Point d'entrée principal de l'application Celery.
Configure le broker, le backend de résultat, la sérialisation,
le fuseau horaire et l'autodécouverte des tâches.

Utilisation :
    celery -A app.workers.celery_app worker --loglevel=info
"""
import logging
from celery import Celery
from celery.signals import after_setup_logger, after_setup_task_logger
from app.core.settings import settings
from app.workers.config import get_celery_config

# ──────────────────────────────────────────────────────────────────────────────
# Instanciation de l'application Celery
# Le nom du module est utilisé par Celery pour l'auto-découverte des tâches.
# ──────────────────────────────────────────────────────────────────────────────
celery_app = Celery(
    "meeting_ai",
    broker=settings.celery_broker_url_to_use,
    backend=settings.celery_result_backend_to_use,
    include=[
        "app.workers.tasks.health",
        "app.workers.tasks.meeting",
        "app.workers.tasks.transcription",
        "app.workers.tasks.report",
        "app.workers.tasks.embeddings",
        "app.workers.tasks.cleanup",
    ],
)

# ──────────────────────────────────────────────────────────────────────────────
# Application de la configuration centralisée (depuis config.py + Settings)
# ──────────────────────────────────────────────────────────────────────────────
celery_app.conf.update(get_celery_config())


# ──────────────────────────────────────────────────────────────────────────────
# Alignement du Logger Celery sur le Logger applicatif centralisé
# Les signaux Celery permettent de rediriger les logs des workers
# et des tâches vers le logger 'meeting_ai' de notre projet.
# Aucun print() n'est utilisé.
# ──────────────────────────────────────────────────────────────────────────────
@after_setup_logger.connect
def configure_celery_worker_logger(logger, *args, **kwargs):
    """
    Alignement du logger principal du worker Celery
    sur le logger applicatif centralisé du projet.
    """
    from app.core.logger import setup_logging
    setup_logging()
    app_logger = logging.getLogger("meeting_ai")
    logger.handlers = app_logger.handlers
    logger.level = app_logger.level


@after_setup_task_logger.connect
def configure_celery_task_logger(logger, *args, **kwargs):
    """
    Alignement du logger des tâches Celery
    sur le logger applicatif centralisé du projet.
    """
    app_logger = logging.getLogger("meeting_ai")
    logger.handlers = app_logger.handlers
    logger.level = app_logger.level


# Import des signaux Celery pour enregistrement automatique
from app.workers import signals


