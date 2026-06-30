import json
from parser_core.factory import ParserFactory
from python_parser.parser import PythonParser
from parser_core.models import AiekpAstNode

def print_tree(node: AiekpAstNode, prefix: str = "", is_last: bool = True):
    """Hàm hỗ trợ in cây AST ra console cho đẹp mắt."""
    connector = "\\-- " if is_last else "|-- "
    
    # Rút gọn text nếu quá dài
    text = node.text.replace('\n', '\\n')
    if len(text) > 40:
        text = text[:37] + "..."
        
    print(f"{prefix}{connector}{node.type}: '{text}'")
    
    prefix += "    " if is_last else "|   "
    for i, child in enumerate(node.children):
        is_last_child = (i == len(node.children) - 1)
        print_tree(child, prefix, is_last_child)

def main():
    # 1. Khởi tạo Factory và Đăng ký Plugin Python
    factory = ParserFactory()
    factory.register_parser(PythonParser())
    
    # 2. Đoạn code Python mẫu để parse
    sample_code = b"""
def hello_world(name: str):
    print(f"Hello {name} from AIEKP!")
    
class MyTestClass:
    def method_a(self):
        return True
"""

    print("--- PARSING THE FOLLOWING CODE ---")
    print(sample_code.decode('utf-8'))
    print("--------------------------------\n")

    # 3. Lấy đúng parser dựa trên đuôi file (.py)
    parser = factory.get_parser(".py")
    
    # 4. Tiến hành parse ra cây AST chung (AiekpAstNode)
    ast_node = parser.parse(sample_code)
    
    # 5. In kết quả dạng cây
    print("AST RESULT (Abstract Syntax Tree):")
    print_tree(ast_node)

if __name__ == "__main__":
    main()
