from fastapi import APIRouter

from app import db

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict:
    db_ok = db.verify_connectivity()
    return {
        "status": "ok" if db_ok else "degraded",
        "database_connected": db_ok,
    }
