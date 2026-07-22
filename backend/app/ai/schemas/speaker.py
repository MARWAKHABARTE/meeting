from pydantic import BaseModel, Field

class SpeakerSegment(BaseModel):
    """
    Représente un segment vocal attribué à un intervenant spécifique.
    """
    speaker: str = Field(..., description="Identifiant ou nom du locuteur (ex: Speaker 1)")
    start: float = Field(..., description="Timestamp de début de parole en secondes")
    end: float = Field(..., description="Timestamp de fin de parole en secondes")
    duration: float = Field(..., description="Durée de parole en secondes")
    confidence: float | None = Field(None, description="Score de confiance ou de probabilité du modèle")


class DiarizationResult(BaseModel):
    """
    Résultat complet retourné par le pipeline de diarisation Pyannote.
    """
    segments: list[SpeakerSegment] = Field(default_factory=list, description="Liste des segments vocaux identifiés")
