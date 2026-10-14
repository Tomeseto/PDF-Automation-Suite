"""Unit tests for the FastAPI web server endpoints."""

from fastapi.testclient import TestClient
from app.web.server import app

client = TestClient(app)


def test_index_route():
    """Verify home page loads HTML."""
    response = client.get("/")
    assert response.status_code == 200
    assert "PDF Automation Suite" in response.text
    assert "iLovePDF" in response.text or "PDF Suite" in response.text


def test_logs_endpoint():
    """Verify logs retrieval endpoint works."""
    response = client.get("/api/logs?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert isinstance(data["events"], list)


def test_batch_operations_endpoint():
    """Verify batch operations list endpoint works."""
    response = client.get("/api/batch/operations")
    assert response.status_code == 200
    data = response.json()
    assert "operations" in data
    assert len(data["operations"]) > 0
