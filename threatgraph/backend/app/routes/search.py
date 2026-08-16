from fastapi import APIRouter, Query

from app.models.responses import SearchResponse
from app.services import search_service

router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("", response_model=SearchResponse)
def search(
    q: str = Query(..., min_length=1, description="Free-text search across all entity types"),
    limit: int = Query(25, ge=1, le=50),
) -> SearchResponse:
    return search_service.search(q, limit)
