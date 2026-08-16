"""
Query 6 - Dashboard Statistics.

Written as one chained MATCH/WITH statement rather than seven separate
round trips, and without APOC or CALL{} subqueries, so it stays
portable across whatever subset of Cypher CognoDB's free tier supports.
Each MATCH is a fresh full scan of one label; the running counts are
threaded forward through WITH.
"""
from app import db
from app.models.responses import DashboardStats


def get_dashboard_stats() -> DashboardStats:
    counts_query = """
        MATCH (ta:ThreatActor)
        WITH count(ta) AS threatActors
        MATCH (mw:Malware)
        WITH threatActors, count(mw) AS malware
        MATCH (vu:Vulnerability)
        WITH threatActors, malware, count(vu) AS vulnerabilities
        MATCH (tq:Technique)
        WITH threatActors, malware, vulnerabilities, count(tq) AS techniques
        MATCH (cm:Campaign)
        WITH threatActors, malware, vulnerabilities, techniques, count(cm) AS campaigns
        MATCH (og:Organization)
        WITH threatActors, malware, vulnerabilities, techniques, campaigns, count(og) AS organizations
        MATCH (ind:Indicator)
        WITH threatActors, malware, vulnerabilities, techniques, campaigns, organizations, count(ind) AS indicators
        RETURN threatActors, malware, vulnerabilities, techniques, campaigns, organizations, indicators
    """
    counts_row = db.run_query(counts_query)[0]
    counts = {
        "ThreatActor": counts_row["threatActors"],
        "Malware": counts_row["malware"],
        "Vulnerability": counts_row["vulnerabilities"],
        "Technique": counts_row["techniques"],
        "Campaign": counts_row["campaigns"],
        "Organization": counts_row["organizations"],
        "Indicator": counts_row["indicators"],
    }

    rel_count_row = db.run_query("MATCH ()-[r]->() RETURN count(r) AS total")[0]

    severity_rows = db.run_query(
        "MATCH (v:Vulnerability) RETURN v.severity AS severity, count(v) AS count"
    )
    severity_breakdown = {row["severity"]: row["count"] for row in severity_rows}

    tactic_rows = db.run_query(
        "MATCH (t:Technique) RETURN t.tactic AS tactic, count(t) AS count"
    )
    tactic_breakdown = {row["tactic"]: row["count"] for row in tactic_rows}

    return DashboardStats(
        counts=counts,
        total_relationships=rel_count_row["total"],
        severity_breakdown=severity_breakdown,
        tactic_breakdown=tactic_breakdown,
    )
