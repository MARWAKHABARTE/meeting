from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from app.services.ai_service import AIService
from app.db.session import SessionLocal
from app.models.meeting import Meeting
from app.core.settings import settings
import uuid
import logging

logger = logging.getLogger("meeting_ai")
router = APIRouter()
ai_service = AIService()

class TranscriptionStartRequest(BaseModel):
    """
    Schéma de validation pour démarrer le pipeline de transcription.
    """
    meeting_id: str = Field(..., description="ID de la réunion à transcrire")


@router.post("/start", response_model=dict, status_code=status.HTTP_202_ACCEPTED)
def start_transcription(payload: TranscriptionStartRequest):
    """
    Déclenche de manière asynchrone le pipeline de transcription (Whisper + Pyannote)
    pour la réunion demandée.
    """
    meeting_id = payload.meeting_id
    try:
        meeting_uuid = uuid.UUID(meeting_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"L'identifiant '{meeting_id}' n'est pas un UUID valide."
        )

    # Récupération de l'audio associé à la réunion en base de données
    db = SessionLocal()
    try:
        meeting = db.query(Meeting).filter(Meeting.id == meeting_uuid).first()
        if not meeting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"La réunion '{meeting_id}' n'existe pas en base."
            )
            
        if not meeting.files:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La réunion '{meeting_id}' ne possède pas de fichier audio attaché."
            )
            
        # Premier fichier attaché comme source audio
        audio_file = meeting.files[0]
        object_name = audio_file.file_path
        bucket_name = settings.minio_bucket_to_use
    finally:
        db.close()

    # Déclenchement de la tâche asynchrone Celery
    try:
        task_id = ai_service.start_transcription(
            meeting_id=meeting_id,
            bucket_name=bucket_name,
            object_name=object_name
        )
        return {
            "task_id": task_id,
            "status": "queued"
        }
    except Exception as e:
        logger.error(f"[Transcriptions API] Échec de mise en file d'attente : {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service de traitement temporairement indisponible : {str(e)}"
        )


@router.get("/{task_id}", response_model=dict)
def get_transcription_status(task_id: str):
    """
    Consulte l'état de la tâche Celery de transcription.
    """
    try:
        task_status = ai_service.get_task_status(task_id)
        return {
            "task_id": task_id,
            "status": task_status
        }
    except Exception as e:
        logger.error(f"[Transcriptions API] Erreur de récupération du statut pour '{task_id}' : {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Impossible d'interroger la file d'attente : {str(e)}"
        )


@router.get("/{task_id}/result", response_model=dict)
def get_transcription_result(task_id: str):
    """
    Retourne le texte consolidé et la timeline fusionnée locuteurs-transcription.
    """
    try:
        task_status = ai_service.get_task_status(task_id)
        
        if task_status in ("PENDING", "STARTED", "RETRY"):
            raise HTTPException(
                status_code=status.HTTP_202_ACCEPTED,
                detail="Le traitement de transcription est toujours en cours d'exécution."
            )
            
        if task_status == "FAILURE":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Le pipeline de traitement IA a échoué."
            )

        # Récupération depuis la base de données
        result = ai_service.get_task_result(task_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Résultat introuvable ou intégrité du transcript corrompue."
            )
            
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Transcriptions API] Échec d'extraction du résultat pour '{task_id}' : {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur interne de traitement : {str(e)}"
        )
