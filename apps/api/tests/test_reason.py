from fastapi.testclient import TestClient
from src.main import app
from src.dependencies import get_reasoning_service
from reasoning_engine.ports.inbound import IReasoningService
from reasoning_engine.domain.models import ReasoningRequest, ReasoningResult

client = TestClient(app)


class MockReasoningService(IReasoningService):
    async def process_query(self, request: ReasoningRequest) -> ReasoningResult:
        return ReasoningResult(
            answer="Mock Answer", sources_used=[{"id": "node_1"}], confidence_score=0.9
        )

    async def stream_process_query(self, request: ReasoningRequest):
        yield "Mock "
        yield "Answer"


app.dependency_overrides[get_reasoning_service] = lambda: MockReasoningService()


def test_reason_endpoint():
    payload = {"query": "How does auth work?", "session_id": "test_123"}
    response = client.post("/reason/", json=payload)
    print("STATUS", response.status_code)
    print("RESPONSE", response.text)

    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "Mock Answer"
    assert data["sources_used"] == [{"id": "node_1"}]
    assert data["confidence_score"] == 0.9
