from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
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


@router.post("/stream")
async def reason_stream(
    request: ReasoningRequest, reasoning_service=Depends(get_reasoning_service)
):
    """
    Process a natural language query and stream the response using Server-Sent Events (SSE).
    """

    async def sse_generator():
        import json
        async for chunk in reasoning_service.stream_process_query(request):
            # Format as SSE
            payload = json.dumps({"content": chunk})
            yield f"data: {payload}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(sse_generator(), media_type="text/event-stream")
