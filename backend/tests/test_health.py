import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app
from app.config import Settings

client = TestClient(app)

def test_health_check_success():
    with patch("app.api.endpoints.health.engine.connect") as mock_connect:
        mock_connect.return_value.__enter__.return_value.execute.return_value = None
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
        assert data["service"] == "IntelliRAG API"
        assert "version" in data
        assert "environment" in data

def test_health_check_database_unavailable():
    with patch("app.api.endpoints.health.engine.connect", side_effect=Exception("DB connection refused")):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"
        assert data["database"] == "unavailable"
        assert data["service"] == "IntelliRAG API"

def test_root_health_endpoint():
    with patch("app.api.endpoints.health.engine.connect") as mock_connect:
        mock_connect.return_value.__enter__.return_value.execute.return_value = None
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"

def test_readiness_endpoint_success():
    with patch("app.api.endpoints.health.engine.connect") as mock_connect:
        mock_connect.return_value.__enter__.return_value.execute.return_value = None
        response = client.get("/health/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert data["database"] == "connected"

def test_readiness_endpoint_database_down():
    with patch("app.api.endpoints.health.engine.connect", side_effect=Exception("DB down")):
        response = client.get("/health/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "not_ready"
        assert data["database"] == "unavailable"

def test_production_jwt_secret_validation():
    with pytest.raises(ValueError):
        Settings(
            ENVIRONMENT="production",
            JWT_SECRET_KEY="changethis-insecure-development-jwt-secret-key-32charsmin"
        )