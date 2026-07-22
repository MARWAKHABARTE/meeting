"""
Constructeur du contexte documentaire pour le RAG.
Assemble les documents récupérés en un bloc de texte cohérent.
"""
import logging
from app.ai.schemas.rag import RAGSourceDocument
from app.core.settings import settings

logger = logging.getLogger("meeting_ai")


class ContextBuilder:
    """
    Assemble les documents sources récupérés par le Retriever
    en un bloc de contexte lisible par le LLM.
    """

    def build(self, documents: list[RAGSourceDocument]) -> str:
        """
        Concatène les extraits documentaires en un contexte structuré.
        :param documents: Documents récupérés par le Retriever.
        :return: Contexte formaté prêt à être injecté dans le prompt RAG.
        """
        if not documents:
            logger.warning("[ContextBuilder] Aucun document source fourni — contexte vide.")
            return "Aucun contexte disponible."

        parts = []
        for i, doc in enumerate(documents, start=1):
            speaker = doc.metadata.get("speaker", "Inconnu")
            chunk_index = doc.metadata.get("chunk_index", "?")
            parts.append(
                f"[Extrait {i} — Locuteur : {speaker}, Chunk #{chunk_index}]\n{doc.content}"
            )

        context = "\n\n".join(parts)

        # Troncature si le contexte dépasse la limite configurée
        if len(context) > settings.MAX_CONTEXT_LENGTH:
            context = context[:settings.MAX_CONTEXT_LENGTH]
            logger.warning(
                f"[ContextBuilder] Contexte tronqué à {settings.MAX_CONTEXT_LENGTH} caractères."
            )

        logger.info(
            f"[ContextBuilder] Contexte assemblé : {len(documents)} extraits, "
            f"{len(context)} caractères."
        )
        return context
