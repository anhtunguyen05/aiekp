from abc import ABC, abstractmethod
from typing import List

from .models import AiekpAstNode


class LanguageParser(ABC):
    """
    Strategy interface for all language-specific parsers.
    """

    @property
    @abstractmethod
    def supported_extensions(self) -> List[str]:
        """
        Returns a list of file extensions supported by this parser (e.g., ['.py']).
        """
        pass

    @abstractmethod
    def parse(self, file_content: bytes, file_path: str = "") -> AiekpAstNode:
        """
        Parses raw source code into a normalized AIEKP AST.

        Args:
            file_content (bytes): The raw source code bytes.

        Returns:
            AiekpAstNode: The root of the normalized AST.
        """
        pass
