import httpx
from typing import List, Optional
from context_engine.domain.models import EvidenceNode
from context_engine.ports.outbound import IKnowledgeEngineClient


class HttpKnowledgeEngineAdapter(IKnowledgeEngineClient):
    """
    Adapter that communicates with the Phase 5 FastAPI Knowledge Engine over HTTP.
    """

    def __init__(self, base_url: str = "http://localhost:8000", token: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.token = token

    async def search_nodes(self, query: str, top_k: int = 5) -> List[dict]:
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/search/", json={"query": query, "top_k": top_k}, headers=headers
            )
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])

    async def get_node_details(self, node_id: str) -> EvidenceNode:
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        async with httpx.AsyncClient() as client:
            # We must URL encode the node_id carefully since it might contain backslashes or slashes
            # However, httpx does basic encoding. Let's send it.
            # FastApi path parameter needs proper escaping if it has slashes.
            import urllib.parse

            encoded_id = urllib.parse.quote(node_id, safe="")

            response = await client.get(f"{self.base_url}/graph/nodes/{encoded_id}", headers=headers)

            if response.status_code == 404:
                return EvidenceNode(
                    id=node_id, name="Unknown", type="unknown", content="Not found"
                )

            response.raise_for_status()
            data = response.json()

            props = data.get("properties", {})
            rels = data.get("relationships", [])

            return EvidenceNode(
                id=node_id,
                name=props.get("name", "Unknown"),
                type=props.get("type", "unknown"),
                content=props.get("content", ""),
                properties=props,
                relationships=rels,
            )
