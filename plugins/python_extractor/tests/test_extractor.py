from parser_core.factory import ParserFactory
from python_parser.parser import PythonParser
from python_extractor.extractor import PythonExtractor


def test_python_extractor():
    # 1. Parse using PythonParser to get AST
    parser_factory = ParserFactory()
    parser_factory.register_parser(PythonParser())
    parser = parser_factory.get_parser(".py")

    code = b"""
def standalone_func(a: int, b: int) -> int:
    \"\"\"This is a standalone function.\"\"\"
    return a + b

class TestClass:
    \"\"\"This is a test class.\"\"\"
    
    def method_one(self, val):
        \"\"\"Method one docstring.\"\"\"
        pass
"""
    ast = parser.parse(code)

    # 2. Extract using PythonExtractor
    extractor = PythonExtractor()
    metadata = extractor.extract(ast, "test.py")

    # 3. Assertions
    assert metadata.file_path == "test.py"
    assert metadata.language == "python"

    # Check standalone functions
    assert len(metadata.standalone_functions) == 1
    func = metadata.standalone_functions[0]
    assert func.name == "standalone_func"
    assert func.docstring == "This is a standalone function."
    assert func.parameters == ["a: int", "b: int"]
    assert func.return_type == "int"

    # Check classes
    assert len(metadata.classes) == 1
    cls = metadata.classes[0]
    assert cls.name == "TestClass"
    assert cls.docstring == "This is a test class."

    # Check methods inside class
    assert len(cls.methods) == 1
    method = cls.methods[0]
    assert method.name == "method_one"
    assert method.docstring == "Method one docstring."
    assert method.parameters == ["self", "val"]
    assert method.return_type is None
