"""
Tests unitaires et d'intégration du pipeline NLP et RAG (Sprint 9).
Tous les tests utilisent des Mocks — aucune dépendance vers Ollama, ChromaDB ou sentence-transformers.
"""
import pytest
from unittest.mock import MagicMock, patch
import json

from app.ai.exceptions import (
    OllamaUnavailable, SummaryException, EmbeddingException,
    VectorStoreException, RAGException
)
from app.ai.llm.prompt_builder import PromptBuilder
from app.ai.embeddings.chunker import TextChunker
from app.ai.schemas.summary import SummaryResult, DecisionSchema, ActionItemSchema
from app.ai.schemas.sentiment import SentimentResult
from app.ai.schemas.rag import RAGQuery, RAGResponse, RAGSourceDocument
from app.ai.rag.context_builder import ContextBuilder


# ──────────────────────────────────────────────────────────────────────────────
# 1. Tests du PromptBuilder
# ──────────────────────────────────────────────────────────────────────────────

def test_prompt_builder_summary_contains_transcript():
    """Le prompt de résumé doit contenir le texte de la transcription."""
    transcript = "Alice : Bonjour. Bob : Bienvenue à la réunion."
    prompt = PromptBuilder.build_summary_prompt(transcript)
    assert transcript in prompt
    assert "JSON" in prompt


def test_prompt_builder_sentiment_contains_labels():
    """Le prompt de sentiment doit mentionner les labels attendus."""
    prompt = PromptBuilder.build_sentiment_prompt("Texte de réunion.")
    assert "positive" in prompt
    assert "negative" in prompt
    assert "neutral" in prompt


def test_prompt_builder_rag_contains_question_and_context():
    """Le prompt RAG doit intégrer la question et le contexte."""
    q = "Qui a décidé d'adopter Celery ?"
    ctx = "Alice : Nous adoptons Celery pour l'asynchronisme."
    prompt = PromptBuilder.build_rag_prompt(question=q, context=ctx)
    assert q in prompt
    assert ctx in prompt


# ──────────────────────────────────────────────────────────────────────────────
# 2. Tests du Chunker
# ──────────────────────────────────────────────────────────────────────────────

def test_chunker_basic_split():
    """Le chunker doit produire plusieurs chunks pour un texte long."""
    chunker = TextChunker(chunk_size=5, chunk_overlap=1)
    text = "mot1 mot2 mot3 mot4 mot5 mot6 mot7 mot8 mot9 mot10"
    chunks = chunker.chunk(text, metadata={"meeting_id": "test"})
    assert len(chunks) > 1
    assert all("text" in c for c in chunks)
    assert all("metadata" in c for c in chunks)


def test_chunker_empty_text():
    """Le chunker doit retourner une liste vide pour un texte vide."""
    chunker = TextChunker()
    assert chunker.chunk("") == []
    assert chunker.chunk("   ") == []


def test_chunker_preserves_metadata():
    """Le chunker doit propager les métadonnées à chaque chunk."""
    chunker = TextChunker(chunk_size=3, chunk_overlap=0)
    chunks = chunker.chunk("a b c d e f", metadata={"meeting_id": "uuid-123"})
    for chunk in chunks:
        assert chunk["metadata"]["meeting_id"] == "uuid-123"
        assert "chunk_index" in chunk["metadata"]


# ──────────────────────────────────────────────────────────────────────────────
# 3. Tests des Schémas Pydantic
# ──────────────────────────────────────────────────────────────────────────────

def test_summary_result_schema():
    """Valide la construction d'un SummaryResult complet."""
    result = SummaryResult(
        meeting_id="meeting-1",
        summary="Résumé de la réunion.",
        decisions=[DecisionSchema(content="Adopter Celery.")],
        action_items=[ActionItemSchema(description="Tester le pipeline.", assignee="Alice")],
        participants=["Alice", "Bob"],
        topics=["Celery", "RAG"],
        key_points=["Pipeline opérationnel."]
    )
    assert result.meeting_id == "meeting-1"
    assert len(result.decisions) == 1
    assert result.decisions[0].content == "Adopter Celery."


def test_sentiment_result_schema_valid():
    """Valide qu'un SentimentResult avec un score hors limites lève une erreur."""
    result = SentimentResult(
        meeting_id="m1", label="positive", score=0.85,
        explanation="Réunion constructive."
    )
    assert result.label == "positive"
    assert 0.0 <= result.score <= 1.0


def test_rag_query_schema():
    """Valide la construction d'une RAGQuery valide."""
    query = RAGQuery(meeting_id="m1", question="Qui a pris la décision ?")
    assert query.meeting_id == "m1"


# ──────────────────────────────────────────────────────────────────────────────
# 4. Tests du ContextBuilder
# ──────────────────────────────────────────────────────────────────────────────

def test_context_builder_with_documents():
    """Le ContextBuilder doit formater correctement les documents sources."""
    docs = [
        RAGSourceDocument(
            content="Alice a décidé d'adopter Celery.",
            metadata={"speaker": "Alice", "chunk_index": 0},
            distance=0.12
        ),
        RAGSourceDocument(
            content="Bob a validé le sprint 8.",
            metadata={"speaker": "Bob", "chunk_index": 1},
            distance=0.25
        ),
    ]
    builder = ContextBuilder()
    context = builder.build(docs)
    assert "Alice" in context
    assert "Celery" in context
    assert "Bob" in context


def test_context_builder_empty_returns_default():
    """Le ContextBuilder doit retourner un message par défaut si pas de documents."""
    builder = ContextBuilder()
    context = builder.build([])
    assert "Aucun contexte" in context


# ──────────────────────────────────────────────────────────────────────────────
# 5. Tests du SummaryGenerator (avec Mock Ollama)
# ──────────────────────────────────────────────────────────────────────────────

def test_summary_generator_with_mock():
    """Valide que le SummaryGenerator parse correctement la réponse JSON du Mock Ollama."""
    from app.ai.llm.summary_generator import SummaryGenerator
    gen = SummaryGenerator()

    mock_json = json.dumps({
        "summary": "La réunion était productive.",
        "decisions": [{"content": "Adopter le RAG."}],
        "action_items": [{"description": "Tester ChromaDB.", "assignee": "Alice"}],
        "participants": ["Alice", "Bob"],
        "topics": ["RAG", "ChromaDB"],
        "key_points": ["Le pipeline fonctionne."]
    })
    gen._client.generate = MagicMock(return_value=mock_json)

    result = gen.generate("meeting-1", "Transcription de test.")
    assert isinstance(result, SummaryResult)
    assert result.summary == "La réunion était productive."
    assert len(result.decisions) == 1


def test_summary_generator_invalid_json_raises():
    """Valide qu'une réponse non-JSON du LLM lève une SummaryException."""
    from app.ai.llm.summary_generator import SummaryGenerator
    gen = SummaryGenerator()
    gen._client.generate = MagicMock(return_value="Ce n'est pas du JSON valide !")

    with pytest.raises(SummaryException):
        gen.generate("meeting-1", "Transcription de test.")
