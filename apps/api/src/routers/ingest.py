import asyncio
import json
from fastapi import APIRouter, BackgroundTasks, Depends, Request
from fastapi.responses import StreamingResponse
import os
from knowledge_graph import GraphIngestor
from src.dependencies import get_ingestor, get_current_user, CurrentUser
from src.schemas import IngestRequest, IngestResponse

router = APIRouter(prefix="/ingest", tags=["ingest"])

STATUS_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "scan_status.json")


def load_status():
    if os.path.exists(STATUS_FILE):
        try:
            with open(STATUS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_status(status_dict):
    try:
        with open(STATUS_FILE, "w", encoding="utf-8") as f:
            json.dump(status_dict, f, indent=2)
    except Exception as e:
        print(f"Failed to save scan status: {e}")


# In-memory store for ingestion progress, backed by STATUS_FILE
scan_status = load_status()


def process_repository(repo_path: str, ingestor: GraphIngestor, tenant_id: str):
    # This simulates a background job for parsing and ingesting the repo
    # using our RepositoryScanner and GraphIngestor.
    # Note: Scanner currently relies on prisma which requires async,
    # but the ingestor is synchronous. We would need an async compatible loop,
    # or handle the DB state outside.

    # For now, let's just do a simple file traversal (mocking the scanner if needed)
    # or instantiate the parser and extractor pipelines here.

    from parser_core.factory import ParserFactory
    from python_parser.parser import PythonParser
    import typescript_parser.parser as ts_parser

    from metadata_extractor.factory import ExtractorFactory
    import python_extractor as python_ext
    import typescript_extractor.extractor as ts_ext

    # 1. Setup Parser Factory
    parser_factory = ParserFactory()
    parser_factory.register_parser(PythonParser())
    parser_factory.register_parser(ts_parser.TypescriptParser())

    # 2. Setup Extractor Factory
    extractor_factory = ExtractorFactory()
    extractor_factory.register_extractor("python", python_ext.PythonExtractor())
    extractor_factory.register_extractor("typescript", ts_ext.TypescriptExtractor())

    # Count total files first to compute progress
    supported_extensions = (".py", ".ts", ".tsx", ".js", ".jsx")
    target_files = []
    for root, _, files in os.walk(repo_path):
        if (
            ".git" in root
            or ".venv" in root
            or "__pycache__" in root
            or "node_modules" in root
            or ".next" in root
        ):
            continue
        for file in files:
            if file.endswith(supported_extensions):
                target_files.append(os.path.join(root, file))

    total_files = len(target_files)

    scan_status[repo_path] = {
        "status": "running",
        "progress": 0,
        "current_file": "",
        "total_files": total_files,
        "processed_files": 0,
    }

    processed_files = 0
    for file_path in target_files:
        scan_status[repo_path]["current_file"] = file_path
        try:
            # Parse
            _, ext = os.path.splitext(file_path)
            parser = parser_factory.get_parser(ext)
            with open(file_path, "rb") as f:
                file_content = f.read()
            parse_result = parser.parse(file_content, file_path=file_path)

            # Extract Metadata
            language = "python" if ext == ".py" else "typescript"
            extractor = extractor_factory.get_extractor(language)
            extract_result = extractor.extract(parse_result, file_path)

            # Ingest
            ingestor.ingest(extract_result, tenant_id)
            print(f"Successfully ingested {file_path}")
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

        processed_files += 1
        scan_status[repo_path]["processed_files"] = processed_files
        scan_status[repo_path]["progress"] = (
            int((processed_files / total_files) * 100) if total_files > 0 else 100
        )

        if processed_files % 10 == 0:
            save_status(scan_status)

    scan_status[repo_path]["status"] = "completed"
    scan_status[repo_path]["progress"] = 100
    scan_status[repo_path]["current_file"] = ""
    save_status(scan_status)


@router.post("/", response_model=IngestResponse)
async def trigger_ingestion(
    request: IngestRequest,
    background_tasks: BackgroundTasks,
    current_user: CurrentUser = Depends(get_current_user),
    ingestor: GraphIngestor = Depends(get_ingestor),
):
    repo_path = os.path.abspath(request.repo_path)
    if not os.path.exists(repo_path):
        return IngestResponse(
            status="error", message=f"Path {repo_path} does not exist."
        )

    scan_status[repo_path] = {
        "status": "starting",
        "progress": 0,
        "current_file": "",
        "total_files": 0,
        "processed_files": 0,
    }
    save_status(scan_status)

    background_tasks.add_task(
        process_repository, repo_path, ingestor, current_user.tenant_id
    )
    return IngestResponse(
        status="accepted",
        message=f"Ingestion started for {repo_path} in the background.",
    )


@router.get("/progress")
async def get_progress(request: Request, repo_path: str):
    """
    SSE endpoint to stream ingestion progress.
    Usage: /ingest/progress?repo_path=/absolute/path/to/repo
    """
    repo_path = os.path.abspath(repo_path)

    async def event_generator():
        while True:
            # If client disconnects, break
            if await request.is_disconnected():
                break

            status_data = scan_status.get(
                repo_path,
                {
                    "status": "unknown",
                    "progress": 0,
                    "current_file": "",
                    "total_files": 0,
                    "processed_files": 0,
                },
            )

            yield f"data: {json.dumps(status_data)}\n\n"

            if status_data["status"] == "completed" or status_data["status"] == "error":
                break

            await asyncio.sleep(1)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
