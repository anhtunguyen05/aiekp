import importlib
import logging
from typing import Dict

from .interfaces import LanguageExtractor


class ExtractorFactory:
    """
    Factory for registering and retrieving language-specific metadata extractors.
    Automatically attempts to load known plugins upon initialization.
    """

    def __init__(self):
        self._extractors: Dict[str, LanguageExtractor] = {}
        self._logger = logging.getLogger(__name__)
        self._load_default_plugins()

    def _load_default_plugins(self):
        """Attempts to load known extractor plugins dynamically."""
        known_plugins = ["python_extractor"]
        for plugin in known_plugins:
            try:
                module = importlib.import_module(plugin)
                if hasattr(module, "register"):
                    module.register(self)
                    self._logger.debug(
                        f"Successfully loaded extractor plugin: {plugin}"
                    )
            except ImportError:
                self._logger.warning(
                    f"Could not load extractor plugin: {plugin}. Is it installed?"
                )
            except Exception as e:
                self._logger.error(f"Error loading extractor plugin {plugin}: {e}")

    def register_extractor(self, ext: str, extractor: LanguageExtractor):
        """
        Register a language extractor for a specific file extension.

        Args:
            ext: File extension starting with dot (e.g., '.py')
            extractor: An instance of a LanguageExtractor
        """
        if not ext.startswith("."):
            ext = "." + ext
        self._extractors[ext] = extractor

    def get_extractor(self, file_extension: str) -> LanguageExtractor:
        """
        Retrieve the appropriate extractor for the given file extension.

        Args:
            file_extension: The extension of the file (e.g., '.py')

        Returns:
            The registered LanguageExtractor instance.

        Raises:
            ValueError: If no extractor is registered for the extension.
        """
        if not file_extension.startswith("."):
            file_extension = "." + file_extension

        extractor = self._extractors.get(file_extension)
        if not extractor:
            raise ValueError(f"No extractor registered for extension: {file_extension}")
        return extractor
