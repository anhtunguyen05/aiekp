from typing import Optional

from metadata_extractor.interfaces import LanguageExtractor
from metadata_extractor.models import ClassMetadata, FileMetadata, FunctionMetadata
from parser_core.models import AiekpAstNode


class PythonExtractor(LanguageExtractor):
    """
    Extracts metadata from a Python AST.
    """

    def extract(self, ast_root: AiekpAstNode, file_path: str) -> FileMetadata:
        classes = []
        standalone_functions = []

        for child in ast_root.children:
            if child.type == "class_definition":
                classes.append(self._extract_class(child))
            elif child.type == "function_definition":
                standalone_functions.append(self._extract_function(child))

        return FileMetadata(
            file_path=file_path,
            language="python",
            classes=classes,
            standalone_functions=standalone_functions,
        )

    def _extract_class(self, node: AiekpAstNode) -> ClassMetadata:
        name = self._get_child_text(node, "identifier") or "Unknown"
        docstring = None
        methods = []

        block = self._get_child(node, "block")
        if block:
            docstring = self._extract_docstring_from_block(block)
            for child in block.children:
                if child.type == "function_definition":
                    methods.append(self._extract_function(child))

        return ClassMetadata(
            name=name,
            docstring=docstring,
            methods=methods,
            start_line=node.start_point[0],
            end_line=node.end_point[0],
        )

    def _extract_function(self, node: AiekpAstNode) -> FunctionMetadata:
        name = self._get_child_text(node, "identifier") or "Unknown"

        # Parameters (just raw text inside the parens for now)
        params_node = self._get_child(node, "parameters")
        params_list = []
        if params_node:
            # params_node.text is something like "(a: int, b: int)"
            raw_params = params_node.text.strip("()")
            if raw_params:
                params_list = [p.strip() for p in raw_params.split(",") if p.strip()]

        # Return type
        return_type = None
        type_node = self._get_child(node, "type")
        if type_node:
            return_type = type_node.text

        # Docstring
        docstring = None
        block = self._get_child(node, "block")
        if block:
            docstring = self._extract_docstring_from_block(block)

        return FunctionMetadata(
            name=name,
            docstring=docstring,
            parameters=params_list,
            return_type=return_type,
            start_line=node.start_point[0],
            end_line=node.end_point[0],
        )

    def _get_child(self, node: AiekpAstNode, child_type: str) -> Optional[AiekpAstNode]:
        for child in node.children:
            if child.type == child_type:
                return child
        return None

    def _get_child_text(self, node: AiekpAstNode, child_type: str) -> Optional[str]:
        child = self._get_child(node, child_type)
        return child.text if child else None

    def _extract_docstring_from_block(self, block_node: AiekpAstNode) -> Optional[str]:
        """
        In Python, a docstring is an expression_statement -> string at the very beginning of a block.
        """
        if not block_node.children:
            return None

        first_child = block_node.children[0]
        if first_child.type == "expression_statement":
            string_node = self._get_child(first_child, "string")
            if string_node:
                # Strip the quotes
                content = string_node.text
                if content.startswith('"""') and content.endswith('"""'):
                    return content[3:-3].strip()
                elif content.startswith("'''") and content.endswith("'''"):
                    return content[3:-3].strip()
                elif content.startswith('"') and content.endswith('"'):
                    return content[1:-1].strip()
                elif content.startswith("'") and content.endswith("'"):
                    return content[1:-1].strip()
        return None
