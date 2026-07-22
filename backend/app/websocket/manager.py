import asyncio
import logging
from fastapi import WebSocket, WebSocketDisconnect
from app.core.settings import settings
from app.websocket.connection import WebSocketConnection
from app.websocket.exceptions import ConnectionLimitException
from app.websocket.events import WSEvent

logger = logging.getLogger("meeting_ai")


class ConnectionManager:
    """
    Singleton thread-safe gérant les connexions WebSocket actives, les rooms et la diffusion.
    """
    _instance = None
    _lock = asyncio.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._connections = {}  # websocket -> WebSocketConnection
            cls._instance._lock = asyncio.Lock()
        return cls._instance

    async def connect(self, websocket: WebSocket, user_id: str, meeting_id: str | None = None) -> WebSocketConnection:
        """
        Enregistre une nouvelle connexion client active.
        """
        async with self._lock:
            if len(self._connections) >= settings.WEBSOCKET_MAX_CONNECTIONS:
                logger.warning(
                    f"[WebSocket Manager] Connexion refusée pour l'utilisateur '{user_id}' : "
                    f"nombre max de connexions atteint ({settings.WEBSOCKET_MAX_CONNECTIONS})."
                )
                raise ConnectionLimitException(settings.WEBSOCKET_MAX_CONNECTIONS)

            connection = WebSocketConnection(websocket, user_id, meeting_id)
            self._connections[websocket] = connection
            logger.info(
                f"[WebSocket Manager] Client connecté — Utilisateur: '{user_id}', "
                f"Réunion: '{meeting_id or 'aucune'}', Total: {len(self._connections)} connexions actives."
            )
            return connection

    async def disconnect(self, websocket: WebSocket) -> None:
        """
        Supprime proprement une connexion.
        """
        async with self._lock:
            if websocket in self._connections:
                conn = self._connections.pop(websocket)
                logger.info(
                    f"[WebSocket Manager] Client déconnecté — Utilisateur: '{conn.user_id}', "
                    f"Total restant: {len(self._connections)} connexions actives."
                )

    async def send_json(self, websocket: WebSocket, event: WSEvent) -> None:
        """
        Envoie un événement JSON à une connexion unique de manière sécurisée.
        """
        try:
            await websocket.send_json(event.model_dump(mode="json"))
        except (WebSocketDisconnect, RuntimeError):
            # Supprime la connexion de manière asynchrone si elle est cassée
            await self.disconnect(websocket)
        except Exception as e:
            logger.error(f"[WebSocket Manager] Erreur lors de l'envoi du message : {e}")

    async def broadcast(self, event: WSEvent) -> None:
        """
        Diffuse un événement à l'ensemble des clients connectés.
        """
        # On copie les sockets pour éviter les problèmes de modification concurrente
        async with self._lock:
            websockets = list(self._connections.keys())

        if not websockets:
            return

        logger.debug(f"[WebSocket Manager] Diffusion générale de l'événement '{event.event}' à {len(websockets)} clients.")
        # Utiliser asyncio.gather pour diffuser en parallèle sans bloquer
        await asyncio.gather(
            *(self.send_json(ws, event) for ws in websockets),
            return_exceptions=True
        )

    async def broadcast_room(self, room: str, event: WSEvent) -> None:
        """
        Diffuse un événement aux clients inscrits à une room spécifique.
        """
        async with self._lock:
            targets = [
                ws for ws, conn in self._connections.items()
                if conn.in_room(room)
            ]

        if not targets:
            return

        logger.info(
            f"[WebSocket Manager] Diffusion dans la room '{room}' de l'événement '{event.event}' "
            f"à {len(targets)} clients."
        )
        await asyncio.gather(
            *(self.send_json(ws, event) for ws in targets),
            return_exceptions=True
        )

    async def broadcast_meeting(self, meeting_id: str, event: WSEvent) -> None:
        """
        Diffuse un événement lié à une réunion spécifique (room meeting:{meeting_id}).
        """
        await self.broadcast_room(f"meeting:{meeting_id}", event)

    async def broadcast_user(self, user_id: str, event: WSEvent) -> None:
        """
        Diffuse un événement à un utilisateur spécifique (room user:{user_id}).
        """
        await self.broadcast_room(f"user:{user_id}", event)

    async def heartbeat(self) -> None:
        """
        Tâche périodique de Ping/Pong (Heartbeat) pour maintenir la connexion active
        et détecter les connexions mortes.
        """
        while True:
            try:
                await asyncio.sleep(settings.WEBSOCKET_HEARTBEAT_INTERVAL)
                async with self._lock:
                    websockets = list(self._connections.keys())

                if not websockets:
                    continue

                logger.debug(f"[WebSocket Manager] Envoi heartbeat à {len(websockets)} clients.")
                heartbeat_event = WSEvent(
                    event="HEARTBEAT",
                    payload={"status": "ping"}
                )

                await asyncio.gather(
                    *(self.send_json(ws, heartbeat_event) for ws in websockets),
                    return_exceptions=True
                )
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[WebSocket Manager] Erreur inattendue dans la boucle de heartbeat : {e}")
