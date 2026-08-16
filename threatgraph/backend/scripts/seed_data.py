"""
Loads the synthetic ThreatGraph dataset into CognoDB.

Usage:
    python -m scripts.seed_data          # from the backend/ directory

Idempotency: every node is written with `MERGE (n:Label {id: $id}) SET
n += $props`, and every relationship with `MERGE (a)-[r:TYPE]->(b)`.
Running this script twice against the same database updates properties
in place and does not create duplicate nodes or relationships.

Relationship wiring is generated deterministically (see the module-level
RNG below) rather than hand-listed, then passed through an "orphan
pass" for each relationship so every node ends up with at least one
connection - important because an isolated node makes for a dead-end
entity detail page.
"""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db import close_driver, init_driver, run_query  # noqa: E402
from scripts import data  # noqa: E402
from scripts.schema import create_constraints  # noqa: E402

EDGE_RNG = random.Random(7)


def _ids(prefix: str, count: int) -> list[str]:
    return [f"{prefix}-{i + 1:02d}" for i in range(count)]


TA = _ids("ta", len(data.THREAT_ACTORS))
MW = _ids("mw", len(data.MALWARE))
VU = _ids("vu", len(data.VULNERABILITIES))
TQ = _ids("tq", len(data.TECHNIQUES))
CM = _ids("cm", len(data.CAMPAIGNS))
OG = _ids("og", len(data.ORGANIZATIONS))
IN = _ids("in", len(data.INDICATORS))

# Real-world exploit-related ATT&CK techniques, used to bias the
# Vulnerability -> Technique wiring so it reads as intentional rather
# than uniformly random.
_EXPLOIT_TECHNIQUES = [TQ[1], TQ[14]]  # T1190, T1210


# ---------------------------------------------------------------------------
# Node payload builders
# ---------------------------------------------------------------------------
def _threat_actor_rows() -> list[dict]:
    rows = []
    for tid, (name, motivation, origin) in zip(TA, data.THREAT_ACTORS):
        rows.append({
            "id": tid,
            "name": name,
            "description": data.actor_description(name, motivation),
            "aliases": [f"{name.split()[0]}-{tid.upper()}"],
            "motivation": motivation,
            "origin": origin,
            "search_text": f"{name.lower()} {tid} {motivation.lower()} {origin.lower()}",
        })
    return rows


def _malware_rows() -> list[dict]:
    rows = []
    for mid, (name, mtype, platform) in zip(MW, data.MALWARE):
        rows.append({
            "id": mid,
            "name": name,
            "type": mtype,
            "description": data.malware_description(name, mtype, platform),
            "platform": platform,
            "search_text": f"{name.lower()} {mid} {mtype.lower()} {platform.lower()}",
        })
    return rows


def _vulnerability_rows() -> list[dict]:
    rows = []
    for vid, (cve, severity, product) in zip(VU, data.VULNERABILITIES):
        rows.append({
            "id": vid,
            "cve": cve,
            "severity": severity,
            "description": data.vulnerability_description(cve, product, severity),
            "affected_product": product,
            "search_text": f"{cve.lower()} {vid} {severity.lower()} {product.lower()}",
        })
    return rows


def _technique_rows() -> list[dict]:
    rows = []
    for qid, (att_id, name, tactic) in zip(TQ, data.TECHNIQUES):
        full_name = f"{att_id} {name}"
        rows.append({
            "id": qid,
            "name": full_name,
            "tactic": tactic,
            "description": data.technique_description(full_name, tactic),
            "search_text": f"{full_name.lower()} {qid} {tactic.lower()}",
        })
    return rows


def _campaign_rows() -> list[dict]:
    rows = []
    for cid, (name, year) in zip(CM, data.CAMPAIGNS):
        rows.append({
            "id": cid,
            "name": name,
            "description": data.campaign_description(name, year),
            "year": year,
            "search_text": f"{name.lower()} {cid} {year}",
        })
    return rows


def _organization_rows() -> list[dict]:
    rows = []
    for oid, (name, industry, country) in zip(OG, data.ORGANIZATIONS):
        rows.append({
            "id": oid,
            "name": name,
            "industry": industry,
            "country": country,
            "search_text": f"{name.lower()} {oid} {industry.lower()} {country.lower()}",
        })
    return rows


def _indicator_rows() -> list[dict]:
    rows = []
    for iid, (ioc_type, value, confidence) in zip(IN, data.INDICATORS):
        rows.append({
            "id": iid,
            "type": ioc_type,
            "value": value,
            "confidence": confidence,
            "search_text": f"{value.lower()} {iid} {ioc_type.lower()} {confidence.lower()}",
        })
    return rows


NODE_BUILDERS = [
    ("ThreatActor", _threat_actor_rows),
    ("Malware", _malware_rows),
    ("Vulnerability", _vulnerability_rows),
    ("Technique", _technique_rows),
    ("Campaign", _campaign_rows),
    ("Organization", _organization_rows),
    ("Indicator", _indicator_rows),
]


def load_nodes() -> None:
    for label, builder in NODE_BUILDERS:
        rows = builder()
        query = f"""
            UNWIND $rows AS row
            MERGE (n:{label} {{id: row.id}})
            SET n += row
        """
        run_query(query, {"rows": rows})
        print(f"  loaded {len(rows)} {label} nodes")


# ---------------------------------------------------------------------------
# Relationship wiring
# ---------------------------------------------------------------------------
def _sample(pool: list[str], k_choices: list[int]) -> list[str]:
    k = min(EDGE_RNG.choice(k_choices), len(pool))
    return EDGE_RNG.sample(pool, k)


def _fill_orphans(pairs: list[tuple[str, str]], universe: list[str], other_pool: list[str]) -> list[tuple[str, str]]:
    """Ensure every id in `universe` appears at least once as the second element of `pairs`."""
    covered = {b for _, b in pairs}
    for missing in universe:
        if missing not in covered:
            pairs.append((EDGE_RNG.choice(other_pool), missing))
    return pairs


def _build_actor_uses_malware() -> list[tuple[str, str]]:
    pairs = [(actor, mw) for actor in TA for mw in _sample(MW, [2, 3])]
    return _fill_orphans(pairs, MW, TA)


def _build_malware_exploits_vuln() -> list[tuple[str, str]]:
    pairs = [(mw, vu) for mw in MW for vu in _sample(VU, [1, 2])]
    return _fill_orphans(pairs, VU, MW)


def _build_actor_uses_technique() -> list[tuple[str, str]]:
    pairs = [(actor, tq) for actor in TA for tq in _sample(TQ, [3, 4, 5])]
    return _fill_orphans(pairs, TQ, TA)


def _build_malware_uses_technique() -> list[tuple[str, str]]:
    pairs = [(mw, tq) for mw in MW for tq in _sample(TQ, [2, 3])]
    return _fill_orphans(pairs, TQ, MW)


def _build_campaign_associated_with_actor() -> list[tuple[str, str]]:
    return [(CM[i], TA[i % len(TA)]) for i in range(len(CM))]


def _build_malware_part_of_campaign(campaign_actor: dict[str, str], actor_malware: dict[str, list[str]]) -> list[tuple[str, str]]:
    pairs = []
    for campaign in CM:
        actor = campaign_actor[campaign]
        pool = actor_malware.get(actor) or MW
        for mw in _sample(pool, [1, 2, 3]):
            pairs.append((mw, campaign))
    return _fill_orphans(pairs, CM, MW)


def _build_campaign_targets_org() -> list[tuple[str, str]]:
    pairs = [(cm, og) for cm in CM for og in _sample(OG, [1, 2, 3])]
    return _fill_orphans(pairs, OG, CM)


def _build_vuln_related_to_technique() -> list[tuple[str, str]]:
    pairs = []
    for vu in VU:
        if EDGE_RNG.random() < 0.6:
            pairs.append((vu, EDGE_RNG.choice(_EXPLOIT_TECHNIQUES)))
        else:
            pairs.append((vu, EDGE_RNG.choice(TQ)))
    return pairs


def _build_indicator_indicates_malware() -> list[tuple[str, str]]:
    return [(IN[i], MW[(i * 3 + 7) % len(MW)]) for i in range(len(IN))]


def _build_indicator_associated_with_actor() -> list[tuple[str, str]]:
    return [(IN[i], EDGE_RNG.choice(TA)) for i in range(len(IN)) if i % 5 == 0]


def load_relationships() -> None:
    actor_uses_malware = _build_actor_uses_malware()
    actor_malware_map: dict[str, list[str]] = {}
    for actor, mw in actor_uses_malware:
        actor_malware_map.setdefault(actor, []).append(mw)

    campaign_actor_pairs = _build_campaign_associated_with_actor()
    campaign_actor_map = dict(campaign_actor_pairs)

    edge_sets: list[tuple[str, str, str, list[tuple[str, str]]]] = [
        ("ThreatActor", "USES", "Malware", actor_uses_malware),
        ("Malware", "EXPLOITS", "Vulnerability", _build_malware_exploits_vuln()),
        ("ThreatActor", "USES_TECHNIQUE", "Technique", _build_actor_uses_technique()),
        ("Malware", "USES_TECHNIQUE", "Technique", _build_malware_uses_technique()),
        ("Campaign", "ASSOCIATED_WITH", "ThreatActor", campaign_actor_pairs),
        ("Malware", "PART_OF", "Campaign", _build_malware_part_of_campaign(campaign_actor_map, actor_malware_map)),
        ("Campaign", "TARGETS", "Organization", _build_campaign_targets_org()),
        ("Vulnerability", "RELATED_TO", "Technique", _build_vuln_related_to_technique()),
        ("Indicator", "INDICATES", "Malware", _build_indicator_indicates_malware()),
        ("Indicator", "ASSOCIATED_WITH", "ThreatActor", _build_indicator_associated_with_actor()),
    ]

    for from_label, rel_type, to_label, pairs in edge_sets:
        rows = [{"from": a, "to": b} for a, b in pairs]
        query = f"""
            UNWIND $rows AS row
            MATCH (a:{from_label} {{id: row.from}})
            MATCH (b:{to_label} {{id: row.to}})
            MERGE (a)-[r:{rel_type}]->(b)
        """
        run_query(query, {"rows": rows})
        print(f"  loaded {len(rows)} ({from_label})-[:{rel_type}]->({to_label}) relationships")


def main() -> None:
    init_driver()
    try:
        print("Ensuring schema constraints...")
        create_constraints()
        print("Loading nodes...")
        load_nodes()
        print("Loading relationships...")
        load_relationships()
        print("Seed complete.")
    finally:
        close_driver()


if __name__ == "__main__":
    main()
