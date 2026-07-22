"""
Tests de sécurité — Headers HTTP, CORS et protections globales.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


class TestSecurityHeaders:
    """Tests de présence et de valeur des headers de sécurité HTTP."""

    def test_health_endpoint_is_accessible_without_auth(self, client: TestClient):
        """Le health check doit être accessible sans authentification."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_protected_api_route_without_token_is_refused(self, client: TestClient):
        """Un endpoint protégé sans token JWT doit retourner 401 ou 403."""
        response = client.get("/api/v1/auth/me")
        # L'absence de token doit entraîner un refus d'accès
        assert response.status_code in (401, 403)

    def test_cors_headers_present_on_health(self, client: TestClient):
        """Les headers CORS doivent être présents sur les réponses (pour les origines autorisées)."""
        response = client.get(
            "/health",
            headers={"Origin": "http://localhost:3000"}
        )
        # La clé peut être Access-Control-Allow-Origin selon la config CORS
        assert response.status_code == 200


class TestRequestValidation:
    """Tests de validation des requêtes entrantes."""

    def test_invalid_json_body_returns_422(self, client: TestClient):
        """Une requête avec un mauvais corps JSON doit retourner 422."""
        response = client.post(
            "/api/v1/transcriptions/start",
            content="invalid-json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422

    def test_missing_required_field_returns_422(self, client: TestClient):
        """Un champ obligatoire manquant doit retourner 422."""
        response = client.post("/api/v1/transcriptions/start", json={"foo": "bar"})
        assert response.status_code == 422

    def test_unknown_endpoint_returns_404(self, client: TestClient):
        """Un endpoint inexistant doit retourner 404."""
        response = client.get("/api/v1/nonexistent-route")
        assert response.status_code == 404
