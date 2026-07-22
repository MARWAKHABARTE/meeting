"""
Tests d'intégration — Stockage MinIO.
Vérifie la connexion, l'existence du bucket et les opérations de base.
"""
import pytest
from unittest.mock import patch, MagicMock
from app.storage.service import StorageService
from app.storage.exceptions import StorageException


class TestStorageService:
    """Tests du service de stockage MinIO."""

    def test_storage_service_instantiates(self):
        """StorageService doit pouvoir s'instancier sans erreur."""
        service = StorageService()
        assert service is not None

    @patch("app.storage.client.MinioClientProvider.get_client")
    def test_upload_file_calls_put_object(self, mock_get_client):
        """upload_file doit appeler put_object sur le client MinIO."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        service = StorageService()
        service.upload_file(
            bucket_name="test-bucket",
            object_name="audio.mp3",
            data=b"fake-audio-data",
            content_type="audio/mpeg"
        )

        mock_client.put_object.assert_called_once()

    @patch("app.storage.client.MinioClientProvider.get_client")
    def test_get_file_url_calls_presigned_get_object(self, mock_get_client):
        """get_file_url doit appeler presigned_get_object sur le client MinIO."""
        mock_client = MagicMock()
        mock_client.presigned_get_object.return_value = "http://minio.local/audio.mp3?token=xyz"
        mock_get_client.return_value = mock_client

        service = StorageService()
        url = service.get_file_url("test-bucket", "audio.mp3")

        assert url == "http://minio.local/audio.mp3?token=xyz"
        mock_client.presigned_get_object.assert_called_once()


class TestStorageHealth:
    """Tests du health check MinIO via l'API."""

    def test_storage_health_endpoint(self):
        """Le endpoint de santé MinIO doit être accessible."""
        from fastapi.testclient import TestClient
        from app.main import app
        with TestClient(app) as client:
            response = client.get("/api/v1/storage/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
