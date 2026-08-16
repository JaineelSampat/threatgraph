"""
Query 1 - Entity Search.

Every node is seeded with a lowercase `search_text` property (its name/
identifier plus a couple of useful synonyms, see scripts/seed_data.py).
Searching against that precomputed property, rather than re-lowercasing
several different display properties at query time, keeps this query
index-friendly and identical regardless of which of the seven node
types matches.
"""
from app import db
from app.models.responses import EntitySummary, SearchResponse
from app.repositories.base import to_entity_summary

_SEARCHABLE_LABELS = [
    "ThreatActor",
    "Malware",
    "Vulnerability",
    "Technique",
    "Campaign",
    "Organization",
    "Indicator",
]


def search_entities(search_term: str, limit: int = 25) -> SearchResponse:
    query = """
        MATCH (n)
        WHERE any(lbl IN labels(n) WHERE lbl IN $labels)
          AND n.search_text CONTAINS toLower($search)
        RETURN properties(n) AS properties, labels(n)[0] AS entity_type
        LIMIT $limit
    """
    rows = db.run_query(
        query,
        {"labels": _SEARCHABLE_LABELS, "search": search_term, "limit": limit},
    )
    results: list[EntitySummary] = [
        to_entity_summary(row["properties"], row["entity_type"]) for row in rows
    ]
    return SearchResponse(query=search_term, count=len(results), results=results)
