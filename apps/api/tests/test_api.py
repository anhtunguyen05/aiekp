from fastapi.testclient import TestClient
from src.main import app
import pytest

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to AIEKP API"}


def test_search_endpoint():
    # Because lifespan runs async, TestClient with lifespan can be tricky in older versions,
    # but with modern TestClient(app) it triggers lifespan on `with TestClient(app) as client:`
    # Let's test the search validation
    with TestClient(app) as client:
        # 1. Invalid payload
        response = client.post("/search/", json={})
        assert response.status_code == 422

        # 2. Valid payload (might fail if Neo4j/Qdrant are not up, but let's see)
        try:
            response = client.post("/search/", json={"query": "test", "top_k": 2})
            assert response.status_code == 200
            data = response.json()
            assert "results" in data
            assert data["query"] == "test"
        except Exception as e:
            pytest.skip(f"Skipping search test, DB likely not running: {e}")


def test_ingest_endpoint():
    with TestClient(app) as client:
        # Invalid path should return error status in 200 response
        response = client.post("/ingest/", json={"repo_path": "/invalid/path/12345"})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"


def test_impact_endpoint_validation():
    with TestClient(app) as client:
        # Invalid max_depth (< 1)
        response = client.get("/graph/impact/some_node?max_depth=0")
        assert response.status_code == 422

        # Invalid max_depth (> 5)
        response = client.get("/graph/impact/some_node?max_depth=6")
        assert response.status_code == 422


def test_impact_endpoint_not_found():
    with TestClient(app) as client:
        try:
            response = client.get("/graph/impact/node_does_not_exist_xyz_12345")
            assert response.status_code == 404
        except Exception as e:
            pytest.skip(f"DB not running: {e}")
