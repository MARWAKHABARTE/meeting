"""
Tests IA — Pipeline RAG et VectorStore.
Vérifie les services RAG, VectorStore et l'intégration Ollama en mode mock.
"""
import pytest
from unittest.mock import patch, MagicMock


class TestRAGService:
    """Tests du service RAG (Retrieval Augmented Generation)."""

    def test_rag_service_is_importable(self):
        """RAGService doit être importable sans erreur."""
        from app.services.rag_service import RAGService
        service = RAGService()
        assert service is not None

    @patch("app.ai.embeddings.vector_store.VectorStore.search")
    @patch("app.ai.llm.ollama_client.OllamaClient.generate")
    def test_rag_query_returns_answer(self, mock_generate, mock_search):
        """RAGService.query() doit retourner une réponse avec 'answer' et 'sources'."""
        mock_search.return_value = [
            {"content": "Le projet a été validé.", "metadata": {"meeting_id": "test"}, "distance": 0.1}
        ]
        mock_generate.return_value = "Le projet a été validé lors de la réunion du 15 juillet."

        from app.services.rag_service import RAGService
        service = RAGService()
        result = service.query(meeting_id="test-meeting", question="Quel est le statut du projet ?")

        assert hasattr(result, "answer") or "answer" in (result if isinstance(result, dict) else result.model_dump())


class TestVectorStore:
    """Tests du VectorStore ChromaDB."""

    def test_vector_store_singleton(self):
        """VectorStore doit être un singleton."""
        from app.ai.embeddings.vector_store import VectorStore
        vs1 = VectorStore()
        vs2 = VectorStore()
        assert vs1 is vs2

    @patch("chromadb.PersistentClient")
    def test_vector_store_creates_collection(self, mock_chroma):
        """create_collection doit retourner une collection valide."""
        mock_collection = MagicMock()
        mock_client = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chroma.return_value = mock_client

        from app.ai.embeddings.vector_store import VectorStore
        vs = VectorStore()
        vs._client = mock_client  # Injection manuelle pour le test

        collection = vs.create_collection("test-meetings")
        assert collection is not None


class TestEmbeddingModel:
    """Tests du modèle d'embedding sentence-transformers."""

    def test_embedding_model_provider_importable(self):
        """EmbeddingModelProvider doit être importable."""
        from app.ai.embeddings.embedding_model import EmbeddingModelProvider
        assert EmbeddingModelProvider is not None

    @patch("app.ai.embeddings.embedding_model.EmbeddingModelProvider._load_model")
    def test_encode_returns_list_of_floats(self, mock_load_model):
        """encode() doit retourner des listes de flottants."""
        import numpy as np
        mock_model = MagicMock()
        mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3]])
        mock_load_model.return_value = mock_model

        from app.ai.embeddings.embedding_model import EmbeddingModelProvider
        EmbeddingModelProvider._instance = mock_model

        result = EmbeddingModelProvider.encode(["Test sentence"])
        assert isinstance(result, list)
