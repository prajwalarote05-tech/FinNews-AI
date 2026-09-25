from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_root_endpoint():
    """Verify GET / returns online status and correct API metadata."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "FinNews AI" in data["name"]
    assert data["health"] == "/health"
    assert data["docs"] == "/docs"

def test_health_endpoint():
    """Verify GET /health returns status healthy."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data == {"status": "healthy"}
