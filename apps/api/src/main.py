# ruff: noqa: E402
import json
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# Load global configuration
global_config_file = Path.home() / ".aiekp" / "config.json"
if global_config_file.exists():
    try:
        with open(global_config_file, "r") as f:
            global_config = json.load(f)
            for k, v in global_config.items():
                if k not in os.environ:
                    os.environ[k] = str(v)
    except Exception as e:
        print(f"Warning: Failed to load global config from {global_config_file}: {e}")

from fastapi import FastAPI, Depends  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from strawberry.fastapi import GraphQLRouter  # noqa: E402
from src.dependencies import init_dependencies, close_dependencies, verify_api_key  # noqa: E402
from src.routers import (
    health,
    scanner,
    ingest,
    search,
    graph,
    context,
    reason,
    stats,
    rules,
    docs,
    feedback,
)  # noqa: E402
from src.config import settings  # noqa: E402
from src.graphql_api.schema import schema  # noqa: E402


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize Neo4j, Qdrant, etc.
    from src.telemetry.database import init_db

    init_db()
    await init_dependencies()
    yield
    # Cleanup connections
    await close_dependencies()


app = FastAPI(
    title="AIEKP Knowledge Engine API",
    description="API for managing and querying the AI Engineering Knowledge Platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)  # Healthcheck doesn't need API Key

# Protected routers
protected_dependencies = [Depends(verify_api_key)]
app.include_router(scanner.router, dependencies=protected_dependencies)
app.include_router(ingest.router, dependencies=protected_dependencies)
app.include_router(search.router, dependencies=protected_dependencies)
app.include_router(graph.router, dependencies=protected_dependencies)
app.include_router(context.router, dependencies=protected_dependencies)
app.include_router(reason.router, dependencies=protected_dependencies)
app.include_router(stats.router, dependencies=protected_dependencies)
app.include_router(rules.router, dependencies=protected_dependencies)
app.include_router(docs.router, dependencies=protected_dependencies)
app.include_router(feedback.router, dependencies=protected_dependencies)

graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql", dependencies=protected_dependencies)


@app.get("/")
async def root():
    return {"message": "Welcome to AIEKP API"}
