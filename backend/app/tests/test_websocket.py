import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi import WebSocket, WebSocketDisconnect
from app.websocket.connection import WebSocketConnection
from app.websocket.manager import ConnectionManager
from app.websocket.events import WSEvent, WSEventType
from app.websocket.exceptions import ConnectionLimitException
from app.workers.signals import on_task_prerun, on_task_postrun, on_task_failure


# ──────────────────────────────────────────────────────────────────────────────
# 1. Tests de WebSocketConnection
# ──────────────────────────────────────────────────────────────────────────────

def test_websocket_connection_init():
    websocket_mock = MagicMock(spec=WebSocket)
    conn = WebSocketConnection(websocket_mock, user_id="user_123", meeting_id="meeting_456")

    assert conn.websocket == websocket_mock
    assert conn.user_id == "user_123"
    assert conn.meeting_id == "meeting_456"
    assert "user:user_123" in conn.rooms
    assert "meeting:meeting_456" in conn.rooms


def test_websocket_connection_join_leave_room():
    websocket_mock = MagicMock(spec=WebSocket)
    conn = WebSocketConnection(websocket_mock, user_id="user_123")

    conn.join_room("custom_room")
    assert conn.in_room("custom_room")

    conn.leave_room("custom_room")
    assert not conn.in_room("custom_room")


# ──────────────────────────────────────────────────────────────────────────────
# 2. Tests de ConnectionManager (Singleton, Connect, Disconnect)
# ──────────────────────────────────────────────────────────────────────────────

@pytest.mark.anyio
async def test_connection_manager_connect_disconnect():
    manager = ConnectionManager()
    websocket_mock = MagicMock(spec=WebSocket)

    # Réinitialisation de l'état interne pour isolation du test
    manager._connections.clear()

    # Connexion
    conn = await manager.connect(websocket_mock, user_id="u1", meeting_id="m1")
    assert websocket_mock in manager._connections
    assert len(manager._connections) == 1
    assert conn.user_id == "u1"

    # Déconnexion
    await manager.disconnect(websocket_mock)
    assert websocket_mock not in manager._connections
    assert len(manager._connections) == 0


@pytest.mark.anyio
async def test_connection_manager_max_limit():
    manager = ConnectionManager()
    websocket_mock_1 = MagicMock(spec=WebSocket)
    websocket_mock_2 = MagicMock(spec=WebSocket)

    manager._connections.clear()

    # Mock settings.WEBSOCKET_MAX_CONNECTIONS à 1
    with patch("app.websocket.manager.settings") as mock_settings:
        mock_settings.WEBSOCKET_MAX_CONNECTIONS = 1

        # 1ère connexion -> OK
        await manager.connect(websocket_mock_1, user_id="u1")

        # 2ème connexion -> Levée ConnectionLimitException
        with pytest.raises(ConnectionLimitException):
            await manager.connect(websocket_mock_2, user_id="u2")


# ──────────────────────────────────────────────────────────────────────────────
# 3. Tests de Diffusion (Broadcast Meeting / User)
# ──────────────────────────────────────────────────────────────────────────────

@pytest.mark.anyio
async def test_connection_manager_broadcast_meeting():
    manager = ConnectionManager()
    ws_m1_1 = MagicMock(spec=WebSocket)
    ws_m1_1.send_json = AsyncMock()
    ws_m2_1 = MagicMock(spec=WebSocket)
    ws_m2_1.send_json = AsyncMock()

    manager._connections.clear()

    # Enregistrement des connexions
    await manager.connect(ws_m1_1, user_id="u1", meeting_id="meeting_1")
    await manager.connect(ws_m2_1, user_id="u2", meeting_id="meeting_2")

    # Événement cible meeting_1
    event = WSEvent(
        event=WSEventType.TRANSCRIPTION_PROGRESS,
        meeting_id="meeting_1",
        payload={"percent": 50}
    )

    # Diffusion
    await manager.broadcast_meeting("meeting_1", event)

    # ws_m1_1 doit recevoir l'événement, ws_m2_1 ne doit rien recevoir
    ws_m1_1.send_json.assert_called_once()
    ws_m2_1.send_json.assert_not_called()


# ──────────────────────────────────────────────────────────────────────────────
# 4. Tests des signaux Celery
# ──────────────────────────────────────────────────────────────────────────────

@patch("app.workers.signals.WebSocketService.publish")
def test_celery_signals_prerun(mock_publish):
    # Mock du sender de la tâche
    task_mock = MagicMock()
    task_mock.name = "workers.transcription_task"

    on_task_prerun(
        sender=task_mock,
        task_id="t-123",
        args=("meeting-uuid-789",),
        kwargs={}
    )

    # Vérification qu'un événement TRANSCRIPTION_STARTED a été publié
    mock_publish.assert_called_once()
    published_event = mock_publish.call_args[0][0]
    assert isinstance(published_event, WSEvent)
    assert published_event.event == WSEventType.TRANSCRIPTION_STARTED
    assert published_event.meeting_id == "meeting-uuid-789"
    assert published_event.payload["percent"] == 0
