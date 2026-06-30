import os
from knowledge_graph.ingestor import GraphIngestor
from knowledge_graph.neo4j_client import Neo4jGraphManager
from knowledge_graph.qdrant_client import QdrantVectorManager
from knowledge_graph.embedder import MockEmbedder

from parser_core.factory import ParserFactory
from python_parser.parser import PythonParser
from metadata_extractor.factory import ExtractorFactory
import python_extractor as python_ext


def test_ingest():
    print("Initializing Managers...")
    neo4j = Neo4jGraphManager("bolt://localhost:7687", "neo4j", "aiekp_password")
    qdrant = QdrantVectorManager(host="localhost", port=6333)
    embedder = MockEmbedder()

    ingestor = GraphIngestor(
        neo4j_manager=neo4j, qdrant_manager=qdrant, embedder=embedder
    )

    parser_factory = ParserFactory()
    parser_factory.register_parser(PythonParser())

    extractor_factory = ExtractorFactory()
    extractor_factory.register_extractor("python", python_ext.PythonExtractor())

    repo_path = r"D:\AIEKP\plugins\python_parser"

    for root, _, files in os.walk(repo_path):
        if ".git" in root or ".venv" in root or "__pycache__" in root:
            continue
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith(".py"):
                try:
                    parser = parser_factory.get_parser(".py")
                    with open(file_path, "rb") as f:
                        file_content = f.read()
                    parse_result = parser.parse(file_content)

                    extractor = extractor_factory.get_extractor(".py")
                    extract_result = extractor.extract(parse_result, file_path)

                    ingestor.ingest(extract_result)
                    print(f"Successfully ingested {file_path}")
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
                    import traceback

                    traceback.print_exc()


if __name__ == "__main__":
    test_ingest()
