"""
Générateur de réponse finale du pipeline RAG via Ollama.
"""
import logging
from app.ai.llm.ollama_client import OllamaClient
from app.ai.llm.prompt_builder import PromptBuilder
from app.ai.exceptions import RAGException

logger = logging.getLogger("meeting_ai")


class RAGGenerator:
    """
    Génère la réponse finale à une question utilisateur en utilisant
    le contexte documentaire récupéré depuis ChromaDB.
    """

    def __init__(self):
        self._client = OllamaClient()

    def generate(self, question: str, context: str) -> str:
        """
        Génère une réponse textuelle à partir d'une question et d'un contexte.
        :param question: Question en langage naturel de l'utilisateur.
        :param context: Contexte documentaire assemblé par ContextBuilder.
        :return: Réponse textuelle du LLM.
        :raises RAGException: En cas d'échec de génération.
        """
        logger.info(f"[RAGGenerator] Génération de réponse RAG pour : '{question[:60]}...'")
        try:
            prompt = PromptBuilder.build_rag_prompt(question=question, context=context)
            answer = self._client.generate(prompt).strip()
            logger.info(f"[RAGGenerator] Réponse générée ({len(answer)} caractères).")
            return answer
        except Exception as e:
            logger.error(f"[RAGGenerator] Erreur lors de la génération RAG : {e}")
            raise RAGException(f"Impossible de générer la réponse RAG : {str(e)}")
