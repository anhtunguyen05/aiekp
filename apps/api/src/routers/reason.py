from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from src.dependencies import get_reasoning_service
from reasoning_engine.ports.inbound import IReasoningService
from reasoning_engine.domain.models import ReasoningRequest, ReasoningResult
from src.telemetry.tracer import SimpleTracer
from src.telemetry.database import get_telemetry_db
import json

router = APIRouter(prefix="/reason", tags=["Reasoning"])


def save_trace(tracer: SimpleTracer):
    """Background task to save trace"""
    db = next(get_telemetry_db())
    tracer.persist(db)


@router.post("/", response_model=ReasoningResult)
async def process_reasoning(
    request: ReasoningRequest,
    background_tasks: BackgroundTasks,
    reasoning_service: IReasoningService = Depends(get_reasoning_service),
):
    tracer = SimpleTracer(session_id=request.session_id)
    tracer.set_query(request.query)
    try:
        with tracer.span("process_query"):
            result = await reasoning_service.process_query(request)
        
        # We can add metadata like sources used
        tracer.metadata["sources_used"] = result.sources_used
        return result
    except Exception as e:
        tracer.metadata["error"] = str(e)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        background_tasks.add_task(save_trace, tracer)


@router.post("/stream")
async def reason_stream(
    request: ReasoningRequest, 
    background_tasks: BackgroundTasks,
    reasoning_service=Depends(get_reasoning_service)
):
    """
    Process a natural language query and stream the response using Server-Sent Events (SSE).
    """
    tracer = SimpleTracer(session_id=request.session_id)
    tracer.set_query(request.query)

    async def sse_generator():
        # Yield the trace ID immediately so the frontend can associate feedback
        yield f"data: {json.dumps({'type': 'trace', 'trace_id': tracer.trace_id})}\n\n"
        
        try:
            full_answer = ""
            with tracer.span("stream_process_query"):
                async for chunk in reasoning_service.stream_process_query(request):
                    # Format as SSE
                    if isinstance(chunk, dict):
                        payload = json.dumps(chunk)
                        if "content" in chunk and chunk["type"] == "message":
                            full_answer += chunk["content"]
                    else:
                        payload = json.dumps({"type": "message", "content": str(chunk)})
                        full_answer += str(chunk)
                    yield f"data: {payload}\n\n"
            tracer.metadata["answer"] = full_answer
        except Exception as e:
            tracer.metadata["error"] = str(e)
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
        finally:
            yield "data: [DONE]\n\n"
            save_trace(tracer) # We call it here because BackgroundTasks don't work reliably with StreamingResponse completion in all ASGI servers, so we just run it directly at the end of the stream.

    return StreamingResponse(sse_generator(), media_type="text/event-stream")
