"""
Endpoints FastAPI pour le pipeline RAG (question/réponse et santé).
"""
import logging
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from app.services.rag_service import RAGService
from app.ai.exceptions import RAGException, VectorStoreException

logger = logging.getLogger("meeting_ai")
router = APIRouter()
_rag_service = RAGService()


class RAGQueryRequest(BaseModel):
    meeting_id: str = Field(..., description="Identifiant de la réunion à interroger")
    question: str = Field(..., min_length=3, description="Question en langage naturel")


@router.post("/query", response_model=dict, status_code=status.HTTP_200_OK)
def query_rag(payload: RAGQueryRequest):
    """
    Exécute une recherche RAG complète sur la réunion spécifiée.
    Retourne la réponse LLM enrichie des sources documentaires.
    """
    try:
        result = _rag_service.query(
            meeting_id=payload.meeting_id,
            question=payload.question
        )
        return result.model_dump()
    except (RAGException, VectorStoreException) as e:
        logger.error(f"[rag API] Erreur RAG contrôlée : {e.message}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"[rag API] Erreur inattendue RAG : {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur interne du pipeline RAG : {str(e)}"
        )


@router.get("/health", response_model=dict)
def rag_health():
    """
    Vérifie la santé de l'infrastructure RAG (Ollama + ChromaDB).
    """
    try:
        return _rag_service.health()
    except Exception as e:
        logger.error(f"[rag API] Erreur lors du health check : {e}")
        return {"status": "error", "detail": str(e)}
