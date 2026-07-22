from pydantic_settings import BaseSettings


class AISettings(BaseSettings):
    """
    Configuration complète du pipeline IA :
    Whisper, Pyannote, Ollama, Embeddings, Chunker, ChromaDB et RAG.
    """
    # ──────────────────────────────────────────────────────────
    # Whisper (Transcription ASR)
    # ──────────────────────────────────────────────────────────
    WHISPER_MODEL: str = "base"
    WHISPER_DEVICE: str = "cpu"
    WHISPER_COMPUTE_TYPE: str = "float32"

    # ──────────────────────────────────────────────────────────
    # Pyannote (Diarisation)
    # ──────────────────────────────────────────────────────────
    PYANNOTE_MODEL: str = "pyannote/speaker-diarization-3.1"
    PYANNOTE_AUTH_TOKEN: str | None = None
    PYANNOTE_TOKEN: str | None = None

    # ──────────────────────────────────────────────────────────
    # Gestion des fichiers audio temporaires
    # ──────────────────────────────────────────────────────────
    AI_TEMP_DIRECTORY: str = "temp_ai"
    MAX_AUDIO_SIZE_MB: int = 100
    SUPPORTED_AUDIO_FORMATS: list[str] = ["mp3", "wav", "m4a", "flac", "ogg", "wma"]

    # ──────────────────────────────────────────────────────────
    # Ollama (LLM local — Sprint 9)
    # ──────────────────────────────────────────────────────────
    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "mistral"
    OLLAMA_TIMEOUT: int = 120

    # ──────────────────────────────────────────────────────────
    # Embeddings (sentence-transformers — Sprint 9)
    # ──────────────────────────────────────────────────────────
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    # ──────────────────────────────────────────────────────────
    # Chunking (découpage sémantique de texte — Sprint 9)
    # ──────────────────────────────────────────────────────────
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50

    # ──────────────────────────────────────────────────────────
    # ChromaDB (Vector Store — Sprint 9)
    # ──────────────────────────────────────────────────────────
    CHROMA_PERSIST_DIRECTORY: str = "chroma_db"
    VECTOR_COLLECTION: str = "meetings"

    # ──────────────────────────────────────────────────────────
    # RAG (Retrieval-Augmented Generation — Sprint 9)
    # ──────────────────────────────────────────────────────────
    RAG_TOP_K: int = 3
    MAX_CONTEXT_LENGTH: int = 4000

    # ──────────────────────────────────────────────────────────
    # Modèles NLP annexes (Sprint 10+)
    # ──────────────────────────────────────────────────────────
    LLM_MODEL: str = "gpt-3.5-turbo"
    SPACY_MODEL: str = "fr_core_news_sm"

    @property
    def pyannote_auth_token_to_use(self) -> str | None:
        """
        Retourne le token d'authentification Pyannote (Hugging Face) configuré.
        """
        return self.PYANNOTE_TOKEN or self.PYANNOTE_AUTH_TOKEN
