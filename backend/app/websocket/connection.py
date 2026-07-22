from fastapi import WebSocket
from typing import Set


class WebSocketConnection:
    """
    Encapsule une connexion WebSocket client active avec ses métadonnées.
    """
    def __init__(self, websocket: WebSocket, user_id: str, meeting_id: str | None = None):
        self.websocket = websocket
        self.user_id = user_id
        self.meeting_id = meeting_id
        self.rooms: Set[str] = set()

        # Rejoindre automatiquement la room utilisateur
        self.rooms.add(f"user:{user_id}")

        # Rejoindre la room de la réunion spécifique si présente
        if meeting_id:
            self.rooms.add(f"meeting:{meeting_id}")

    def join_room(self, room: str) -> None:
        """Ajoute la connexion à une room spécifique."""
        self.rooms.add(room)

    def leave_room(self, room: str) -> None:
        """Retire la connexion d'une room spécifique."""
        self.rooms.discard(room)

    def in_room(self, room: str) -> bool:
        """Vérifie si la connexion appartient à une room."""
        return room in self.rooms
