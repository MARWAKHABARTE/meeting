"""
Tâche Celery de génération des embeddings et d'indexation dans ChromaDB.
Orchestre : transcription PostgreSQL → Chunking → Vectorisation → ChromaDB.
"""
import logging
import uuid
from app.workers.celery_app import celery_app
from app.db.session import SessionLocal
from app.models.transcript import Transcript
from app.ai.embeddings.chunker import TextChunker
from app.ai.embeddings.vector_store import VectorStore
from app.ai.exceptions import AIException
from app.core.settings import settings
from app.services.websocket_service import WebSocketService
from app.websocket.events import WSEventType

logger = logging.getLogger("meeting_ai")


@celery_app.task(
    name="workers.embedding_task",
    bind=True,
    max_retries=3,
    default_retry_delay=30,
)
def embedding_task(self, meeting_id: str) -> dict:
    """
    Génère les embeddings de la réunion et les indexe dans ChromaDB.
    La collection est nommée '{VECTOR_COLLECTION}_{meeting_id}' pour isoler les données.
    :param meeting_id: UUID de la réunion à vectoriser.
    """
    logger.info(f"[embedding_task] Démarrage pour meeting_id='{meeting_id}'.")

    try:
        meeting_uuid = uuid.UUID(meeting_id)
    except ValueError:
        return {"status": "failed", "error": f"UUID invalide : {meeting_id}"}

    db = SessionLocal()
    try:
        # Récupération de la transcription existante depuis PostgreSQL
        transcript = db.query(Transcript).filter(
            Transcript.meeting_id == meeting_uuid
        ).first()

        if not transcript or not transcript.full_text:
            logger.warning(
                f"[embedding_task] Aucune transcription disponible pour '{meeting_id}'."
            )
            return {"status": "skipped", "reason": "Aucune transcription disponible."}

        text = transcript.full_text

    finally:
        db.close()

    # Découpage du texte en chunks
    WebSocketService.publish_meeting_progress(meeting_id, WSEventType.EMBEDDING_STARTED, "Découpage du texte", 25)
    chunker = TextChunker()
    chunks = chunker.chunk(text, metadata={"meeting_id": meeting_id})

    if not chunks:
        logger.warning(f"[embedding_task] Aucun chunk généré pour '{meeting_id}'.")
        return {"status": "skipped", "reason": "Texte vide — aucun chunk généré."}

    # Construction des listes pour ChromaDB
    ids = [f"{meeting_id}_chunk_{c['metadata']['chunk_index']}" for c in chunks]
    documents = [c["text"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]

    # Indexation dans ChromaDB
    WebSocketService.publish_meeting_progress(meeting_id, WSEventType.EMBEDDING_STARTED, "Indexation ChromaDB", 75)
    collection_name = f"{settings.VECTOR_COLLECTION}_{meeting_id}"
    vector_store = VectorStore()

    # Réinitialisation de la collection pour idempotence
    try:
        vector_store.delete_collection(collection_name)
    except Exception:
        pass  # La collection n'existait pas encore

    vector_store.upsert_documents(
        collection_name=collection_name,
        ids=ids,
        documents=documents,
        metadatas=metadatas,
    )

    logger.info(
        f"[embedding_task] {len(chunks)} chunks indexés dans la collection "
        f"'{collection_name}'."
    )
    return {
        "status": "success",
        "meeting_id": meeting_id,
        "chunks_indexed": len(chunks),
        "collection": collection_name,
    }
