"""
Query 1 (partly), Query 2, and Query 5 from the assignment brief live here:
- entity detail (properties + immediate relationships)
- related/connected entities
- paginated browsing of a single entity type

A note on labels and relationship types: the Bolt protocol only lets you
bind *property values* as query parameters - node labels and
relationship types can't be parameterized by the driver. Every query
below that embeds a label (e.g. f":{entity_type}") only ever receives
`entity_type` after FastAPI has validated it against the `EntityType`
Literal in `app/models/entities.py`, so the value is one of seven fixed,
hardcoded strings by the time it reaches Cypher - never arbitrary user
input. All *values* (ids, search text, limits, offsets) are still bound
as real parameters.
"""
from typing import Any

from app import db
from app.models.entities import DISPLAY_PROPERTY, EntityType
from app.models.responses import EntityListResponse, EntitySummary, RelatedEntity
from app.repositories.base import to_entity_summary


def list_entities(entity_type: EntityType, limit: int, offset: int) -> EntityListResponse:
    order_prop = DISPLAY_PROPERTY[entity_type]

    count_query = f"MATCH (n:{entity_type}) RETURN count(n) AS total"
    total = db.run_query(count_query)[0]["total"]

    list_query = f"""
        MATCH (n:{entity_type})
        RETURN properties(n) AS properties, labels(n)[0] AS entity_type
        ORDER BY n[$order_prop]
        SKIP $offset
        LIMIT $limit
    """
    rows = db.run_query(list_query, {"order_prop": order_prop, "offset": offset, "limit": limit})
    results = [to_entity_summary(row["properties"], row["entity_type"]) for row in rows]

    return EntityListResponse(
        entity_type=entity_type,
        total=total,
        limit=limit,
        offset=offset,
        results=results,
    )


def get_entity(entity_id: str) -> EntitySummary | None:
    query = """
        MATCH (n {id: $id})
        RETURN properties(n) AS properties, labels(n)[0] AS entity_type
        LIMIT 1
    """
    rows = db.run_query(query, {"id": entity_id})
    if not rows:
        return None
    return to_entity_summary(rows[0]["properties"], rows[0]["entity_type"])


def get_related_entities(entity_id: str, limit: int = 50) -> list[RelatedEntity]:
    """Every direct neighbor of a node, regardless of relationship type or direction.

    `startNode(r) = n` tells us whether the relationship points away from
    or into the entity we're inspecting, so the UI can render an arrow
    in the right direction.
    """
    query = """
        MATCH (n {id: $id})-[r]-(neighbor)
        RETURN type(r) AS relationship_type,
               CASE WHEN startNode(r) = n THEN 'outgoing' ELSE 'incoming' END AS direction,
               properties(neighbor) AS properties,
               labels(neighbor)[0] AS entity_type
        LIMIT $limit
    """
    rows = db.run_query(query, {"id": entity_id, "limit": limit})
    return [
        RelatedEntity(
            relationship_type=row["relationship_type"],
            direction=row["direction"],
            entity=to_entity_summary(row["properties"], row["entity_type"]),
        )
        for row in rows
    ]
