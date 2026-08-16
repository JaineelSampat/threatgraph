from app.models.responses import SearchResponse
from app.repositories import search_repository

MIN_QUERY_LENGTH = 2
MAX_RESULTS = 50


def search(query: str, limit: int = 25) -> SearchResponse:
    trimmed = query.strip()
    if len(trimmed) < MIN_QUERY_LENGTH:
        return SearchResponse(query=trimmed, count=0, results=[])

    clamped_limit = max(1, min(limit, MAX_RESULTS))
    return search_repository.search_entities(trimmed.lower(), clamped_limit)
