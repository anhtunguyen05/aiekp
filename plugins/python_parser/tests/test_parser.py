from python_parser.parser import PythonParser


def test_python_parser():
    parser = PythonParser()
    assert ".py" in parser.supported_extensions

    code = b"def test_func():\n    pass\n"
    ast = parser.parse(code)

    assert ast.type == "module"
    assert len(ast.children) == 1
    assert ast.children[0].type == "function_definition"
    assert "def test_func():" in ast.children[0].text
