"""
Feedback route — POST /feedback.
"""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from feedback.store import feedback_store

router = APIRouter(tags=["feedback"])


class FeedbackRequest(BaseModel):
    session_id: str = Field(default="default", description="Session ID")
    query: str = Field(..., min_length=1, description="The query that was asked")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    comment: str = Field(default="", description="Optional comment")


@router.post("/feedback")
def submit_feedback(request: FeedbackRequest) -> dict:
    entry = feedback_store.add(
        session_id=request.session_id,
        query=request.query,
        rating=request.rating,
        comment=request.comment,
    )
    return {
        "status": "ok",
        "feedback_id": entry["id"],
        "message": "Thank you for your feedback!",
    }
