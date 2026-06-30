from parser_core import ParserFactory
from .parser import PythonParser


def register(factory: ParserFactory):
    """
    Registers the PythonParser with the global ParserFactory.
    """
    factory.register_parser(PythonParser())


__all__ = ["register", "PythonParser"]
