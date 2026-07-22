"""
Tests Celery — Infrastructure asynchrone.
Vérifie la création de l'application Celery et les routes de monitoring.
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


class TestCeleryInfrastructure:
    """Tests de l'infrastructure Celery."""

    def test_celery_app_is_importable(self):
        """L'application Celery doit être importable sans erreur."""
        from app.workers.celery_app import celery_app
        assert celery_app is not None

    def test_celery_app_has_correct_name(self):
        """L'application Celery doit avoir le bon nom."""
        from app.workers.celery_app import celery_app
        assert celery_app.main == "meeting_ai" or "meeting" in celery_app.main.lower()

    def test_celery_health_endpoint_returns_200(self, client: TestClient):
        """L'endpoint /workers/health doit retourner 200."""
        response = client.get("/api/v1/workers/health")
        assert response.status_code == 200

    def test_celery_health_response_has_correct_keys(self, client: TestClient):
        """La réponse du health check Celery doit contenir 'worker' et 'broker'."""
        response = client.get("/api/v1/workers/health")
        data = response.json()
        assert "worker" in data
        assert "broker" in data

    @patch("app.workers.tasks.health.health_task.delay")
    def test_submit_test_task_returns_202(self, mock_delay, client: TestClient):
        """Le endpoint /workers/test doit retourner 202 Accepted."""
        mock_result = MagicMock()
        mock_result.id = "test-task-uuid-12345"
        mock_delay.return_value = mock_result

        response = client.post("/api/v1/workers/test")
        assert response.status_code == 202

    @patch("app.api.v1.endpoints.workers.AsyncResult")
    def test_get_task_status_returns_200(self, mock_async_result, client: TestClient):
        """La consultation d'un task_id doit retourner 200."""
        mock_result = MagicMock()
        mock_result.state = "PENDING"
        mock_result.result = None
        mock_async_result.return_value = mock_result

        response = client.get("/api/v1/workers/tasks/unknown-task-test-id")
        assert response.status_code == 200
