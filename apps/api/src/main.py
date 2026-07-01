import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from fastapi import FastAPI  # noqa: E402
from src.dependencies import init_dependencies, close_dependencies  # noqa: E402
from src.routers import health, scanner, ingest, search, graph, context  # noqa: E402


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize Neo4j, Qdrant, etc.
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

app.include_router(health.router)
app.include_router(scanner.router)
app.include_router(ingest.router)
app.include_router(search.router)
app.include_router(graph.router)
app.include_router(context.router)


@app.get("/")
async def root():
    return {"message": "Welcome to AIEKP API"}
