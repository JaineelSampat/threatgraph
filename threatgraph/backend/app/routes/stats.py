from fastapi import APIRouter

from app.models.responses import DashboardStats
from app.services import stats_service

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("", response_model=DashboardStats)
def get_stats() -> DashboardStats:
    return stats_service.get_dashboard_stats()
