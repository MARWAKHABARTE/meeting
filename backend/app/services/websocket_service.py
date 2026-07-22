import json
import logging
import redis
from datetime import datetime, timezone
from app.core.settings import settings
from app.websocket.events import WSEvent, WSEventType

logger = logging.getLogger("meeting_ai")


class WebSocketService:
    """
    Service permettant aux différents composants de l'application (notamment les Workers Celery)
    de publier des événements temps réel sur le canal Redis Pub/Sub.
    Garantit le découplage complet entre les tâches asynchrones et l'infrastructure WebSocket.
    """
    _redis_client = None

    @classmethod
    def _get_redis_client(cls):
        """Retourne un client Redis synchrone thread-safe unique (Lazy Loading)."""
        if cls._redis_client is None:
            cls._redis_client = redis.Redis.from_url(settings.redis_url)
            logger.info("[WebSocketService] Client Redis synchrone initialisé.")
        return cls._redis_client

    @classmethod
    def publish(cls, event: WSEvent) -> None:
        """
        Publie un événement sur le canal Redis Pub/Sub.
        """
        try:
            client = cls._get_redis_client()
            channel = settings.WEBSOCKET_REDIS_CHANNEL
            message = event.model_dump_as_json() if hasattr(event, "model_dump_as_json") else json.dumps(event.model_dump(mode="json"))
            client.publish(channel, message)
            logger.debug(f"[WebSocketService] Événement '{event.event}' publié sur le canal '{channel}'.")
        except Exception as e:
            logger.error(f"[WebSocketService] Échec de publication de l'événement : {e}")

    @classmethod
    def publish_meeting_progress(
        cls,
        meeting_id: str,
        event_type: WSEventType,
        step: str,
        percent: int,
        status: str = "running",
        details: str | None = None,
        user_id: str | None = None
    ) -> None:
        """
        Helper pour envoyer facilement un événement de progression de réunion.
        """
        payload = {
            "step": step,
            "percent": percent,
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        if details:
            payload["details"] = details
        if user_id:
            payload["user_id"] = user_id

        event = WSEvent(
            event=event_type,
            meeting_id=meeting_id,
            payload=payload
        )
        cls.publish(event)
