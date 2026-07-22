class AIException(Exception):
    """Exception de base pour toutes les erreurs du module IA."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class AudioNotFoundException(AIException):
    def __init__(self, filename: str, details: str = ""):
        super().__init__(f"Fichier audio '{filename}' introuvable. {details}".strip())
        self.filename = filename


class StorageException(AIException):
    def __init__(self, details: str):
        super().__init__(f"Erreur de stockage MinIO : {details}")
        self.details = details


class WhisperException(AIException):
    def __init__(self, details: str):
        super().__init__(f"Erreur lors de la transcription Whisper : {details}")
        self.details = details


class PyannoteException(AIException):
    def __init__(self, details: str):
        super().__init__(f"Erreur lors de la diarisation Pyannote : {details}")
        self.details = details


class PipelineException(AIException):
    def __init__(self, details: str):
        super().__init__(f"Échec de l'exécution du pipeline de traitement : {details}")
        self.details = details


class OllamaUnavailable(AIException):
    def __init__(self, details: str):
        super().__init__(f"Le serveur Ollama est indisponible : {details}")
        self.details = details


class SummaryException(AIException):
    def __init__(self, details: str):
        super().__init__(f"Échec de la génération du résumé : {details}")
        self.details = details


class EmbeddingException(AIException):
    def __init__(self, details: str):
        super().__init__(f"Erreur lors de la génération des embeddings : {details}")
        self.details = details


class VectorStoreException(AIException):
    def __init__(self, details: str):
        super().__init__(f"Erreur du Vector Store ChromaDB : {details}")
        self.details = details


class RAGException(AIException):
    def __init__(self, details: str):
        super().__init__(f"Échec du pipeline RAG : {details}")
        self.details = details
