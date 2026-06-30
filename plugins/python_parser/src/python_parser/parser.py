import tree_sitter_python as tspython
from tree_sitter import Language, Parser, Node
from typing import List

from parser_core import LanguageParser, AiekpAstNode

class PythonParser(LanguageParser):
    """
    Python-specific implementation of the LanguageParser using tree-sitter-python.
    """
    def __init__(self):
        self.language = Language(tspython.language())
        self.parser = Parser(self.language)

    @property
    def supported_extensions(self) -> List[str]:
        return [".py", ".pyw"]

    def parse(self, file_content: bytes) -> AiekpAstNode:
        """
        Parses python source code into a normalized AiekpAstNode.
        """
        tree = self.parser.parse(file_content)
        return self._map_node(tree.root_node, file_content)

    def _map_node(self, node: Node, source: bytes) -> AiekpAstNode:
        """
        Recursively maps a tree-sitter node to an AiekpAstNode.
        """
        text = source[node.start_byte:node.end_byte].decode('utf-8', errors='replace')
        
        children = [self._map_node(child, source) for child in node.children]
        
        return AiekpAstNode(
            type=node.type,
            text=text,
            start_byte=node.start_byte,
            end_byte=node.end_byte,
            start_point=node.start_point,
            end_point=node.end_point,
            children=children,
            properties={}
        )
