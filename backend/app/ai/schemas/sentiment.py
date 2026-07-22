from pydantic import BaseModel, Field
from typing import Literal


class SentimentResult(BaseModel):
    """
    Résultat de l'analyse de sentiment d'une réunion.
    """
    meeting_id: str = Field(..., description="Identifiant de la réunion analysée")
    label: Literal["positive", "neutral", "negative"] = Field(
        ..., description="Étiquette de sentiment globale"
    )
    score: float = Field(..., ge=0.0, le=1.0, description="Score de confiance entre 0 et 1")
    explanation: str = Field(..., description="Justification textuelle du sentiment détecté")
