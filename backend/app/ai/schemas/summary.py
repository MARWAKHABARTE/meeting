from pydantic import BaseModel, Field


class ActionItemSchema(BaseModel):
    """Tâche extraite de la réunion par le LLM."""
    description: str = Field(..., description="Description de l'action à effectuer")
    assignee: str | None = Field(None, description="Personne responsable si identifiée")


class DecisionSchema(BaseModel):
    """Décision prise lors de la réunion."""
    content: str = Field(..., description="Texte de la décision")


class SummaryResult(BaseModel):
    """
    Résultat structuré complet de l'analyse NLP d'une réunion.
    """
    meeting_id: str = Field(..., description="Identifiant de la réunion analysée")
    summary: str = Field(..., description="Résumé global de la réunion")
    decisions: list[DecisionSchema] = Field(default_factory=list, description="Liste des décisions prises")
    action_items: list[ActionItemSchema] = Field(default_factory=list, description="Liste des actions à réaliser")
    participants: list[str] = Field(default_factory=list, description="Liste des participants identifiés")
    topics: list[str] = Field(default_factory=list, description="Principaux sujets abordés")
    key_points: list[str] = Field(default_factory=list, description="Points importants à retenir")
