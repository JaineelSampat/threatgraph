import pytest
from fastapi.testclient import TestClient

from app.db import DatabaseUnavailableError
from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_health_reports_degraded_when_db_down(client, monkeypatch):
    monkeypatch.setattr("app.db.verify_connectivity", lambda: False)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "degraded", "database_connected": False}


def test_get_entity_404_when_missing(client, db_stub):
    db_stub.add([])  # entity_repository.get_entity finds nothing
    response = client.get("/api/entities/does-not-exist")
    assert response.status_code == 404
    assert "does-not-exist" in response.json()["detail"]


def test_get_entity_detail_combines_entity_and_related(client, db_stub):
    db_stub.add([{"properties": {"id": "ta-01", "name": "GRAYWING SPIDER"}, "entity_type": "ThreatActor"}])
    db_stub.add([
        {
            "relationship_type": "USES",
            "direction": "outgoing",
            "properties": {"id": "mw-01", "name": "GraniteLocker", "type": "Ransomware"},
            "entity_type": "Malware",
        }
    ])
    response = client.get("/api/entities/ta-01")
    assert response.status_code == 200
    body = response.json()
    assert body["entity"]["id"] == "ta-01"
    assert len(body["related"]) == 1
    assert body["related"][0]["entity"]["id"] == "mw-01"


def test_browse_entities_requires_valid_entity_type(client):
    response = client.get("/api/entities", params={"entity_type": "NotARealType"})
    assert response.status_code == 422


def test_browse_entities_happy_path(client, db_stub):
    db_stub.add([{"total": 1}])
    db_stub.add([{"properties": {"id": "og-01", "name": "Meridian Capital Group"}, "entity_type": "Organization"}])
    response = client.get("/api/entities", params={"entity_type": "Organization", "limit": 20, "offset": 0})
    assert response.status_code == 200
    assert response.json()["total"] == 1


def test_search_short_query_returns_empty_without_hitting_db(client, db_stub):
    # single character queries are filtered by the service layer before
    # a query is ever issued
    response = client.get("/api/search", params={"q": "a"})
    assert response.status_code == 200
    assert response.json() == {"query": "a", "count": 0, "results": []}
    assert db_stub.calls == []


def test_search_returns_results(client, db_stub):
    db_stub.add([{"properties": {"id": "mw-01", "name": "GraniteLocker"}, "entity_type": "Malware"}])
    response = client.get("/api/search", params={"q": "granite"})
    assert response.status_code == 200
    assert response.json()["count"] == 1


def test_campaign_trail_404s_for_unknown_actor(client, db_stub):
    db_stub.add([])  # _assert_actor_exists -> get_entity finds nothing
    response = client.get("/api/investigations/campaign-trail/ta-99")
    assert response.status_code == 404


def test_stats_endpoint_shape(client, db_stub):
    db_stub.add([{
        "threatActors": 12, "malware": 20, "vulnerabilities": 24,
        "techniques": 16, "campaigns": 16, "organizations": 20, "indicators": 30,
    }])
    db_stub.add([{"total": 250}])
    db_stub.add([{"severity": "Critical", "count": 4}, {"severity": "High", "count": 8}])
    db_stub.add([{"tactic": "Initial Access", "count": 2}])
    response = client.get("/api/stats")
    assert response.status_code == 200
    body = response.json()
    assert body["counts"]["ThreatActor"] == 12
    assert body["total_relationships"] == 250
    assert body["severity_breakdown"]["Critical"] == 4


def test_database_unavailable_returns_503(client, db_stub, monkeypatch):
    def boom(*args, **kwargs):
        raise DatabaseUnavailableError("CognoDB is unreachable right now.")

    monkeypatch.setattr("app.db.run_query", boom)
    response = client.get("/api/stats")
    assert response.status_code == 503
