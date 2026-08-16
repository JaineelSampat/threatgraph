from app.repositories import entity_repository, investigation_repository, search_repository
from app.repositories.base import to_entity_summary


def test_to_entity_summary_uses_correct_label_property():
    props = {"id": "vu-01", "cve": "CVE-2023-91000", "severity": "Critical", "affected_product": "Apex Mail Gateway"}
    summary = to_entity_summary(props, "Vulnerability")
    assert summary.label == "CVE-2023-91000"
    assert summary.subtitle == "Critical"
    assert summary.entity_type == "Vulnerability"


def test_get_entity_returns_none_when_not_found(db_stub):
    db_stub.add([])
    result = entity_repository.get_entity("does-not-exist")
    assert result is None


def test_get_entity_maps_row_to_summary(db_stub):
    db_stub.add([{"properties": {"id": "ta-01", "name": "GRAYWING SPIDER", "motivation": "Financial Gain"}, "entity_type": "ThreatActor"}])
    result = entity_repository.get_entity("ta-01")
    assert result is not None
    assert result.id == "ta-01"
    assert result.label == "GRAYWING SPIDER"
    assert result.entity_type == "ThreatActor"


def test_get_related_entities_reports_direction(db_stub):
    db_stub.add([
        {
            "relationship_type": "USES",
            "direction": "outgoing",
            "properties": {"id": "mw-01", "name": "GraniteLocker", "type": "Ransomware"},
            "entity_type": "Malware",
        },
        {
            "relationship_type": "ASSOCIATED_WITH",
            "direction": "incoming",
            "properties": {"id": "cm-01", "name": "Operation Coldharbor", "year": 2023},
            "entity_type": "Campaign",
        },
    ])
    related = entity_repository.get_related_entities("ta-01")
    assert len(related) == 2
    assert related[0].direction == "outgoing"
    assert related[0].entity.entity_type == "Malware"
    assert related[1].direction == "incoming"


def test_list_entities_paginates_and_orders(db_stub):
    db_stub.add([{"total": 12}])
    db_stub.add([
        {"properties": {"id": "ta-01", "name": "GRAYWING SPIDER"}, "entity_type": "ThreatActor"},
    ])
    result = entity_repository.list_entities("ThreatActor", limit=1, offset=0)
    assert result.total == 12
    assert result.limit == 1
    assert len(result.results) == 1

    # the second query must bind the pagination + ordering parameters
    query, params = db_stub.calls[1]
    assert params == {"order_prop": "name", "offset": 0, "limit": 1}
    assert "ORDER BY n[$order_prop]" in query


def test_search_entities_binds_parameters_not_string_concat(db_stub):
    db_stub.add([{"properties": {"id": "mw-01", "name": "GraniteLocker"}, "entity_type": "Malware"}])
    response = search_repository.search_entities("granite", limit=10)
    assert response.count == 1
    query, params = db_stub.calls[0]
    assert params["search"] == "granite"
    assert params["limit"] == 10
    # the search term must never be interpolated directly into the query text
    assert "granite" not in query


def test_campaign_trail_builds_graph_with_edges(db_stub):
    db_stub.add([
        {
            "actor": {"id": "ta-01", "name": "GRAYWING SPIDER"},
            "campaign": {"id": "cm-01", "name": "Operation Coldharbor", "year": 2023},
            "organization": {"id": "og-01", "name": "Meridian Capital Group"},
            "malware": [{"id": "mw-01", "name": "GraniteLocker"}],
        }
    ])
    results, graph = investigation_repository.campaign_trail("ta-01")
    assert len(results) == 1
    assert results[0].actor.id == "ta-01"
    assert results[0].malware[0].id == "mw-01"
    # 4 nodes: actor, campaign, org, malware
    assert len(graph.nodes) == 4
    # 3 edges: campaign->actor, campaign->org, malware->campaign
    assert len(graph.edges) == 3


def test_reachability_reports_hop_count(db_stub):
    db_stub.add([
        {"properties": {"id": "og-05", "name": "Solvane Energy Partners"}, "hops": 2, "path_labels": ["ThreatActor", "Campaign", "Organization"]}
    ])
    hits = investigation_repository.reachability("ta-01", max_hops=3)
    assert len(hits) == 1
    assert hits[0].hop_count == 2
    assert hits[0].organization.id == "og-05"
