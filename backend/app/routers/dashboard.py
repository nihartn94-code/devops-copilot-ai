from fastapi import APIRouter, HTTPException
from backend.app.database import get_dashboard_metrics
from backend.app.models import DashboardStatsResponse

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/stats", response_model=DashboardStatsResponse)
async def get_stats():
    """
    Returns aggregate DevOps Copilot metrics and recent analyses.
    """
    metrics = await get_dashboard_metrics()
    return metrics
