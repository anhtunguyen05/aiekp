from abc import ABC, abstractmethod
from parser_core.models import AiekpAstNode
from .models import FileMetadata


class LanguageExtractor(ABC):
    """
    Abstract Base Class for language-specific metadata extractors.
    Each plugin (e.g., PythonExtractor) must implement this interface.
    """

    @abstractmethod
    def extract(self, ast_root: AiekpAstNode, file_path: str) -> FileMetadata:
        """
        Extract business metadata (Classes, Functions, Docstrings) from a parsed AST.

        Args:
            ast_root: The root node of the normalized AST.
            file_path: The original file path.

        Returns:
            FileMetadata containing extracted structures.
        """
        pass
