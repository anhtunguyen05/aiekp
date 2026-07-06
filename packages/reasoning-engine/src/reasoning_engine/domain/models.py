from typing import List, Optional, Any, Dict
from pydantic import BaseModel


class ReasoningRequest(BaseModel):
    query: str
    session_id: str


class ReasoningResult(BaseModel):
    answer: str
    sources_used: List[Dict[str, Any]]
    confidence_score: float


# This is the state passed around in LangGraph
class ReasoningState(BaseModel):
    query: str
    session_id: str
    context_accumulated: List[Dict[str, Any]] = []
    is_context_sufficient: bool = False
    iterations: int = 0
    final_answer: Optional[str] = None
    sources_used: List[Dict[str, Any]] = []
    confidence_score: float = 0.0
    error: Optional[str] = None
