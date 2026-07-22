class StorageException(Exception):
    """
    Exception de base pour toutes les erreurs liées au stockage objet.
    """
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class BucketNotFoundException(StorageException):
    """
    Exception levée lorsque le bucket spécifié n'existe pas.
    """
    def __init__(self, bucket_name: str):
        super().__init__(f"Le bucket '{bucket_name}' n'a pas été trouvé sur le serveur MinIO.")
        self.bucket_name = bucket_name


class UploadFailedException(StorageException):
    """
    Exception levée lors de l'échec de téléversement d'un objet.
    """
    def __init__(self, object_name: str, details: str = ""):
        super().__init__(f"Le téléversement de l'objet '{object_name}' a échoué. {details}".strip())
        self.object_name = object_name
        self.details = details


class DownloadFailedException(StorageException):
    """
    Exception levée lors de l'échec de téléchargement ou récupération d'un objet.
    """
    def __init__(self, object_name: str, details: str = ""):
        super().__init__(f"La récupération de l'objet '{object_name}' a échoué. {details}".strip())
        self.object_name = object_name
        self.details = details
