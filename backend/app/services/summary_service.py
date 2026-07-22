"""
Service orchestrant la génération et la récupération des résumés NLP.
Aucune logique IA dans ce service : délégation exclusive aux tâches Celery.
"""
import logging
import uuid
from celery.result import AsyncResult
from app.workers.celery_app import celery_app
from app.workers.tasks.report import summary_task
from app.workers.tasks.embeddings import embedding_task
from app.db.session import SessionLocal
from app.models.meeting import Meeting
from app.models.summary import Summary
from app.models.decision import Decision
from app.models.action_item import ActionItem
from app.models.sentiment_analysis import SentimentAnalysis

logger = logging.getLogger("meeting_ai")


class SummaryService:
    """
    Service de gestion du pipeline NLP.
    Responsable de la soumission des tâches Celery et de la récupération des résultats.
    """

    def start_summary(self, meeting_id: str) -> dict:
        """
        Soumet en parallèle les tâches de génération de résumé NLP et d'indexation.
        :param meeting_id: UUID de la réunion.
        :return: Dict contenant les task_ids des deux tâches lancées.
        """
        logger.info(f"[SummaryService] Déclenchement du pipeline NLP pour '{meeting_id}'.")
        summary_t = summary_task.delay(meeting_id)
        embedding_t = embedding_task.delay(meeting_id)

        return {
            "summary_task_id": summary_t.id,
            "embedding_task_id": embedding_t.id,
            "status": "queued",
        }

    def get_task_status(self, task_id: str) -> str:
        """Interroge le statut d'une tâche Celery."""
        result = AsyncResult(task_id, app=celery_app)
        return result.state

    def get_summary(self, meeting_id: str) -> dict | None:
        """
        Récupère le rapport NLP complet depuis PostgreSQL.
        :param meeting_id: UUID de la réunion.
        :return: Dictionnaire complet ou None si pas encore disponible.
        """
        db = SessionLocal()
        try:
            m_uuid = uuid.UUID(meeting_id)
            summary = db.query(Summary).filter(Summary.meeting_id == m_uuid).first()
            if not summary:
                return None

            decisions = db.query(Decision).filter(
                Decision.meeting_id == m_uuid
            ).all()
            actions = db.query(ActionItem).filter(
                ActionItem.meeting_id == m_uuid
            ).all()
            sentiments = db.query(SentimentAnalysis).filter(
                SentimentAnalysis.meeting_id == m_uuid
            ).all()

            logger.info(
                f"[SummaryService] Rapport récupéré pour '{meeting_id}' — "
                f"{len(decisions)} décisions, {len(actions)} actions."
            )
            return {
                "meeting_id": meeting_id,
                "summary": summary.content,
                "decisions": [d.content for d in decisions],
                "action_items": [
                    {"description": a.description, "assignee": a.assignee, "status": a.status}
                    for a in actions
                ],
                "sentiment": {
                    "label": sentiments[0].label,
                    "score": sentiments[0].sentiment_score,
                } if sentiments else None,
            }
        finally:
            db.close()
