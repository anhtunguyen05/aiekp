from parser_core.factory import ParserFactory
from python_parser.parser import PythonParser
from metadata_extractor.factory import ExtractorFactory
import python_extractor as python_ext
from knowledge_graph import Neo4jGraphManager, QdrantVectorManager, GraphIngestor

def main():
    # 1. Setup Parser (Phase 2)
    parser_factory = ParserFactory()
    parser_factory.register_parser(PythonParser())
    parser = parser_factory.get_parser(".py")
    
    # 2. Setup Extractor (Phase 3)
    extractor_factory = ExtractorFactory()
    python_ext.register(extractor_factory)
    extractor = extractor_factory.get_extractor(".py")
    
    # 3. Sample code
    sample_code = b"""
def sum_numbers(a: int, b: int) -> int:
    \"\"\"Calculates the sum of two integers.\"\"\"
    return a + b
    
class Database:
    \"\"\"Handles database connections and queries.\"\"\"
    def connect(self):
        \"\"\"Establishes the connection to the database.\"\"\"
        pass
"""

    print("--- 1. PARSING CODE ---")
    ast_root = parser.parse(sample_code)
    
    print("--- 2. EXTRACTING METADATA ---")
    file_metadata = extractor.extract(ast_root, file_path="sample_db.py")
    
    print("--- 3. INITIALIZING GRAPH & VECTOR MANAGERS ---")
    # Make sure neo4j and qdrant are running via docker-compose up -d
    # Credentials from docker-compose.yml: neo4j/aiekp_password
    neo4j_manager = Neo4jGraphManager("bolt://localhost:7687", "neo4j", "aiekp_password")
    qdrant_manager = QdrantVectorManager(host="localhost", port=6333)
    from knowledge_graph.embedder import MockEmbedder
    embedder = MockEmbedder(size=384)
    
    ingestor = GraphIngestor(
        neo4j_manager=neo4j_manager,
        qdrant_manager=qdrant_manager,
        embedder=embedder
    )
    
    print("--- 4. INGESTING INTO NEO4J AND QDRANT ---")
    ingestor.ingest(file_metadata)
    
    print("Ingestion completed successfully!")
    neo4j_manager.close()

if __name__ == "__main__":
    main()
