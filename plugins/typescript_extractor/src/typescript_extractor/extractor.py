from typing import Optional

from metadata_extractor.interfaces import LanguageExtractor
from metadata_extractor.models import ClassMetadata, FileMetadata, FunctionMetadata
from parser_core.models import AiekpAstNode


class TypescriptExtractor(LanguageExtractor):
    """
    Extracts metadata from a Typescript/Javascript AST.
    """

    def extract(self, ast_root: AiekpAstNode, file_path: str) -> FileMetadata:
        classes = []
        standalone_functions = []

        # Recursively search for classes and functions
        self._find_declarations(ast_root, classes, standalone_functions)

        return FileMetadata(
            file_path=file_path,
            language="typescript",
            classes=classes,
            standalone_functions=standalone_functions,
        )

    def _find_declarations(self, node: AiekpAstNode, classes: list, functions: list):
        if node.type == "class_declaration":
            classes.append(self._extract_class(node))
        elif node.type in [
            "function_declaration",
            "arrow_function",
            "generator_function",
        ]:
            # Check if it's not part of a class
            functions.append(self._extract_function(node))
        else:
            for child in node.children:
                self._find_declarations(child, classes, functions)

    def _extract_class(self, node: AiekpAstNode) -> ClassMetadata:
        name = (
            self._get_child_text(node, "type_identifier")
            or self._get_child_text(node, "identifier")
            or "Unknown"
        )
        docstring = self._extract_docstring_from_previous_sibling(node)
        methods = []

        class_body = self._get_child(node, "class_body")
        if class_body:
            for child in class_body.children:
                if child.type == "method_definition":
                    methods.append(self._extract_function(child))

        return ClassMetadata(
            name=name,
            docstring=docstring,
            methods=methods,
            start_line=node.start_point[0],
            end_line=node.end_point[0],
        )

    def _extract_function(self, node: AiekpAstNode) -> FunctionMetadata:
        if node.type == "method_definition":
            name = self._get_child_text(node, "property_identifier") or "Unknown"
        else:
            name = self._get_child_text(node, "identifier") or "Unknown"

        # Parameters
        params_node = self._get_child(node, "formal_parameters")
        params_list = []
        if params_node:
            raw_params = params_node.text.strip("()")
            if raw_params:
                params_list = [p.strip() for p in raw_params.split(",") if p.strip()]

        # Return type
        return_type = None
        type_node = self._get_child(node, "type_annotation")
        if type_node:
            # type_annotation usually starts with ':', so we strip it
            return_type = type_node.text.lstrip(":").strip()

        # Docstring
        docstring = self._extract_docstring_from_previous_sibling(node)

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

    def _extract_docstring_from_previous_sibling(
        self, node: AiekpAstNode
    ) -> Optional[str]:
        # Currently, AiekpAstNode does not expose siblings directly.
        # TS docstrings (JSDoc) are usually 'comment' nodes before the declaration.
        # Since we don't have parent/sibling refs yet, this is difficult.
        # For now, return None. JSDoc extraction can be enhanced by passing parent contexts.
        return None
