import asyncio
import json
import logging
import redis.asyncio as aioredis
from app.core.settings import settings
from app.websocket.manager import ConnectionManager
from app.websocket.events import WSEvent

logger = logging.getLogger("meeting_ai")


class RedisBroadcaster:
    """
    Tâche asynchrone d'arrière-plan abonnée à un canal Redis Pub/Sub.
    Elle fait office de passerelle entre les Workers Celery (qui publient)
    et le ConnectionManager (qui diffuse).
    """
    _instance = None
    _lock = asyncio.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._manager = ConnectionManager()
            cls._instance._channel = settings.WEBSOCKET_REDIS_CHANNEL
            cls._instance._redis_url = settings.redis_url
            cls._instance._task = None
            cls._instance._running = False
        return cls._instance

    async def start(self) -> None:
        """
        Démarre la tâche de fond asyncio de lecture Redis Pub/Sub.
        """
        async with self._lock:
            if self._running:
                return
            self._running = True
            self._task = asyncio.create_task(self._loop())
            logger.info("[Broadcaster] RedisBroadcaster démarré.")

    async def stop(self) -> None:
        """
        Arrête la tâche de fond proprement.
        """
        async with self._lock:
            if not self._running:
                return
            self._running = False
            if self._task:
                self._task.cancel()
                try:
                    await self._task
                except asyncio.CancelledError:
                    pass
            logger.info("[Broadcaster] RedisBroadcaster arrêté.")

    async def _loop(self) -> None:
        """
        Boucle principale de lecture Pub/Sub avec mécanisme de reconnexion.
        """
        while self._running:
            try:
                logger.info(f"[Broadcaster] Connexion à Redis Pub/Sub sur {self._redis_url}...")
                redis_client = aioredis.from_url(self._redis_url)
                pubsub = redis_client.pubsub()
                await pubsub.subscribe(self._channel)
                logger.info(f"[Broadcaster] Abonné au canal '{self._channel}'. Attente des messages...")

                while self._running:
                    # Lecture non bloquante avec un timeout de 1s pour permettre l'arrêt
                    message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                    if message and message["type"] == "message":
                        data_str = message["data"].decode("utf-8")
                        try:
                            data = json.loads(data_str)
                            event = WSEvent(**data)
                            await self._dispatch(event)
                        except json.JSONDecodeError as e:
                            logger.error(f"[Broadcaster] Erreur de décodage JSON : {e}. Message: {data_str}")
                        except Exception as e:
                            logger.error(f"[Broadcaster] Erreur de validation de l'événement : {e}")

                await pubsub.unsubscribe(self._channel)
                await redis_client.close()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[Broadcaster] Erreur de connexion Redis Pub/Sub : {e}. Reconnexion dans 5 secondes...")
                await asyncio.sleep(5)

    async def _dispatch(self, event: WSEvent) -> None:
        """
        Dispatche l'événement lu dans la bonne room ou de manière globale.
        """
        meeting_id = event.meeting_id
        user_id = event.payload.get("user_id")

        if meeting_id:
            # Diffuse à la room de la réunion
            await self._manager.broadcast_meeting(meeting_id, event)
        elif user_id:
            # Diffuse à l'utilisateur ciblé
            await self._manager.broadcast_user(user_id, event)
        else:
            # Diffusion générale
            await self._manager.broadcast(event)
