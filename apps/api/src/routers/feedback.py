from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.telemetry.database import get_telemetry_db
from src.telemetry.models import Feedback

router = APIRouter(prefix="/feedback", tags=["Feedback"])


class FeedbackRequest(BaseModel):
    trace_id: str
    score: int
    comment: str = None


@router.post("/")
async def submit_feedback(request: FeedbackRequest, db=Depends(get_telemetry_db)):
    try:
        feedback = Feedback(
            trace_id=request.trace_id, score=request.score, comment=request.comment
        )
        db.add(feedback)
        db.commit()
        return {"status": "success", "message": "Feedback recorded."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
