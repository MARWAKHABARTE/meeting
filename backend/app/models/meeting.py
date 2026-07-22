import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Enum, DateTime
from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.workspace import Workspace
    from app.models.meeting_file import MeetingFile
    from app.models.speaker import Speaker
    from app.models.transcript import Transcript
    from app.models.summary import Summary
    from app.models.decision import Decision
    from app.models.action_item import ActionItem
    from app.models.sentiment_analysis import SentimentAnalysis
    from app.models.embedding import Embedding
    from app.models.chat_conversation import ChatConversation
    from app.models.report import Report

class MeetingStatus(str, PyEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Meeting(Base):
    """
    Modèle central représentant une réunion importée/enregistrée.
    """
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[MeetingStatus] = mapped_column(Enum(MeetingStatus), default=MeetingStatus.PENDING, index=True)
    
    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspace.id"), nullable=False, index=True)
    
    # Relations Parentes
    workspace: Mapped["Workspace"] = relationship("Workspace", back_populates="meetings")
    
    # Relations Enfants
    files: Mapped[list["MeetingFile"]] = relationship("MeetingFile", back_populates="meeting", cascade="all, delete-orphan")
    speakers: Mapped[list["Speaker"]] = relationship("Speaker", back_populates="meeting", cascade="all, delete-orphan")
    transcript: Mapped["Transcript"] = relationship("Transcript", back_populates="meeting", uselist=False, cascade="all, delete-orphan")
    summary: Mapped["Summary"] = relationship("Summary", back_populates="meeting", uselist=False, cascade="all, delete-orphan")
    decisions: Mapped[list["Decision"]] = relationship("Decision", back_populates="meeting", cascade="all, delete-orphan")
    action_items: Mapped[list["ActionItem"]] = relationship("ActionItem", back_populates="meeting", cascade="all, delete-orphan")
    sentiment_analyses: Mapped[list["SentimentAnalysis"]] = relationship("SentimentAnalysis", back_populates="meeting", cascade="all, delete-orphan")
    embeddings: Mapped[list["Embedding"]] = relationship("Embedding", back_populates="meeting", cascade="all, delete-orphan")
    chat_conversations: Mapped[list["ChatConversation"]] = relationship("ChatConversation", back_populates="meeting", cascade="all, delete-orphan")
    reports: Mapped[list["Report"]] = relationship("Report", back_populates="meeting", cascade="all, delete-orphan")
