import io
from datetime import timedelta
from minio.error import S3Error
from app.storage.client import MinioClientProvider
from app.storage.exceptions import (
    BucketNotFoundException,
    UploadFailedException,
    DownloadFailedException,
    StorageException
)
from app.storage.schemas import StorageObject
from app.core.logger import logger

class StorageService:
    """
    Service orienté objet générique pour interagir avec le stockage d'objets MinIO.
    Totalement indépendant de la logique métier (ni réunion, ni rapport, ni transcription).
    """

    def __init__(self):
        # Instance de client résolue dynamiquement via une property (lazy-loading)
        self._client = None

    @property
    def client(self):
        """
        Résout dynamiquement et de manière unique le client Minio singleton.
        """
        if self._client is None:
            self._client = MinioClientProvider.get_client()
        return self._client

    def create_bucket_if_not_exists(self, bucket_name: str) -> None:
        """
        Crée un bucket de stockage s'il n'existe pas déjà.
        
        :param bucket_name: Le nom du bucket à valider/créer
        :raises StorageException: En cas d'erreur de communication S3
        """
        try:
            if not self.client.bucket_exists(bucket_name):
                logger.info(f"Le bucket '{bucket_name}' n'existe pas. Création automatique...")
                self.client.make_bucket(bucket_name)
                logger.info(f"Le bucket '{bucket_name}' a été créé avec succès.")
            else:
                logger.debug(f"Le bucket '{bucket_name}' existe déjà.")
        except Exception as e:
            logger.error(f"Erreur lors de la création ou vérification du bucket '{bucket_name}' : {e}")
            raise StorageException(f"Impossible de valider ou créer le bucket '{bucket_name}' : {e}")

    def upload_file(self, bucket_name: str, object_name: str, data: bytes, content_type: str) -> int:
        """
        Téléverse le contenu binaire d'un fichier dans le bucket MinIO.
        
        :param bucket_name: Nom du bucket cible
        :param object_name: Nom unique de l'objet (clé)
        :param data: Contenu binaire brut sous forme de bytes
        :param content_type: Type MIME du fichier (ex: image/png, audio/mpeg)
        :raises BucketNotFoundException: Si le bucket cible n'existe pas
        :raises UploadFailedException: Si le téléversement échoue
        :return: Nombre d'octets téléversés
        """
        self.create_bucket_if_not_exists(bucket_name)
        data_stream = io.BytesIO(data)
        try:
            result = self.client.put_object(
                bucket_name=bucket_name,
                object_name=object_name,
                data=data_stream,
                length=len(data),
                content_type=content_type
            )
            logger.info(
                f"Fichier '{object_name}' ({len(data)} octets) téléversé dans le bucket '{bucket_name}'. "
                f"Etag: {result.etag}"
            )
            return len(data)
        except S3Error as e:
            if e.code == "NoSuchBucket":
                raise BucketNotFoundException(bucket_name)
            raise UploadFailedException(object_name, f"Code S3 : {e.code} - {e.message}")
        except Exception as e:
            raise UploadFailedException(object_name, str(e))

    def download_file(self, bucket_name: str, object_name: str) -> bytes:
        """
        Télécharge le contenu binaire d'un objet depuis le bucket MinIO.
        
        :param bucket_name: Nom du bucket source
        :param object_name: Nom de l'objet à télécharger
        :raises BucketNotFoundException: Si le bucket n'existe pas
        :raises DownloadFailedException: Si l'objet n'existe pas ou si le téléchargement échoue
        :return: Le contenu brut du fichier sous forme de bytes
        """
        try:
            response = self.client.get_object(bucket_name, object_name)
            try:
                return response.read()
            finally:
                response.close()
                response.release_conn()
        except S3Error as e:
            if e.code == "NoSuchBucket":
                raise BucketNotFoundException(bucket_name)
            if e.code == "NoSuchKey":
                raise DownloadFailedException(object_name, "L'objet demandé n'existe pas (NoSuchKey).")
            raise DownloadFailedException(object_name, f"Code S3 : {e.code} - {e.message}")
        except Exception as e:
            raise DownloadFailedException(object_name, str(e))

    def delete_file(self, bucket_name: str, object_name: str) -> None:
        """
        Supprime un objet du stockage.
        
        :param bucket_name: Nom du bucket
        :param object_name: Clé de l'objet à supprimer
        :raises BucketNotFoundException: Si le bucket n'existe pas
        :raises StorageException: En cas de panne de suppression
        """
        try:
            self.client.remove_object(bucket_name, object_name)
            logger.info(f"Objet '{object_name}' supprimé avec succès du bucket '{bucket_name}'.")
        except S3Error as e:
            if e.code == "NoSuchBucket":
                raise BucketNotFoundException(bucket_name)
            raise StorageException(f"Impossible de supprimer l'objet '{object_name}' (S3 Error: {e.message})")
        except Exception as e:
            raise StorageException(f"Erreur inattendue lors de la suppression de '{object_name}' : {e}")

    def file_exists(self, bucket_name: str, object_name: str) -> bool:
        """
        Vérifie la présence d'un objet dans le bucket en lisant ses métadonnées.
        
        :param bucket_name: Nom du bucket
        :param object_name: Clé de l'objet
        :return: True si le fichier existe, False sinon
        """
        try:
            self.client.stat_object(bucket_name, object_name)
            return True
        except S3Error as e:
            if e.code in ("NoSuchKey", "NoSuchBucket"):
                return False
            raise StorageException(f"Erreur de diagnostic de l'objet '{object_name}' (S3 Error: {e.message})")
        except Exception as e:
            raise StorageException(f"Erreur de diagnostic de l'objet '{object_name}' : {e}")

    def list_files(self, bucket_name: str, prefix: str = None) -> list[StorageObject]:
        """
        Liste les fichiers présents dans un bucket, avec un filtre par préfixe optionnel.
        
        :param bucket_name: Nom du bucket
        :param prefix: Filtre de dossier/préfixe
        :raises BucketNotFoundException: Si le bucket n'existe pas
        :return: Liste de StorageObject contenant les métadonnées de chaque fichier
        """
        try:
            objects = self.client.list_objects(bucket_name, prefix=prefix, recursive=True)
            result = []
            for obj in objects:
                result.append(StorageObject(
                    name=obj.object_name,
                    size=obj.size,
                    content_type=obj.content_type or "application/octet-stream",
                    last_modified=obj.last_modified
                ))
            return result
        except S3Error as e:
            if e.code == "NoSuchBucket":
                raise BucketNotFoundException(bucket_name)
            raise StorageException(f"Impossible de lister le contenu du bucket '{bucket_name}' : {e.message}")
        except Exception as e:
            raise StorageException(f"Échec de listing des objets pour le bucket '{bucket_name}' : {e}")

    def get_file_url(self, bucket_name: str, object_name: str, expires_in_seconds: int = 3600) -> str:
        """
        Génère une URL pré-signée temporaire pour télécharger ou lire directement l'objet.
        
        :param bucket_name: Nom du bucket
        :param object_name: Clé de l'objet
        :param expires_in_seconds: Durée de validité de l'URL pré-signée
        :raises BucketNotFoundException: Si le bucket n'existe pas
        :return: URL complète signée cryptographiquement
        """
        try:
            return self.client.presigned_get_object(
                bucket_name,
                object_name,
                expires=timedelta(seconds=expires_in_seconds)
            )
        except S3Error as e:
            if e.code == "NoSuchBucket":
                raise BucketNotFoundException(bucket_name)
            raise StorageException(f"Erreur de génération d'URL d'accès pour '{object_name}' : {e.message}")
        except Exception as e:
            raise StorageException(f"Échec de génération de l'URL pré-signée pour '{object_name}' : {e}")
