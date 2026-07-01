from abc import ABC, abstractmethod
from typing import List
from context_engine.domain.models import RetrievalIntent, EvidenceNode


class IIntentAnalyzer(ABC):
    @abstractmethod
    async def analyze(self, query: str) -> RetrievalIntent:
        pass


class IKnowledgeEngineClient(ABC):
    @abstractmethod
    async def search_nodes(self, query: str, top_k: int = 5) -> List[dict]:
        """Performs semantic search to find entry point nodes."""
        pass

    @abstractmethod
    async def get_node_details(self, node_id: str) -> EvidenceNode:
        """Retrieves exact node details and relationships from the Graph DB."""
        pass
