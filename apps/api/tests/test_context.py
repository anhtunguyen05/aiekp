from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_context_retrieve():
    # 1. Valid payload
    response = client.post("/context/retrieve", json={"query": "find user class"})
    assert response.status_code == 200
    data = response.json()
    assert "intent" in data
    assert "nodes" in data
    assert data["intent"]["query"] == "find user class"
    assert "class" in data["intent"]["target_types"]
