from metadata_extractor.factory import ExtractorFactory
from .extractor import TypescriptExtractor


def register(factory: ExtractorFactory):
    """
    Registers the TypescriptExtractor with the ExtractorFactory.
    """
    extractor = TypescriptExtractor()
    factory.register_extractor(".ts", extractor)
    factory.register_extractor(".tsx", extractor)
    factory.register_extractor(".js", extractor)
    factory.register_extractor(".jsx", extractor)
