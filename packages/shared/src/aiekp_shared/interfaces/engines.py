from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

from aiekp_shared.domain.models import Repository, Evidence


class IKnowledgeEngine(ABC):
    """
    Interface for the Knowledge Engine.
    Responsible for converting repositories into engineering knowledge.
    """

    @abstractmethod
    async def scan_repository(self, repo: Repository) -> bool:
        """Scan a repository and trigger processing."""
        pass

    @abstractmethod
    async def query_graph(
        self, cypher_query: str, params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Query the knowledge graph (Neo4j)."""
        pass

    @abstractmethod
    async def semantic_search(self, query: str, top_k: int = 5) -> List[Evidence]:
        """Perform semantic search using vector embeddings (Qdrant)."""
        pass


class IContextEngine(ABC):
    """
    Interface for the Context Intelligence Engine.
    Responsible for generating the optimal context payload for a task.
    """

    @abstractmethod
    async def build_context(
        self, task_intent: str, knowledge_engine: IKnowledgeEngine
    ) -> Dict[str, Any]:
        """
        Detect intent, retrieve knowledge, collect evidence, and compose a Context Payload.
        """
        pass


class IReasoningEngine(ABC):
    """
    Interface for the Reasoning Engine.
    Responsible for orchestrating AI reasoning over the context payload.
    """

    @abstractmethod
    async def reason(self, context_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the LangGraph workflow using the provided context payload.
        Returns an evidence-based answer.
        """
        pass
