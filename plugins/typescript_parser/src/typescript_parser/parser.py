import tree_sitter_typescript as tstypescript
import tree_sitter_javascript as tsjavascript
from tree_sitter import Language, Parser, Node
from typing import List

from parser_core import LanguageParser, AiekpAstNode


class TypescriptParser(LanguageParser):
    """
    Typescript and Javascript implementation of the LanguageParser using tree-sitter.
    """

    def __init__(self):
        self.ts_language = Language(tstypescript.language_typescript())
        self.tsx_language = Language(tstypescript.language_tsx())
        self.js_language = Language(tsjavascript.language())

        self.ts_parser = Parser(self.ts_language)
        self.tsx_parser = Parser(self.tsx_language)
        self.js_parser = Parser(self.js_language)

    @property
    def supported_extensions(self) -> List[str]:
        return [".ts", ".tsx", ".js", ".jsx"]

    def parse(self, file_content: str, file_path: str) -> AiekpAstNode:
        """
        Parses TS/JS source code into a normalized AiekpAstNode.
        """
        source_bytes = file_content.encode("utf-8")
        if file_path.endswith(".tsx"):
            tree = self.tsx_parser.parse(source_bytes)
        elif file_path.endswith(".ts"):
            tree = self.ts_parser.parse(source_bytes)
        else:
            tree = self.js_parser.parse(source_bytes)

        return self._map_node(tree.root_node, source_bytes)

    def _map_node(self, node: Node, source: bytes) -> AiekpAstNode:
        """
        Recursively maps a tree-sitter Node to an AiekpAstNode.
        """
        try:
            text = source[node.start_byte : node.end_byte].decode(
                "utf-8", errors="replace"
            )
        except Exception:
            text = ""

        children = [self._map_node(child, source) for child in node.children]

        return AiekpAstNode(
            type=node.type,
            text=text,
            start_byte=node.start_byte,
            end_byte=node.end_byte,
            start_point=node.start_point,
            end_point=node.end_point,
            children=children,
            properties={},
        )
