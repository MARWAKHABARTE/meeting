from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class WSEventType(str, Enum):
    # Upload events
    UPLOAD_STARTED = "UPLOAD_STARTED"
    UPLOAD_PROGRESS = "UPLOAD_PROGRESS"
    UPLOAD_COMPLETED = "UPLOAD_COMPLETED"

    # Transcription events
    TRANSCRIPTION_STARTED = "TRANSCRIPTION_STARTED"
    TRANSCRIPTION_PROGRESS = "TRANSCRIPTION_PROGRESS"
    TRANSCRIPTION_COMPLETED = "TRANSCRIPTION_COMPLETED"

    # NLP/Summary events
    SUMMARY_STARTED = "SUMMARY_STARTED"
    SUMMARY_COMPLETED = "SUMMARY_COMPLETED"

    # Embeddings/ChromaDB events
    EMBEDDING_STARTED = "EMBEDDING_STARTED"
    EMBEDDING_COMPLETED = "EMBEDDING_COMPLETED"

    # RAG events
    RAG_STARTED = "RAG_STARTED"
    RAG_COMPLETED = "RAG_COMPLETED"

    # System events
    MEETING_UPDATED = "MEETING_UPDATED"
    NOTIFICATION = "NOTIFICATION"
    ERROR = "ERROR"
    HEARTBEAT = "HEARTBEAT"


class WSEvent(BaseModel):
    """
    Structure type d'un événement WebSocket.
    """
    event: WSEventType = Field(..., description="Type de l'événement")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp UTC")
    meeting_id: str | None = Field(None, description="ID de la réunion concernée")
    payload: dict = Field(default_factory=dict, description="Données associées à l'événement")
