"""
Sits between the routes and the repository layer.

The repository layer only knows how to run Cypher and shape rows into
Pydantic models. This layer owns things that aren't database concerns:
turning "no such id" into a typed exception the route layer can map to
a 404, clamping pagination inputs, and composing two repository calls
(entity + its neighbors) into one EntityDetail response.
"""
from app.models.entities import EntityType
from app.models.responses import EntityDetail, EntityListResponse
from app.repositories import entity_repository
from app.services.exceptions import EntityNotFoundError

MAX_PAGE_SIZE = 100


def browse_entities(entity_type: EntityType, limit: int, offset: int) -> EntityListResponse:
    clamped_limit = max(1, min(limit, MAX_PAGE_SIZE))
    clamped_offset = max(0, offset)
    return entity_repository.list_entities(entity_type, clamped_limit, clamped_offset)


def get_entity_detail(entity_id: str) -> EntityDetail:
    entity = entity_repository.get_entity(entity_id)
    if entity is None:
        raise EntityNotFoundError(entity_id)

    related = entity_repository.get_related_entities(entity_id)
    return EntityDetail(entity=entity, related=related)
