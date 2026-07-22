from enum import Enum

# Préfixe global pour l'API
API_PREFIX = "/api/v1"

# Pagination
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100

# Fuseau horaire par défaut (Eurafric Information est basée au Maroc)
DEFAULT_TIMEZONE = "Africa/Casablanca"

# Langues supportées par l'application
SUPPORTED_LANGUAGES = ["fr", "en", "ar"]

# Modèles IA par défaut
DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_WHISPER_MODEL = "base"
DEFAULT_SUMMARY_MODEL = "gpt-3.5-turbo"


class UserRole(str, Enum):
    """
    Rôles utilisateur pour l'autorisation Keycloak.
    """
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"


class MeetingStatus(str, Enum):
    """
    Statuts du cycle de vie du traitement d'une réunion.
    """
    PENDING = "PENDING"
    UPLOADING = "UPLOADING"
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    TRANSCRIBING = "TRANSCRIBING"
    DIARIZING = "DIARIZING"
    ANALYZING = "ANALYZING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


# Formats vidéo autorisés pour l'analyse
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".webm"}

# Taille maximale du fichier vidéo (500 Mo par défaut)
MAX_CONTENT_LENGTH_BYTES = 500 * 1024 * 1024

# Langues supportées par le pipeline de transcription
class AudioLanguage(str, Enum):
    FRENCH = "fr"
    ENGLISH = "en"
    ARABIC = "ar"
    AUTO = "auto"
