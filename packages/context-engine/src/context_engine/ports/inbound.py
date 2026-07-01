from abc import ABC, abstractmethod
from context_engine.domain.models import EvidencePayload


class IContextService(ABC):
    @abstractmethod
    async def retrieve_context(self, query: str) -> EvidencePayload:
        """
        Orchestrates intent analysis and knowledge retrieval to build the Evidence Payload.
        """
        pass
