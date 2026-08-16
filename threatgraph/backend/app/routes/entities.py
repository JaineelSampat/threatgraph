from fastapi import APIRouter, Query

from app.models.entities import EntityType
from app.models.responses import EntityDetail, EntityListResponse
from app.services import entity_service

router = APIRouter(prefix="/api/entities", tags=["entities"])


@router.get("", response_model=EntityListResponse)
def browse_entities(
    entity_type: EntityType = Query(..., description="One of the seven graph node types"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> EntityListResponse:
    return entity_service.browse_entities(entity_type, limit, offset)


@router.get("/{entity_id}", response_model=EntityDetail)
def get_entity(entity_id: str) -> EntityDetail:
    return entity_service.get_entity_detail(entity_id)
