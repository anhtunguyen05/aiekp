import importlib
import logging
from typing import Dict

from .interfaces import LanguageParser

logger = logging.getLogger(__name__)

class ParserFactory:
    """
    Registry and factory for instantiating the correct LanguageParser based on file extension.
    """
    def __init__(self):
        self._parsers: Dict[str, LanguageParser] = {}
        
    def register_parser(self, parser: LanguageParser):
        """
        Registers a parser instance for all its supported extensions.
        """
        for ext in parser.supported_extensions:
            self._parsers[ext] = parser
            logger.info(f"Registered parser for {ext}")
            
    def get_parser(self, file_extension: str) -> LanguageParser:
        """
        Retrieves the appropriate parser for the given extension.
        
        Args:
            file_extension: The extension (e.g., '.py')
            
        Raises:
            ValueError: If no parser is registered for the extension.
        """
        if file_extension not in self._parsers:
            raise ValueError(f"No parser registered for file extension: {file_extension}")
        return self._parsers[file_extension]
        
    def load_plugins(self, plugin_modules: list[str]):
        """
        Dynamically loads plugin modules and registers their parsers.
        Each plugin module is expected to have a `register(factory: ParserFactory)` function.
        """
        for module_name in plugin_modules:
            try:
                module = importlib.import_module(module_name)
                if hasattr(module, 'register'):
                    module.register(self)
                else:
                    logger.warning(f"Plugin {module_name} does not have a 'register' function.")
            except Exception as e:
                logger.error(f"Failed to load plugin {module_name}: {e}")
