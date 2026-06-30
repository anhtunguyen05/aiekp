from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class SearchRequest(BaseModel):
    query: str = Field(..., description="The semantic search query")
    top_k: int = Field(5, description="Number of results to return")
    node_labels: Optional[List[str]] = Field(
        None, description="Filter by these graph node labels"
    )


class SearchResultItem(BaseModel):
    node_id: str
    content: str
    score: float
    metadata: Dict[str, Any]


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResultItem]


class IngestRequest(BaseModel):
    repo_path: str = Field(..., description="Absolute path to the repository to ingest")


class IngestResponse(BaseModel):
    status: str
    message: str
    job_id: Optional[str] = None
