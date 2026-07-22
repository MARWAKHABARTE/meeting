from pydantic import BaseModel, Field
from datetime import datetime

class StorageObject(BaseModel):
    """
    Modèle représentant les métadonnées d'un objet stocké.
    """
    name: str = Field(..., description="Nom unique de l'objet dans le bucket (chemin d'accès relatif)")
    size: int = Field(..., description="Taille du fichier en octets")
    content_type: str = Field(..., description="Type de contenu MIME (ex: audio/mpeg)")
    last_modified: datetime = Field(..., description="Horodatage de la dernière modification de l'objet")


class UploadResult(BaseModel):
    """
    Modèle retourné suite à un téléversement réussi.
    """
    name: str = Field(..., description="Nom de l'objet créé sur le serveur")
    size: int = Field(..., description="Taille de l'objet en octets")
    content_type: str = Field(..., description="Type de contenu MIME")
    url: str = Field(..., description="URL temporaire pré-signée pour l'accès direct en lecture")


class DownloadResult(BaseModel):
    """
    Modèle encapsulant les métadonnées de téléchargement.
    Les données binaires brutes sont transférées indépendamment.
    """
    name: str = Field(..., description="Nom de l'objet téléchargé")
    content_type: str = Field(..., description="Type de contenu MIME")
    size: int = Field(..., description="Taille en octets")
