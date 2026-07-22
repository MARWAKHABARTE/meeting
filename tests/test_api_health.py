"""
Tests unitaires — Health Check API.
Vérifie les routes /health et / de l'application FastAPI.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


class TestHealthEndpoint:
    """Groupe de tests : route /health"""

    def test_health_returns_200(self, client: TestClient):
        """Le health check doit retourner HTTP 200."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_healthy_status(self, client: TestClient):
        """Le payload doit contenir status='healthy'."""
        response = client.get("/health")
        data = response.json()
        assert data.get("status") == "healthy"

    def test_health_contains_project_name(self, client: TestClient):
        """Le payload doit contenir le nom du projet."""
        response = client.get("/health")
        data = response.json()
        assert "project" in data

    def test_health_contains_environment(self, client: TestClient):
        """Le payload doit contenir l'environnement."""
        response = client.get("/health")
        data = response.json()
        assert "environment" in data


class TestRootEndpoint:
    """Groupe de tests : route racine /"""

    def test_root_returns_200(self, client: TestClient):
        """La route racine doit retourner HTTP 200."""
        response = client.get("/")
        assert response.status_code == 200

    def test_root_contains_welcome_message(self, client: TestClient):
        """La route racine doit contenir un message de bienvenue."""
        response = client.get("/")
        data = response.json()
        assert "message" in data

    def test_root_contains_docs_url(self, client: TestClient):
        """La réponse doit contenir l'URL de la documentation."""
        response = client.get("/")
        data = response.json()
        assert "docs_url" in data
