"""
Orchestrateur principal du pipeline RAG complet.
Coordonne : Retriever → ContextBuilder → RAGGenerator.
"""
import logging
from app.ai.rag.retriever import Retriever
from app.ai.rag.context_builder import ContextBuilder
from app.ai.llm.rag_generator import RAGGenerator
from app.ai.schemas.rag import RAGQuery, RAGResponse
from app.ai.exceptions import RAGException

logger = logging.getLogger("meeting_ai")


class AnswerGenerator:
    """
    Orchestre le pipeline RAG complet :
    Question → Recherche Vectorielle → Construction du Contexte → LLM → Réponse.
    """

    def __init__(self):
        self._retriever = Retriever()
        self._context_builder = ContextBuilder()
        self._rag_generator = RAGGenerator()

    def answer(self, query: RAGQuery) -> RAGResponse:
        """
        Exécute le pipeline RAG complet pour une requête utilisateur.
        :param query: Objet RAGQuery validé contenant meeting_id et question.
        :return: RAGResponse avec la réponse et les documents sources utilisés.
        :raises RAGException: En cas d'échec à n'importe quelle étape du pipeline.
        """
        logger.info(
            f"[AnswerGenerator] Début du pipeline RAG pour la réunion "
            f"'{query.meeting_id}' — Question : '{query.question[:80]}'"
        )
        try:
            # Étape 1 : Récupération des documents pertinents depuis ChromaDB
            source_documents = self._retriever.retrieve(
                meeting_id=query.meeting_id,
                question=query.question,
            )

            # Étape 2 : Construction du contexte documentaire
            context = self._context_builder.build(source_documents)

            # Étape 3 : Génération de la réponse par le LLM
            answer_text = self._rag_generator.generate(
                question=query.question,
                context=context,
            )

            response = RAGResponse(
                meeting_id=query.meeting_id,
                question=query.question,
                answer=answer_text,
                sources=source_documents,
            )

            logger.info(
                f"[AnswerGenerator] Pipeline RAG terminé — "
                f"{len(source_documents)} sources utilisées."
            )
            return response

        except RAGException:
            raise
        except Exception as e:
            logger.error(f"[AnswerGenerator] Erreur inattendue dans le pipeline RAG : {e}")
            raise RAGException(f"Échec du pipeline RAG : {str(e)}")
