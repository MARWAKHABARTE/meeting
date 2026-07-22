"""
Tests unitaires — Settings et Configuration.
Vérifie que les paramètres de configuration sont correctement chargés depuis les variables d'environnement.
"""
import pytest
from app.core.settings import settings


class TestAppSettings:
    """Tests de la configuration applicative (settings.py)."""

    def test_project_name_is_not_empty(self):
        """Le nom du projet ne doit pas être vide."""
        assert settings.PROJECT_NAME
        assert isinstance(settings.PROJECT_NAME, str)

    def test_api_version_prefix_format(self):
        """Le préfixe de l'API v1 doit commencer par /."""
        assert settings.API_V1_STR.startswith("/")

    def test_environment_value_is_valid(self):
        """L'environnement doit être l'une des valeurs connues."""
        valid = {"development", "staging", "production"}
        assert settings.ENVIRONMENT in valid


class TestDatabaseSettings:
    """Tests de la configuration base de données."""

    def test_postgres_user_is_not_empty(self):
        """L'utilisateur PostgreSQL ne doit pas être vide."""
        assert settings.POSTGRES_USER

    def test_postgres_port_is_valid(self):
        """Le port PostgreSQL doit être un entier positif."""
        assert isinstance(settings.POSTGRES_PORT, int)
        assert 1 <= settings.POSTGRES_PORT <= 65535

    def test_postgres_db_is_not_empty(self):
        """Le nom de la base de données ne doit pas être vide."""
        assert settings.POSTGRES_DB


class TestRedisSettings:
    """Tests de la configuration Redis."""

    def test_redis_host_is_not_empty(self):
        """L'hôte Redis ne doit pas être vide."""
        assert settings.REDIS_HOST

    def test_redis_port_is_valid(self):
        """Le port Redis doit être un entier positif."""
        assert isinstance(settings.REDIS_PORT, int)
        assert 1 <= settings.REDIS_PORT <= 65535


class TestAISettings:
    """Tests de la configuration du pipeline IA."""

    def test_ollama_host_is_not_empty(self):
        """L'hôte Ollama ne doit pas être vide."""
        assert settings.OLLAMA_HOST
        assert settings.OLLAMA_HOST.startswith("http")

    def test_ollama_model_is_not_empty(self):
        """Le modèle Ollama ne doit pas être vide."""
        assert settings.OLLAMA_MODEL

    def test_rag_top_k_is_positive(self):
        """Le top_k du RAG doit être un entier positif."""
        assert settings.RAG_TOP_K > 0

    def test_chunk_size_is_valid(self):
        """La taille des chunks doit être raisonnable."""
        assert 100 <= settings.CHUNK_SIZE <= 4000
