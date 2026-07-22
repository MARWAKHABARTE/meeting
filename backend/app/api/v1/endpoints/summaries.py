"""
Endpoints FastAPI pour le pipeline NLP (génération de résumés, décisions, actions).
"""
import logging
from fastapi import APIRouter, HTTPException, status
from app.services.summary_service import SummaryService

logger = logging.getLogger("meeting_ai")
router = APIRouter()
_summary_service = SummaryService()


@router.post("/start", response_model=dict, status_code=status.HTTP_202_ACCEPTED)
def start_summary(payload: dict):
    """
    Déclenche les tâches asynchrones Celery de résumé NLP et d'indexation.
    Body : {"meeting_id": "..."}
    """
    meeting_id = payload.get("meeting_id")
    if not meeting_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le champ 'meeting_id' est obligatoire."
        )
    try:
        result = _summary_service.start_summary(meeting_id)
        logger.info(f"[summaries API] Pipeline NLP lancé pour '{meeting_id}'.")
        return result
    except Exception as e:
        logger.error(f"[summaries API] Erreur de déclenchement : {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Impossible de lancer le pipeline NLP : {str(e)}"
        )


@router.get("/{meeting_id}", response_model=dict)
def get_summary(meeting_id: str):
    """
    Retourne le rapport NLP complet d'une réunion depuis PostgreSQL.
    """
    try:
        result = _summary_service.get_summary(meeting_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Aucun résumé disponible pour la réunion '{meeting_id}'."
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[summaries API] Erreur de récupération pour '{meeting_id}' : {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
