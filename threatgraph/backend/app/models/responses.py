"""Response-shape models for API endpoints (not raw graph nodes)."""
from typing import Any

from pydantic import BaseModel

from app.models.entities import EntityType


class EntitySummary(BaseModel):
    """A lightweight card-sized view of any node, used in lists and search results."""

    id: str
    entity_type: EntityType
    label: str
    subtitle: str | None = None
    properties: dict[str, Any]


class RelatedEntity(BaseModel):
    """One neighbor of a node, with the relationship that connects them."""

    relationship_type: str
    direction: str  # "outgoing" | "incoming"
    entity: EntitySummary


class EntityDetail(BaseModel):
    entity: EntitySummary
    related: list[RelatedEntity]


class SearchResponse(BaseModel):
    query: str
    count: int
    results: list[EntitySummary]


class EntityListResponse(BaseModel):
    entity_type: EntityType
    total: int
    limit: int
    offset: int
    results: list[EntitySummary]


class DashboardStats(BaseModel):
    counts: dict[str, int]
    total_relationships: int
    severity_breakdown: dict[str, int]
    tactic_breakdown: dict[str, int]


class GraphNode(BaseModel):
    id: str
    entity_type: EntityType
    label: str


class GraphEdge(BaseModel):
    source: str
    target: str
    relationship_type: str


class GraphPath(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]


class CampaignTrailResult(BaseModel):
    """Result of the Query 3 multi-hop investigation:
    ThreatActor -> Campaign -> Organization, with Malware used in that campaign.
    """

    actor: EntitySummary
    campaign: EntitySummary
    organization: EntitySummary
    malware: list[EntitySummary]


class CampaignTrailResponse(BaseModel):
    actor_id: str
    results: list[CampaignTrailResult]
    graph: GraphPath


class ReachabilityHit(BaseModel):
    organization: EntitySummary
    hop_count: int
    path_labels: list[str]


class ReachabilityResponse(BaseModel):
    actor_id: str
    max_hops: int
    hits: list[ReachabilityHit]
