import os
import tempfile
import logging
from contextlib import contextmanager
from app.storage.service import StorageService
from app.storage.exceptions import StorageException as SystemStorageException
from app.ai.exceptions import AudioNotFoundException, StorageException
from app.core.settings import settings

logger = logging.getLogger("meeting_ai")

class AudioLoader:
    """
    Gestionnaire d'accès et de rapatriement des fichiers audio depuis MinIO.
    Fournit un fichier local temporaire utilisable par Whisper / Pyannote,
    et garantit sa suppression du disque après utilisation.
    """

    def __init__(self):
        self._storage_service = StorageService()

    @contextmanager
    def load_audio(self, bucket_name: str, object_name: str):
        """
        Télécharge temporairement un fichier audio depuis MinIO.
        Garantit la suppression du fichier à la fin de la lecture du bloc.
        
        :param bucket_name: Nom du bucket MinIO.
        :param object_name: Nom unique/chemin de l'objet audio.
        :yield: Chemin d'accès local temporaire vers le fichier audio.
        :raises AudioNotFoundException: Si l'objet n'existe pas.
        :raises StorageException: En cas d'erreur réseau ou d'accès S3.
        """
        # 1. Vérification d'existence
        try:
            if not self._storage_service.file_exists(bucket_name, object_name):
                raise AudioNotFoundException(
                    object_name, 
                    f"Le fichier n'a pas été trouvé dans le bucket '{bucket_name}'."
                )
        except SystemStorageException as e:
            raise StorageException(f"Erreur de communication MinIO : {e.message}")
        except AudioNotFoundException:
            raise
        except Exception as e:
            raise StorageException(f"Échec de diagnostic d'accès au fichier : {str(e)}")

        # 2. Résolution du dossier temporaire
        temp_dir = settings.AI_TEMP_DIRECTORY
        os.makedirs(temp_dir, exist_ok=True)

        # 3. Création du fichier temporaire avec extension d'origine (très important pour ffmpeg / librosa)
        _, ext = os.path.splitext(object_name)
        temp_file = tempfile.NamedTemporaryFile(dir=temp_dir, suffix=ext, delete=False)
        temp_file_path = temp_file.name
        temp_file.close()

        logger.info(
            f"[Audio Loader] Téléchargement de '{object_name}' (bucket: '{bucket_name}') "
            f"vers le fichier temporaire local '{temp_file_path}'..."
        )

        try:
            # 4. Rapatriement du flux binaire
            data = self._storage_service.download_file(bucket_name, object_name)
            with open(temp_file_path, "wb") as f:
                f.write(data)
                
            logger.info(f"[Audio Loader] Fichier audio rapatrié avec succès ({len(data)} octets).")
            
            # Transfert de contrôle à la pipeline appelante
            yield temp_file_path

        except SystemStorageException as e:
            logger.error(f"[Audio Loader] Échec de téléchargement S3 de '{object_name}' : {e.message}")
            raise StorageException(f"Erreur de téléchargement MinIO : {e.message}")
        except Exception as e:
            logger.error(f"[Audio Loader] Échec de traitement du fichier temporaire : {e}")
            raise StorageException(f"Erreur interne de gestion du fichier temporaire : {str(e)}")
        finally:
            # 5. Nettoyage systématique et garanti du fichier temporaire
            if os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                    logger.info(f"[Audio Loader] Fichier temporaire '{temp_file_path}' supprimé.")
                except Exception as e:
                    logger.error(f"[Audio Loader] Impossible de supprimer le fichier '{temp_file_path}' : {e}")
