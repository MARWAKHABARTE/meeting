"""
Tâche Celery de génération du rapport NLP complet d'une réunion.
Orchestre : résumé → sentiment → persistance PostgreSQL.
"""
import logging
import uuid
from app.workers.celery_app import celery_app
from app.db.session import SessionLocal
from app.models.meeting import Meeting, MeetingStatus
from app.models.transcript import Transcript
from app.models.summary import Summary
from app.models.decision import Decision
from app.models.action_item import ActionItem, ActionItemStatus
from app.models.sentiment_analysis import SentimentAnalysis
from app.ai.llm.summary_generator import SummaryGenerator
from app.ai.llm.sentiment_generator import SentimentGenerator
from app.ai.exceptions import AIException
from app.services.websocket_service import WebSocketService
from app.websocket.events import WSEventType

logger = logging.getLogger("meeting_ai")


@celery_app.task(
    name="workers.summary_task",
    bind=True,
    max_retries=3,
    default_retry_delay=30,
)
def summary_task(self, meeting_id: str) -> dict:
    """
    Génère le résumé NLP complet et l'analyse de sentiment d'une réunion.
    Sauvegarde les résultats dans PostgreSQL (Summary, Decision, ActionItem, SentimentAnalysis).
    :param meeting_id: UUID de la réunion à analyser.
    """
    logger.info(f"[summary_task] Démarrage pour meeting_id='{meeting_id}'.")
    try:
        meeting_uuid = uuid.UUID(meeting_id)
    except ValueError:
        return {"status": "failed", "error": f"UUID invalide : {meeting_id}"}

    db = SessionLocal()
    try:
        # Récupération de la transcription existante
        transcript = db.query(Transcript).filter(
            Transcript.meeting_id == meeting_uuid
        ).first()

        if not transcript or not transcript.full_text:
            logger.warning(
                f"[summary_task] Aucune transcription disponible pour '{meeting_id}'."
            )
            return {"status": "skipped", "reason": "Aucune transcription disponible."}

        transcript_text = transcript.full_text

        # Génération du résumé NLP
        WebSocketService.publish_meeting_progress(meeting_id, WSEventType.SUMMARY_STARTED, "Génération du résumé NLP", 20)
        summary_gen = SummaryGenerator()
        summary_result = summary_gen.generate(
            meeting_id=meeting_id,
            transcript_text=transcript_text
        )

        # Génération de l'analyse de sentiment
        WebSocketService.publish_meeting_progress(meeting_id, WSEventType.SUMMARY_STARTED, "Analyse de sentiment", 60)
        sentiment_gen = SentimentGenerator()
        sentiment_result = sentiment_gen.generate(
            meeting_id=meeting_id,
            transcript_text=transcript_text
        )

        # Persistance transactionnelle
        WebSocketService.publish_meeting_progress(meeting_id, WSEventType.SUMMARY_STARTED, "Enregistrement du rapport", 85)
        # Nettoyage pour idempotence
        db.query(Summary).filter(Summary.meeting_id == meeting_uuid).delete()
        db.query(Decision).filter(Decision.meeting_id == meeting_uuid).delete()
        db.query(ActionItem).filter(ActionItem.meeting_id == meeting_uuid).delete()
        db.query(SentimentAnalysis).filter(
            SentimentAnalysis.meeting_id == meeting_uuid
        ).delete()
        db.flush()

        # Summary
        db_summary = Summary(
            content=summary_result.summary,
            meeting_id=meeting_uuid
        )
        db.add(db_summary)

        # Decisions
        for decision in summary_result.decisions:
            db.add(Decision(content=decision.content, meeting_id=meeting_uuid))

        # Action Items
        for action in summary_result.action_items:
            db.add(ActionItem(
                description=action.description,
                assignee=action.assignee,
                status=ActionItemStatus.TODO,
                meeting_id=meeting_uuid
            ))

        # Sentiment Analysis
        db.add(SentimentAnalysis(
            sentiment_score=sentiment_result.score,
            label=sentiment_result.label,
            meeting_id=meeting_uuid
        ))

        db.commit()

        logger.info(
            f"[summary_task] Rapport NLP sauvegardé pour '{meeting_id}' — "
            f"{len(summary_result.decisions)} décisions, "
            f"{len(summary_result.action_items)} actions, "
            f"sentiment: {sentiment_result.label}."
        )
        return {
            "status": "success",
            "meeting_id": meeting_id,
            "sentiment": sentiment_result.label,
            "decisions_count": len(summary_result.decisions),
            "actions_count": len(summary_result.action_items),
        }

    except AIException as e:
        db.rollback()
        logger.error(f"[summary_task] Erreur IA pour '{meeting_id}' : {e.message}")
        return {"status": "failed", "error": e.message}
    except Exception as e:
        db.rollback()
        logger.error(f"[summary_task] Erreur inattendue pour '{meeting_id}' : {e}")
        raise self.retry(exc=e)
    finally:
        db.close()
