from fastapi import APIRouter, Depends, HTTPException
from src.dependencies import get_reasoning_service
from reasoning_engine.ports.inbound import IReasoningService
from reasoning_engine.domain.models import ReasoningRequest, ReasoningResult

router = APIRouter(prefix="/reason", tags=["Reasoning"])


@router.post("/", response_model=ReasoningResult)
async def process_reasoning(
    request: ReasoningRequest,
    reasoning_service: IReasoningService = Depends(get_reasoning_service),
):
    try:
        result = await reasoning_service.process_query(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
