from fastapi import APIRouter

from services.operations_service import build_analytics_payload

router = APIRouter(tags=["analytics"])


@router.get("/analytics")
def analytics() -> dict:
    return build_analytics_payload()
