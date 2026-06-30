from metadata_extractor.factory import ExtractorFactory
from .extractor import PythonExtractor


def register(factory: ExtractorFactory):
    """
    Registers the PythonExtractor with the ExtractorFactory.
    """
    factory.register_extractor(".py", PythonExtractor())
