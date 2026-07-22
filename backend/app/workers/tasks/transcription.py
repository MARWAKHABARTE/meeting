"""
Tâche Celery de production orchestrant l'intégralité du pipeline d'analyse IA.
Téléchargement S3 -> Whisper -> Pyannote -> Alignement/Fusion -> Persistance SQL.
"""
import logging
import uuid
import time
from app.workers.celery_app import celery_app
from app.db.session import SessionLocal
from app.models.meeting import Meeting, MeetingStatus
from app.models.transcript import Transcript
from app.models.speaker import Speaker
from app.models.transcript_segment import TranscriptSegment

from app.ai import AudioLoader
from app.ai.pipeline.transcription_pipeline import TranscriptionPipeline
from app.ai.pipeline.diarization_pipeline import DiarizationPipeline
from app.ai.pipeline.merge_pipeline import MergePipeline
from app.ai.exceptions import AIException
from app.services.websocket_service import WebSocketService
from app.websocket.events import WSEventType

logger = logging.getLogger("meeting_ai")


@celery_app.task(
    name="workers.transcription_task",
    bind=True,
    max_retries=3,
    default_retry_delay=30,
)
def transcription_task(
    self,
    meeting_id: str,
    bucket_name: str,
    object_name: str,
) -> dict:
    """
    Orchestre le traitement de la réunion :
    1. Récupère le fichier audio depuis MinIO.
    2. Lance la transcription Whisper.
    3. Lance la diarisation Pyannote.
    4. Fusionne les timelines de locuteurs et de paroles.
    5. Enregistre les intervenants, le transcript et les segments en base de données.
    6. Met à jour le statut de la réunion.
    """
    logger.info(
        f"[Celery Worker] Début du traitement asynchrone pour meeting_id='{meeting_id}' "
        f"(bucket: '{bucket_name}', object: '{object_name}')."
    )
    start_time = time.time()

    # Résolution des UUIDs
    try:
        meeting_uuid = uuid.UUID(meeting_id)
    except ValueError as e:
        logger.error(f"[Celery Worker] ID de réunion invalide : {meeting_id}")
        return {"status": "failed", "error": f"ID de réunion '{meeting_id}' invalide."}

    # 1. Vérification de l'existence de la réunion et mise en traitement
    db = SessionLocal()
    try:
        meeting = db.query(Meeting).filter(Meeting.id == meeting_uuid).first()
        if not meeting:
            logger.error(f"[Celery Worker] Réunion introuvable en base : {meeting_id}")
            return {"status": "failed", "error": f"Réunion '{meeting_id}' introuvable."}

        # Transition de statut
        meeting.status = MeetingStatus.PROCESSING
        db.commit()
    except Exception as e:
        db.close()
        logger.error(f"[Celery Worker] Échec de la mise à jour initiale de la réunion : {e}")
        raise self.retry(exc=e)

    # 2. Exécution du pipeline IA
    try:
        audio_loader = AudioLoader()
        t_pipeline = TranscriptionPipeline()
        d_pipeline = DiarizationPipeline()
        m_pipeline = MergePipeline()

        # Rapatriement audio avec auto-suppression
        WebSocketService.publish_meeting_progress(meeting_id, WSEventType.TRANSCRIPTION_PROGRESS, "Chargement audio", 10)
        with audio_loader.load_audio(bucket_name, object_name) as local_audio_path:
            # Transcription brute
            WebSocketService.publish_meeting_progress(meeting_id, WSEventType.TRANSCRIPTION_PROGRESS, "Transcription audio (Whisper)", 25)
            trans_res = t_pipeline.run(local_audio_path)
            
            # Diarisation
            WebSocketService.publish_meeting_progress(meeting_id, WSEventType.TRANSCRIPTION_PROGRESS, "Segmentation des locuteurs (Pyannote)", 60)
            diar_res = d_pipeline.run(local_audio_path)
            
            # Fusion
            WebSocketService.publish_meeting_progress(meeting_id, WSEventType.TRANSCRIPTION_PROGRESS, "Fusion & Consolidation", 85)
            pipeline_result = m_pipeline.run(trans_res, diar_res)

        # 3. Persistance transactionnelle
        WebSocketService.publish_meeting_progress(meeting_id, WSEventType.TRANSCRIPTION_PROGRESS, "Sauvegarde en base de données", 95)
        logger.info(f"[Celery Worker] Enregistrement du transcript consolidé pour meeting_id='{meeting_id}'...")

        # Nettoyage des anciennes données associées pour assurer l'idempotence
        db.query(Transcript).filter(Transcript.meeting_id == meeting_uuid).delete()
        db.query(Speaker).filter(Speaker.meeting_id == meeting_uuid).delete()
        db.flush()

        # Enregistrement des locuteurs uniques détectés
        speaker_map = {}
        for seg in pipeline_result.segments:
            sp_name = seg.speaker
            if sp_name not in speaker_map:
                db_speaker = Speaker(
                    name=sp_name,
                    meeting_id=meeting_uuid
                )
                db.add(db_speaker)
                db.flush()  # Génération de l'UUID speaker
                speaker_map[sp_name] = db_speaker.id

        # Enregistrement du Transcript global
        db_transcript = Transcript(
            full_text=pipeline_result.full_text,
            meeting_id=meeting_uuid
        )
        db.add(db_transcript)
        db.flush()  # Génération de l'UUID transcript

        # Enregistrement de chaque segment temporel lié
        for seg in pipeline_result.segments:
            db_segment = TranscriptSegment(
                start_time=seg.start,
                end_time=seg.end,
                text=seg.text,
                transcript_id=db_transcript.id,
                speaker_id=speaker_map.get(seg.speaker),
                meeting_id=meeting_uuid
            )
            db.add(db_segment)

        # Mise à jour finale du statut de la réunion
        meeting.status = MeetingStatus.COMPLETED
        db.commit()

        total_duration = time.time() - start_time
        logger.info(
            f"[Celery Worker] Traitement terminé avec succès pour meeting_id='{meeting_id}' "
            f"en {total_duration:.2f}s."
        )

        return {
            "status": "success",
            "meeting_id": meeting_id,
            "duration_seconds": total_duration,
            "language": pipeline_result.language,
        }

    except AIException as e:
        logger.error(f"[Celery Worker] Échec contrôlé de la tâche IA : {e.message}")
        db.rollback()
        try:
            meeting.status = MeetingStatus.FAILED
            db.commit()
        except Exception:
            pass
        return {"status": "failed", "error": e.message}
        
    except Exception as e:
        logger.error(f"[Celery Worker] Erreur non gérée dans la tâche Celery : {e}")
        db.rollback()
        try:
            meeting.status = MeetingStatus.FAILED
            db.commit()
        except Exception:
            pass
        # Permet à Celery de gérer les retry sur erreur inattendue
        raise self.retry(exc=e)
    finally:
        db.close()
