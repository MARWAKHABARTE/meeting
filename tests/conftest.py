"""
Configuration pytest partagée — fixtures et client de test.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.settings import settings


@pytest.fixture(scope="session")
def client():
    """Client de test synchrone FastAPI (httpx)."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def base_url() -> str:
    return f"http://testserver{settings.API_V1_STR}"
