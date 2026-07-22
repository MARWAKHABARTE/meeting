from pydantic import BaseModel, Field

class TranscriptionSegment(BaseModel):
    """
    Segment individuel retourné par Whisper lors de la transcription.
    """
    start: float = Field(..., description="Timestamp de début de parole en secondes")
    end: float = Field(..., description="Timestamp de fin de parole en secondes")
    text: str = Field(..., description="Contenu textuel transcrit")
    confidence: float | None = Field(None, description="Score de confiance locale du décodeur")


class TranscriptionResult(BaseModel):
    """
    Résultat complet de la transcription brute générée par Whisper.
    """
    text: str = Field(..., description="Transcription intégrale mise bout à bout")
    language: str = Field(..., description="Code langue détecté ou forcé (ex: fr, en)")
    duration: float = Field(..., description="Durée totale analysée en secondes")
    segments: list[TranscriptionSegment] = Field(default_factory=list, description="Segments temporels de texte")
    confidence: float | None = Field(None, description="Confiance globale moyenne")


class MergedSegment(BaseModel):
    """
    Segment fusionné final alliant la transcription de Whisper et la diarisation de Pyannote.
    """
    speaker: str = Field(..., description="Identifiant du locuteur (ex: Speaker 1)")
    start: float = Field(..., description="Timestamp de début du segment en secondes")
    end: float = Field(..., description="Timestamp de fin du segment en secondes")
    text: str = Field(..., description="Texte transcrit prononcé par cet intervenant")
    confidence: float | None = Field(None, description="Score de confiance du segment")


class PipelineResult(BaseModel):
    """
    Résultat consolidé final du pipeline de traitement IA.
    C'est cet objet qui est sauvegardé en base de données et exposé par l'API.
    """
    full_text: str = Field(..., description="Texte complet consolidé de la réunion")
    language: str = Field(..., description="Langue principale détectée de la réunion")
    duration: float = Field(..., description="Durée totale traitée de la réunion en secondes")
    segments: list[MergedSegment] = Field(default_factory=list, description="Liste des segments textuels par intervenant")
