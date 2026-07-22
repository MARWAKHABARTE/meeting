from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from app.core.settings import settings
from app.core.logger import setup_logging, logger
from app.db import base  # noqa: F401
from app.api.v1.router import api_router


# Initialisation du logging avant de démarrer l'application FastAPI
setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    import asyncio
    from app.websocket import RedisBroadcaster, ConnectionManager
    
    # Log de démarrage de l'application
    logger.info(f"Démarrage de l'application {settings.PROJECT_NAME} en mode {settings.ENVIRONMENT}")
    
    # Démarrage de la diffusion temps réel Redis Pub/Sub
    broadcaster = RedisBroadcaster()
    await broadcaster.start()
    
    # Lancement du Heartbeat des connexions WebSocket
    manager = ConnectionManager()
    heartbeat_task = asyncio.create_task(manager.heartbeat())

    # Initialisation et vérification du stockage objet MinIO au démarrage
    try:
        from app.storage.service import StorageService
        storage_service = StorageService()
        bucket_name = settings.minio_bucket_to_use
        logger.info(f"[Startup] Vérification de la connexion MinIO et présence du bucket '{bucket_name}'...")
        storage_service.create_bucket_if_not_exists(bucket_name)
        logger.info("[Startup] Infrastructure de stockage objet MinIO initialisée avec succès.")
    except Exception as e:
        logger.error(f"[Startup] Échec de la vérification de la connexion MinIO au démarrage : {e}")
        
    yield
    # Log d'arrêt de l'application
    logger.info(f"Arrêt de l'application {settings.PROJECT_NAME}")
    
    # Arrêt de la diffusion temps réel
    await broadcaster.stop()
    heartbeat_task.cancel()
    try:
        await heartbeat_task
    except asyncio.CancelledError:
        pass

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Plateforme web intelligente d'analyse des réunions Skype for Business assistée par IA",
    version="1.0.0",
    lifespan=lifespan,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    # Déclaration du schéma Bearer Auth pour Keycloak
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Saisissez votre token JWT Keycloak (ex: Bearer <token>)"
        }
    }
    # Applique la sécurité globale sur tous les endpoints de l'API (sauf health et root si exclus)
    openapi_schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Configuration de CORS (Cross-Origin Resource Sharing)
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Endpoint de vérification d'état de santé
@app.get("/health", tags=["health"])
def health_check():
    """
    Retourne l'état de fonctionnement de l'API.
    """
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT
    }

# Endpoint racine
@app.get("/", tags=["root"])
def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "docs_url": "/docs",
        "health_check": "/health"
    }

# Inclusion du routeur principal de l'API v1
app.include_router(api_router, prefix=settings.API_V1_STR)

# Instrumentation Prometheus pour FastAPI
try:
    from prometheus_fastapi_instrumentator import Instrumentator
    Instrumentator().instrument(app).expose(app)
except Exception as e:
    logger.warning(f"Impossible d'activer l'instrumentation Prometheus : {e}")

