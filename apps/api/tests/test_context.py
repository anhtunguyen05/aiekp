from fastapi.testclient import TestClient
from src.main import app
from src.dependencies import get_context_service
from context_engine.ports.inbound import IContextService
from context_engine.domain.models import EvidencePayload, RetrievalIntent, EvidenceNode

client = TestClient(app)


class MockContextService(IContextService):
    async def retrieve_context(self, query: str) -> EvidencePayload:
        return EvidencePayload(
            original_query=query,
            intent=RetrievalIntent(
                query=query, target_types=["class"], semantic_keywords=[]
            ),
            nodes=[EvidenceNode(id="mock_id", name="Mock Node", type="class")],
            summary="Mock summary",
        )


app.dependency_overrides[get_context_service] = lambda: MockContextService()


def test_context_retrieve():
    # 1. Valid payload
    response = client.post("/context/retrieve", json={"query": "find user class"})
    assert response.status_code == 200
    data = response.json()
    assert "intent" in data
    assert "nodes" in data
    assert data["intent"]["query"] == "find user class"
    assert "class" in data["intent"]["target_types"]
