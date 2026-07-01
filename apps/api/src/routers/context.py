from fastapi import APIRouter, Depends
from pydantic import BaseModel
from context_engine.domain.models import EvidencePayload
from context_engine.ports.inbound import IContextService
from src.dependencies import get_context_service

router = APIRouter(prefix="/context", tags=["Context Engine"])

class ContextRequest(BaseModel):
    query: str

@router.post("/retrieve", response_model=EvidencePayload)
async def retrieve_context(
    request: ContextRequest,
    context_service: IContextService = Depends(get_context_service)
):
    """
    Analyzes user intent and retrieves the corresponding architectural 
    context (evidence nodes) from the Knowledge Graph.
    """
    payload = await context_service.retrieve_context(request.query)
    return payload
