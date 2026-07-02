import sys
from pathlib import Path
from parser_core.factory import ParserFactory
from metadata_extractor.factory import ExtractorFactory

# Register the plugins (normally done by the app startup)
# But actually, the parser/extractor factories just need the plugins installed 
# and their entry points will be picked up? 
# Wait, let's look at how the app registers them. 
# Usually, we just import them to register.
import typescript_parser
import typescript_extractor

def test_ts_parsing():
    print("Testing TS Parsing...")
    
    file_path = Path("../../sample-ts-app/index.ts")
    content = file_path.read_text()
    
    parser_factory = ParserFactory()
    parser_factory.load_plugins(["typescript_parser"])
    parser = parser_factory.get_parser(".ts")
        
    print(f"Parser class: {parser.__class__.__name__}")
    ast = parser.parse(content, str(file_path))
    if not ast:
        print("Failed to generate AST")
        return
    print("AST generated successfully!")
    
    extractor_factory = ExtractorFactory()
    extractor = extractor_factory.get_extractor(".ts")
        
    print(f"Extractor class: {extractor.__class__.__name__}")
    
    file_metadata = extractor.extract(ast, str(file_path))
    
    print("\nExtracted Classes:")
    for cls in file_metadata.classes:
        print(f"- Class: {cls.name} (Lines {cls.start_line}-{cls.end_line})")
        for method in cls.methods:
            print(f"  - Method: {method.name}")

    print("\nExtracted Functions:")
    for func in file_metadata.standalone_functions:
        print(f"- Function: {func.name} (Lines {func.start_line}-{func.end_line})")

if __name__ == "__main__":
    test_ts_parsing()
