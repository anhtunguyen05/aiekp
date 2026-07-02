from parser_core import ParserFactory
from .parser import TypescriptParser


def register(factory: ParserFactory):
    """
    Registers the TypescriptParser with the global ParserFactory.
    """
    factory.register_parser(TypescriptParser())


__all__ = ["register", "TypescriptParser"]
