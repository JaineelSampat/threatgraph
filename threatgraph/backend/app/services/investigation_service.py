from app.models.responses import CampaignTrailResponse, ReachabilityResponse
from app.repositories import entity_repository, investigation_repository
from app.services.exceptions import EntityNotFoundError

MAX_HOPS = 5
MIN_HOPS = 1


def _assert_actor_exists(actor_id: str) -> None:
    entity = entity_repository.get_entity(actor_id)
    if entity is None or entity.entity_type != "ThreatActor":
        raise EntityNotFoundError(actor_id)


def get_campaign_trail(actor_id: str) -> CampaignTrailResponse:
    _assert_actor_exists(actor_id)
    results, graph = investigation_repository.campaign_trail(actor_id)
    return CampaignTrailResponse(actor_id=actor_id, results=results, graph=graph)


def get_reachability(actor_id: str, max_hops: int) -> ReachabilityResponse:
    _assert_actor_exists(actor_id)
    clamped_hops = max(MIN_HOPS, min(max_hops, MAX_HOPS))
    hits = investigation_repository.reachability(actor_id, clamped_hops)
    return ReachabilityResponse(actor_id=actor_id, max_hops=clamped_hops, hits=hits)
