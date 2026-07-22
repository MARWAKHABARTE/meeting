# ==============================================================================
# Centralisation des modèles pour les migrations Alembic
# ==============================================================================
# Cet import permet à Alembic de découvrir les métadonnées de la base déclarative
from .base_class import Base  # noqa: F401

# Importez vos futurs modèles métier ici pour qu'ils soient détectés par Alembic :
from app.models.user import User  # noqa: F401
from app.models.workspace import Workspace  # noqa: F401
from app.models.meeting import Meeting  # noqa: F401
from app.models.meeting_file import MeetingFile  # noqa: F401
from app.models.speaker import Speaker  # noqa: F401
from app.models.transcript import Transcript  # noqa: F401
from app.models.transcript_segment import TranscriptSegment  # noqa: F401
from app.models.summary import Summary  # noqa: F401
from app.models.decision import Decision  # noqa: F401
from app.models.action_item import ActionItem  # noqa: F401
from app.models.sentiment_analysis import SentimentAnalysis  # noqa: F401
from app.models.embedding import Embedding  # noqa: F401
from app.models.chat_conversation import ChatConversation  # noqa: F401
from app.models.chat_message import ChatMessage  # noqa: F401
from app.models.report import Report  # noqa: F401
from app.models.notification import Notification  # noqa: F401
from app.models.audit_log import AuditLog  # noqa: F401
