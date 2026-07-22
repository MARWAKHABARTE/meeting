from fastapi import APIRouter
from app.api.v1.endpoints import auth, storage, workers, transcriptions, summaries, rag, websocket

# Routeur principal regroupant tous les sous-modules de l'API v1
api_router = APIRouter()

# Authentification Keycloak
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# Stockage MinIO
api_router.include_router(storage.router, prefix="/storage", tags=["storage"])

# Workers Celery
api_router.include_router(workers.router, prefix="/workers", tags=["workers"])

# Pipeline de transcription IA (Sprint 8)
api_router.include_router(transcriptions.router, prefix="/transcriptions", tags=["transcriptions"])

# Pipeline NLP — Résumés, Décisions, Actions (Sprint 9)
api_router.include_router(summaries.router, prefix="/summaries", tags=["summaries"])

# Pipeline RAG — Recherche sémantique (Sprint 9)
api_router.include_router(rag.router, prefix="/rag", tags=["rag"])

# WebSocket temps réel (Sprint 10)
api_router.include_router(websocket.router, prefix="/ws", tags=["websocket"])
