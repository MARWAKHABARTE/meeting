from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.storage.service import StorageService
from app.storage.client import MinioClientProvider
from app.storage.schemas import UploadResult
from app.core.settings import settings
from app.core.logger import logger
from app.storage.exceptions import StorageException

router = APIRouter()
storage_service = StorageService()

@router.get("/health", response_model=dict)
def check_storage_health():
    """
    Point d'entrée de diagnostic vérifiant la connexion à MinIO
    et l'existence du bucket de configuration par défaut.
    """
    try:
        client = MinioClientProvider.get_client()
        bucket_name = settings.minio_bucket_to_use
        exists = client.bucket_exists(bucket_name)
        if exists:
            return {"status": "healthy"}
        else:
            logger.warn(f"[Storage Health] Le bucket par défaut '{bucket_name}' est introuvable sur le serveur.")
            return {"status": "unhealthy"}
    except Exception as e:
        logger.error(f"[Storage Health] Échec du diagnostic de connexion MinIO : {e}")
        return {"status": "unhealthy"}


@router.post("/upload-test", response_model=UploadResult, status_code=status.HTTP_201_CREATED)
async def upload_test(file: UploadFile = File(...)):
    """
    Point d'entrée de démonstration permettant d'envoyer un fichier dans MinIO
    et de récupérer son URL d'accès pré-signée.
    """
    try:
        # Lecture du contenu binaire
        content = await file.read()
        bucket_name = settings.minio_bucket_to_use
        object_name = file.filename

        # Téléversement de l'objet
        storage_service.upload_file(
            bucket_name=bucket_name,
            object_name=object_name,
            data=content,
            content_type=file.content_type or "application/octet-stream"
        )

        # Génération de l'URL d'accès pré-signée (valide 1 heure)
        url = storage_service.get_file_url(bucket_name, object_name)

        return UploadResult(
            name=object_name,
            size=len(content),
            content_type=file.content_type or "application/octet-stream",
            url=url
        )
    except StorageException as e:
        logger.error(f"[Storage API] Échec de l'upload de test : {e.message}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"[Storage API] Erreur inattendue de l'upload de test : {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur interne lors du traitement : {str(e)}"
        )
