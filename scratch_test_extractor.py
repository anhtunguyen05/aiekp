from parser_core.factory import ParserFactory
from python_parser.parser import PythonParser
from metadata_extractor.factory import ExtractorFactory
import python_extractor as python_ext


def main():
    # 1. Setup Parser (Phase 2)
    parser_factory = ParserFactory()
    parser_factory.register_parser(PythonParser())
    parser = parser_factory.get_parser(".py")

    # 2. Setup Extractor (Phase 3)
    extractor_factory = ExtractorFactory()
    # It auto-loads, but we can also manually register to be safe
    python_ext.register(extractor_factory)
    extractor = extractor_factory.get_extractor(".py")

    # 3. Sample code
    sample_code = b"""
import os

def create_user(username: str, age: int) -> bool:
    \"\"\"
    Creates a new user in the system.
    Returns True if successful.
    \"\"\"
    if age < 18:
        return False
    return True
    
class UserManager:
    \"\"\"
    Manages user operations and state.
    \"\"\"
    
    def __init__(self):
        self.users = []
        
    def delete_user(self, user_id: int):
        \"\"\"Deletes a user by their ID.\"\"\"
        pass
"""

    print("--- 1. PARSING CODE ---")
    ast_root = parser.parse(sample_code)
    print(f"Parsed {len(ast_root.children)} root nodes.\n")

    print("--- 2. EXTRACTING METADATA ---")
    file_metadata = extractor.extract(ast_root, file_path="example_user_manager.py")

    print("--- 3. OUTPUT METADATA (JSON) ---")
    print(file_metadata.model_dump_json(indent=4))


if __name__ == "__main__":
    main()
