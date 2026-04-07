from fastapi import APIRouter

from services.seller_service import build_insights_payload

router = APIRouter(tags=["insights"])


@router.get("/insights")
def insights() -> dict:
    return build_insights_payload()
