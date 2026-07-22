"""
Service orchestrant le pipeline RAG.
Aucune logique IA directe — délégation vers AnswerGenerator et VectorStore.
"""
import logging
from app.ai.rag.answer_generator import AnswerGenerator
from app.ai.embeddings.vector_store import VectorStore
from app.ai.llm.ollama_client import OllamaClient
from app.ai.schemas.rag import RAGQuery, RAGResponse

logger = logging.getLogger("meeting_ai")


class RAGService:
    """
    Service exposant les opérations RAG à la couche API.
    Aucun traitement vectoriel ou LLM n'est effectué ici directement.
    """

    def __init__(self):
        self._answer_generator = AnswerGenerator()
        self._ollama_client = OllamaClient()
        self._vector_store = VectorStore()

    def query(self, meeting_id: str, question: str) -> RAGResponse:
        """
        Exécute une requête RAG complète sur une réunion.
        :param meeting_id: ID de la réunion à interroger.
        :param question: Question en langage naturel de l'utilisateur.
        :return: RAGResponse validé par Pydantic.
        """
        logger.info(f"[RAGService] Requête pour '{meeting_id}' : '{question[:80]}'")
        rag_query = RAGQuery(meeting_id=meeting_id, question=question)
        return self._answer_generator.answer(rag_query)

    def health(self) -> dict:
        """
        Vérifie l'état de santé de l'infrastructure RAG (Ollama + ChromaDB).
        Retourne immédiatement sans bloquer si un service est indisponible.
        """
        # Health Ollama : timeout réduit, ne bloque pas le serveur
        ollama_ok = False
        try:
            ollama_ok = self._ollama_client.health()
        except Exception as e:
            logger.warning(f"[RAGService] Ollama indisponible : {e}")

        # Health ChromaDB : vérification du client persistant
        chroma_ok = False
        try:
            self._vector_store._get_client()
            chroma_ok = True
        except Exception as e:
            logger.warning(f"[RAGService] ChromaDB indisponible : {e}")

        status = "healthy" if ollama_ok and chroma_ok else "degraded"
        logger.info(
            f"[RAGService] Health — Ollama: {'OK' if ollama_ok else 'KO'}, "
            f"ChromaDB: {'OK' if chroma_ok else 'KO'}"
        )
        return {
            "status": status,
            "ollama": "online" if ollama_ok else "offline",
            "chromadb": "online" if chroma_ok else "offline",
        }
