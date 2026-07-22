"""
Celery configuration module.
Centralise tous les paramètres spécifiques à Celery en les lisant
exclusivement depuis les Settings de l'application (pas de constantes en dur).
"""
from app.core.settings import settings


def get_celery_config() -> dict:
    """
    Retourne un dictionnaire de configuration Celery basé sur les Settings.
    Ce dictionnaire est appliqué à l'instance Celery via app.config_from_object().

    :return: Dictionnaire de configuration Celery
    """
    return {
        # ──────────────────────────────────────────────────────
        # Sérialisation des messages
        # ──────────────────────────────────────────────────────
        "task_serializer": settings.CELERY_TASK_SERIALIZER,
        "result_serializer": settings.CELERY_RESULT_SERIALIZER,
        "accept_content": settings.CELERY_ACCEPT_CONTENT,

        # ──────────────────────────────────────────────────────
        # Fuseau horaire — toujours UTC en production
        # ──────────────────────────────────────────────────────
        "timezone": settings.CELERY_TIMEZONE,
        "enable_utc": settings.CELERY_ENABLE_UTC,

        # ──────────────────────────────────────────────────────
        # Résilience du broker
        # Réessaie la connexion au Broker Redis au démarrage
        # au lieu de lever une exception immédiate.
        # ──────────────────────────────────────────────────────
        "broker_connection_retry_on_startup": True,

        # ──────────────────────────────────────────────────────
        # Comportement des tâches
        # ──────────────────────────────────────────────────────
        "task_track_started": True,  # Permet d'observer l'état STARTED
        "task_acks_late": True,       # La tâche n'est acquittée qu'après exécution réussie
        "worker_prefetch_multiplier": 1,  # Un seul message à la fois par worker (fairness)

        # ──────────────────────────────────────────────────────
        # Persistance des résultats
        # ──────────────────────────────────────────────────────
        "result_expires": 3600,  # Les résultats expirent après 1 heure dans Redis
    }
