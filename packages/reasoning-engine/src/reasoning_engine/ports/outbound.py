from abc import ABC, abstractmethod
from typing import Dict, Any, List


class IContextFetcher(ABC):
    """
    Driven port for fetching context from the Context Intelligence Engine (Phase 6).
    """

    @abstractmethod
    async def fetch_context(
        self, query: str, target_types: List[str] = None
    ) -> Dict[str, Any]:
        """
        Calls POST /context/retrieve and returns the EvidencePayload as a dict.
        """
        pass


class ILLMGenerator(ABC):
    """
    Driven port for generating responses using an LLM.
    """

    @abstractmethod
    async def generate(self, prompt: str, system_message: str = None) -> str:
        """
        Sends the prompt and optional system message to the LLM and returns the completion.
        """
        pass

    @abstractmethod
    async def astream(self, prompt: str, system_message: str = None):
        """
        Sends the prompt and streams the completion back using an async generator.
        """
        pass
