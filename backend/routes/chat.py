"""
Chat route — POST /chat.
Updated to pass the FastAPI app instance to ask_rag.
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field, validator

from services.rag_client import ask_rag

router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Customer support query")
    order_id: str = Field(default="", description="Optional order id")
    session_id: str = Field(default="default", description="Session ID for memory")
    use_rewrite: bool = Field(default=True)
    use_mq: bool = Field(default=False)
    use_comp: bool = Field(default=False)

    @validator('query')
    def query_not_whitespace(cls, v):
        stripped = v.strip()
        if not stripped:
            raise ValueError('Query cannot be empty or whitespace-only')
        return stripped


@router.post("/chat")
def chat(request: ChatRequest, req: Request) -> dict:
    try:
        return ask_rag(
            query=request.query,
            order_id=request.order_id,
            session_id=request.session_id,
            use_rewrite=request.use_rewrite,
            use_mq=request.use_mq,
            use_comp=request.use_comp,
            app=req.app,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process chat request: {exc}",
        ) from exc
