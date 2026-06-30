from fastapi import APIRouter, BackgroundTasks, Depends
import os
from knowledge_graph import GraphIngestor
from src.dependencies import get_ingestor
from src.schemas import IngestRequest, IngestResponse

router = APIRouter(prefix="/ingest", tags=["ingest"])


def process_repository(repo_path: str, ingestor: GraphIngestor):
    # This simulates a background job for parsing and ingesting the repo
    # using our RepositoryScanner and GraphIngestor.
    # Note: Scanner currently relies on prisma which requires async,
    # but the ingestor is synchronous. We would need an async compatible loop,
    # or handle the DB state outside.

    # For now, let's just do a simple file traversal (mocking the scanner if needed)
    # or instantiate the parser and extractor pipelines here.

    from parser_core.factory import ParserFactory
    from python_parser.parser import PythonParser
    from metadata_extractor.factory import ExtractorFactory
    import python_extractor as python_ext

    # 1. Setup Parser Factory
    parser_factory = ParserFactory()
    parser_factory.register_parser(PythonParser())

    # 2. Setup Extractor Factory
    extractor_factory = ExtractorFactory()
    extractor_factory.register_extractor("python", python_ext.PythonExtractor())

    for root, _, files in os.walk(repo_path):
        # Skip common directories
        if ".git" in root or ".venv" in root or "__pycache__" in root:
            continue

        for file in files:
            file_path = os.path.join(root, file)
            # Process python files
            if file.endswith(".py"):
                try:
                    # Parse
                    parser = parser_factory.get_parser(".py")
                    with open(file_path, "rb") as f:
                        file_content = f.read()
                    parse_result = parser.parse(file_content)

                    # Extract Metadata
                    extractor = extractor_factory.get_extractor(".py")
                    extract_result = extractor.extract(parse_result, file_path)

                    # Ingest
                    ingestor.ingest(extract_result)
                    print(f"Successfully ingested {file_path}")
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")


@router.post("/", response_model=IngestResponse)
async def trigger_ingestion(
    request: IngestRequest,
    background_tasks: BackgroundTasks,
    ingestor: GraphIngestor = Depends(get_ingestor),
):
    repo_path = os.path.abspath(request.repo_path)
    if not os.path.exists(repo_path):
        return IngestResponse(
            status="error", message=f"Path {repo_path} does not exist."
        )

    background_tasks.add_task(process_repository, repo_path, ingestor)
    return IngestResponse(
        status="accepted",
        message=f"Ingestion started for {repo_path} in the background.",
    )
