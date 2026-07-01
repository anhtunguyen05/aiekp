import httpx
from typing import Dict, Any, List
from reasoning_engine.ports.outbound import IContextFetcher


class ContextEngineHttpAdapter(IContextFetcher):
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def fetch_context(
        self, query: str, target_types: List[str] = None
    ) -> Dict[str, Any]:
        """
        Calls the Context Intelligence Engine (Phase 6) to fetch evidence for the query.
        """
        payload = {"query": query, "target_types": target_types or []}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/context/retrieve", json=payload
            )
            response.raise_for_status()
            return response.json()
