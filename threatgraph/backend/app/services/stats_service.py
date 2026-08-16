from app.models.responses import DashboardStats
from app.repositories import stats_repository


def get_dashboard_stats() -> DashboardStats:
    return stats_repository.get_dashboard_stats()
