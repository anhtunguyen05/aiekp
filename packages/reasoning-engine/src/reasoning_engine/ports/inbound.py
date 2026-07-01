from abc import ABC, abstractmethod
from reasoning_engine.domain.models import ReasoningRequest, ReasoningResult


class IReasoningService(ABC):
    """
    Driving port for orchestrating AI reasoning.
    """

    @abstractmethod
    async def process_query(self, request: ReasoningRequest) -> ReasoningResult:
        """
        Takes a raw query, orchestrates LangGraph to fetch context and synthesize an answer,
        and returns the final ReasoningResult.
        """
        pass

    @abstractmethod
    async def stream_process_query(self, request: ReasoningRequest):
        """
        Takes a raw query, orchestrates context fetching and streams the synthesized answer.
        Yields chunks of text.
        """
        pass
