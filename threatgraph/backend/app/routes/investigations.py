from fastapi import APIRouter, Query

from app.models.responses import CampaignTrailResponse, ReachabilityResponse
from app.services import investigation_service

router = APIRouter(prefix="/api/investigations", tags=["investigations"])


@router.get("/campaign-trail/{actor_id}", response_model=CampaignTrailResponse)
def campaign_trail(actor_id: str) -> CampaignTrailResponse:
    """Query 3 - the mandatory multi-hop investigation.

    ThreatActor <- Campaign -> Organization, with the Malware used in
    that campaign attached as context.
    """
    return investigation_service.get_campaign_trail(actor_id)


@router.get("/reachability/{actor_id}", response_model=ReachabilityResponse)
def reachability(
    actor_id: str,
    max_hops: int = Query(3, ge=1, le=5, description="How many relationship hops to traverse"),
) -> ReachabilityResponse:
    """Query 4 - the relationally-awkward query.

    Every Organization reachable from this actor within `max_hops`,
    through any combination of relationship types.
    """
    return investigation_service.get_reachability(actor_id, max_hops)
