"""
Composant de récupération sémantique (Retriever).
Interroge ChromaDB pour récupérer les documents les plus pertinents.
"""
import logging
from app.ai.embeddings.vector_store import VectorStore
from app.ai.schemas.rag import RAGSourceDocument
from app.ai.exceptions import RAGException
from app.core.settings import settings

logger = logging.getLogger("meeting_ai")


class Retriever:
    """
    Exécute la recherche vectorielle dans ChromaDB et retourne
    les documents les plus proches sémantiquement de la requête.
    """

    def __init__(self):
        self._vector_store = VectorStore()

    def retrieve(
        self,
        meeting_id: str,
        question: str,
        top_k: int | None = None,
    ) -> list[RAGSourceDocument]:
        """
        Récupère les chunks de la réunion les plus proches de la question.
        :param meeting_id: Identifiant de la réunion (filtre sur la collection).
        :param question: Question de l'utilisateur en langage naturel.
        :param top_k: Nombre maximum de documents à retourner.
        :return: Liste de RAGSourceDocument validés.
        :raises RAGException: En cas d'erreur de recherche.
        """
        n = top_k or settings.RAG_TOP_K
        collection_name = f"{settings.VECTOR_COLLECTION}_{meeting_id}"

        logger.info(
            f"[Retriever] Recherche sémantique dans la collection '{collection_name}' "
            f"pour : '{question[:60]}...'"
        )
        try:
            raw_results = self._vector_store.search(
                collection_name=collection_name,
                query_text=question,
                top_k=n,
            )
            documents = [
                RAGSourceDocument(
                    content=r["content"],
                    metadata=r.get("metadata", {}),
                    distance=r.get("distance"),
                )
                for r in raw_results
            ]
            logger.info(f"[Retriever] {len(documents)} document(s) récupéré(s).")
            return documents
        except Exception as e:
            logger.error(f"[Retriever] Erreur lors de la récupération : {e}")
            raise RAGException(f"Impossible de récupérer les documents : {str(e)}")
