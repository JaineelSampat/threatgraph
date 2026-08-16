"""
Query 3 - Multi-Hop Investigation, and Query 4 - Relationally Awkward Query.

Query 3 ("campaign trail") walks a fixed, meaningful shape:
    ThreatActor <-[:ASSOCIATED_WITH]- Campaign -[:TARGETS]-> Organization
with the Malware used in that campaign pulled in as a branch. This is
the kind of question an analyst asks constantly: "what did this actor
touch, and through what campaign?"

Query 4 ("reachability") is deliberately open-ended: instead of a fixed
relationship shape, it asks "what organizations sit within N hops of
this actor, through *any* combination of relationship types?" Answering
that in a relational database means a hand-written recursive CTE (or a
UNION of one CTE per relationship-type join path) that has to be
rewritten every time the schema grows a new relationship type. In
Cypher it's a single variable-length pattern.
"""
from app import db
from app.models.responses import (
    CampaignTrailResult,
    EntitySummary,
    GraphEdge,
    GraphNode,
    GraphPath,
    ReachabilityHit,
)
from app.repositories.base import to_entity_summary

_TRAVERSABLE_RELATIONSHIPS = (
    "USES|EXPLOITS|USES_TECHNIQUE|PART_OF|TARGETS|ASSOCIATED_WITH|INDICATES|RELATED_TO"
)


def campaign_trail(actor_id: str) -> tuple[list[CampaignTrailResult], GraphPath]:
    query = """
        MATCH (ta:ThreatActor {id: $actorId})<-[:ASSOCIATED_WITH]-(c:Campaign)-[:TARGETS]->(o:Organization)
        OPTIONAL MATCH (c)<-[:PART_OF]-(m:Malware)
        RETURN properties(ta) AS actor,
               properties(c) AS campaign,
               properties(o) AS organization,
               collect(DISTINCT properties(m)) AS malware
        ORDER BY c.year DESC
    """
    rows = db.run_query(query, {"actorId": actor_id})

    results: list[CampaignTrailResult] = []
    nodes: dict[str, GraphNode] = {}
    edges: list[GraphEdge] = []

    for row in rows:
        actor = to_entity_summary(row["actor"], "ThreatActor")
        campaign = to_entity_summary(row["campaign"], "Campaign")
        org = to_entity_summary(row["organization"], "Organization")
        malware = [to_entity_summary(m, "Malware") for m in row["malware"] if m is not None]

        results.append(
            CampaignTrailResult(actor=actor, campaign=campaign, organization=org, malware=malware)
        )

        for summary in [actor, campaign, org, *malware]:
            nodes[summary.id] = GraphNode(id=summary.id, entity_type=summary.entity_type, label=summary.label)

        edges.append(GraphEdge(source=campaign.id, target=actor.id, relationship_type="ASSOCIATED_WITH"))
        edges.append(GraphEdge(source=campaign.id, target=org.id, relationship_type="TARGETS"))
        for m in malware:
            edges.append(GraphEdge(source=m.id, target=campaign.id, relationship_type="PART_OF"))

    graph = GraphPath(nodes=list(nodes.values()), edges=edges)
    return results, graph


def reachability(actor_id: str, max_hops: int, target_type: str = "Organization") -> list[ReachabilityHit]:
    # target_type is validated by the route/service layer against the
    # same EntityType Literal used everywhere else before it ever reaches
    # this f-string, for the same reason entity_type is safe to embed in
    # entity_repository.py - see that file's module docstring.
    query = f"""
        MATCH p = (ta:ThreatActor {{id: $actorId}})-[:{_TRAVERSABLE_RELATIONSHIPS}*1..{max_hops}]-(target:{target_type})
        WHERE ta <> target
        WITH target, min(length(p)) AS hops, head(collect(p)) AS samplePath
        RETURN properties(target) AS properties,
               hops,
               [n IN nodes(samplePath) | labels(n)[0]] AS path_labels
        ORDER BY hops ASC, target.name ASC
        LIMIT 25
    """
    rows = db.run_query(query, {"actorId": actor_id})
    return [
        ReachabilityHit(
            organization=to_entity_summary(row["properties"], target_type),  # type: ignore[arg-type]
            hop_count=row["hops"],
            path_labels=row["path_labels"],
        )
        for row in rows
    ]
