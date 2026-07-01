from pydantic import BaseModel
from typing import List, Optional

class RetrievalIntent(BaseModel):
    query: str
    target_types: List[str]  # e.g., ["class", "method", "function", "module"]
    semantic_keywords: List[str]
    graph_expansion_depth: int = 1

class EvidenceNode(BaseModel):
    id: str
    name: str
    type: str
    content: Optional[str] = None
    properties: dict = {}
    relationships: List[dict] = []

class EvidencePayload(BaseModel):
    original_query: str
    intent: RetrievalIntent
    nodes: List[EvidenceNode]
    summary: str
