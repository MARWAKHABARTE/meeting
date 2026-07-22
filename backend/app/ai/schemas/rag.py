from pydantic import BaseModel, Field


class RAGQuery(BaseModel):
    """
    Requête utilisateur en langage naturel adressée au pipeline RAG.
    """
    meeting_id: str = Field(..., description="Identifiant de la réunion à interroger")
    question: str = Field(..., min_length=3, description="Question en langage naturel")


class RAGSourceDocument(BaseModel):
    """
    Document source récupéré depuis ChromaDB pour alimenter le contexte.
    """
    content: str = Field(..., description="Extrait de texte pertinent")
    metadata: dict = Field(default_factory=dict, description="Métadonnées du document source")
    distance: float | None = Field(None, description="Distance cosine par rapport à la requête")


class RAGResponse(BaseModel):
    """
    Réponse finale du pipeline RAG enrichie des sources utilisées.
    """
    meeting_id: str = Field(..., description="Identifiant de la réunion interrogée")
    question: str = Field(..., description="Question originale de l'utilisateur")
    answer: str = Field(..., description="Réponse générée par le LLM à partir du contexte")
    sources: list[RAGSourceDocument] = Field(
        default_factory=list,
        description="Liste des documents récupérés utilisés pour générer la réponse"
    )
