# Interview Guide

This is my own reference for defending ThreatGraph, organized by the kind of
question I'd expect: schema decisions, query-by-query walkthroughs, and the
tradeoffs I made on purpose.

## 1. Why these seven node types and eight relationship types?

They map onto the standard "diamond model" of intrusion analysis: an
**adversary** (`ThreatActor`) uses **capabilities** (`Malware`, which itself
`EXPLOITS` a `Vulnerability` and implements ATT&CK `Technique`s) against
**victims** (`Organization`) through **infrastructure** (`Indicator`), all tied
together by a specific **event** (`Campaign`). Eight relationship types is the
minimum set that lets every node type reach every other node type through at
least one meaningful path, without inventing relationships that don't
correspond to a real analyst question.

One deliberate choice: relationship types are reused across different
node-type pairs — `ASSOCIATED_WITH` connects both `Campaign -> ThreatActor`
(attribution) and `Indicator -> ThreatActor` (infrastructure tied directly to
an actor). In a relational schema that's two different junction tables with
different foreign keys; in a property graph it's the same relationship type
doing double duty, which is a real structural difference worth being able to
explain, not just a quirk of the seed script.

## 2. Walking through each query

### Query 1 — Search (`search_repository.py`)

```cypher
MATCH (n)
WHERE any(lbl IN labels(n) WHERE lbl IN $labels)
  AND n.search_text CONTAINS toLower($search)
RETURN properties(n) AS properties, labels(n)[0] AS entity_type
LIMIT $limit
```

Every node gets a precomputed lowercase `search_text` at seed time (e.g.
`"granitelocker mw-01 ransomware windows"`) instead of the query
re-lowercasing several different display properties (`name` vs `cve` vs
`value`) at query time. That keeps one query shape working identically
across all seven node types. The `$labels` allowlist guards against ever
matching a stray node that isn't one of the seven domain types, even though
none exist in this schema today.

**Tradeoff I'd flag unprompted:** `CONTAINS` can't use a standard index —
it's a substring scan. Fine at this dataset size (122 nodes); at real scale
I'd add a full-text index (`db.index.fulltext.createNodeIndex` in Neo4j, or
whatever CognoDB's equivalent is) and switch this query to use it.

### Query 2 / 5 — Entity detail + related entities (`entity_repository.py`)

```cypher
MATCH (n {id: $id})
RETURN properties(n) AS properties, labels(n)[0] AS entity_type
LIMIT 1
```
```cypher
MATCH (n {id: $id})-[r]-(neighbor)
RETURN type(r) AS relationship_type,
       CASE WHEN startNode(r) = n THEN 'outgoing' ELSE 'incoming' END AS direction,
       properties(neighbor) AS properties,
       labels(neighbor)[0] AS entity_type
LIMIT $limit
```

I implemented these as one repository with two functions rather than
duplicating the neighbor-fetch logic inside a combined query, because the
service layer (`entity_service.get_entity_detail`) composes them — Query 2
and Query 5 share the same neighbor-fetch code path instead of two near-
identical queries drifting apart over time.

`startNode(r) = n` is what lets the UI draw an arrow in the correct
direction without the frontend having to know anything about relationship
semantics — it's a boolean the database already knows.

### Query 3 — Campaign trail (`investigation_repository.py`) — the mandatory multi-hop query

```cypher
MATCH (ta:ThreatActor {id: $actorId})<-[:ASSOCIATED_WITH]-(c:Campaign)-[:TARGETS]->(o:Organization)
OPTIONAL MATCH (c)<-[:PART_OF]-(m:Malware)
RETURN properties(ta) AS actor, properties(c) AS campaign, properties(o) AS organization,
       collect(DISTINCT properties(m)) AS malware
ORDER BY c.year DESC
```

This is a fixed 2-hop shape (`ThreatActor <- Campaign -> Organization`) with
malware pulled in as an `OPTIONAL MATCH` branch rather than a third hop in
the main pattern — if I put `Malware` in the main `MATCH`, a campaign with no
recorded malware would silently disappear from the results instead of
showing up with an empty malware list. That's the kind of bug that's easy to
miss until someone asks "why doesn't this campaign show up?"

### Query 4 — Reachability — the relationally-awkward query

```cypher
MATCH p = (ta:ThreatActor {id: $actorId})
          -[:USES|EXPLOITS|USES_TECHNIQUE|PART_OF|TARGETS|ASSOCIATED_WITH|INDICATES|RELATED_TO*1..5]-
          (target:Organization)
WHERE ta <> target
WITH target, min(length(p)) AS hops, head(collect(p)) AS samplePath
RETURN properties(target) AS properties, hops,
       [n IN nodes(samplePath) | labels(n)[0]] AS path_labels
ORDER BY hops ASC
LIMIT 25
```

If someone asks "why is this the awkward one" — because it doesn't ask for a
specific shape, it asks "what's reachable at all, through anything, within N
steps." In SQL that's a recursive CTE that has to enumerate every
relationship-type join path by hand (`actor_uses_malware JOIN
malware_part_of_campaign JOIN campaign_targets_org UNION actor_uses_malware
JOIN malware_exploits_vuln JOIN vuln_related_to_technique UNION ...` — and
it needs a new UNION branch every time the schema gains a relationship
type). Cypher's variable-length pattern with an alternation of relationship
types handles all of those paths in one statement, and stays correct if the
schema grows an 9th relationship type tomorrow.

**Why `WITH target, min(length(p))` instead of returning every path:** a
graph this connected can have many paths of different lengths between the
same two nodes; the analyst question is "how close is this org," not "list
every possible path," so I collapse to the shortest one found per target
before returning.

### Query 6 — Dashboard stats (`stats_repository.py`)

Written as one chained `MATCH ... WITH ... MATCH ...` statement rather than
`CALL {}` subqueries or APOC, specifically because I didn't want to assume
CognoDB's free tier supports either — chained `WITH` is core Cypher that's
worked the same way since Neo4j 2.x, so it's the safest bet for portability.
If I verified `CALL {}` subqueries work, I'd refactor this into one per
count for readability; right now it's optimized for "works on the first
try against an unfamiliar managed database."

## 3. "Labels can't be parameterized — isn't that a Cypher injection risk?"

The Bolt protocol only binds *property values* as parameters — node labels
and relationship types are part of the query's structure, not its data, and
the driver has no API to parameterize them. Two places in this codebase
embed a label in an f-string: `entity_repository.list_entities` (browsing by
type) and `investigation_repository.reachability` (target type, currently
always `"Organization"`). Both values arrive only after FastAPI validates
them against the `EntityType` `Literal` in `app/models/entities.py` — so by
the time the string reaches Cypher, it's guaranteed to be one of seven
hardcoded values, never arbitrary request input. I'd say this out loud
before anyone had to ask.

## 4. "Why FastAPI + a service layer instead of just routes calling the driver directly?"

Three layers (routes -> services -> repositories) for a project this size is
arguably more structure than strictly necessary, but it's what let me test
the mapping logic (Cypher row -> Pydantic model) without a live database —
every repository function takes rows shaped exactly like what
`session.run(...).data()` returns and is tested against hand-built fixtures
of that shape (see `tests/test_repositories.py`). The alternative — testing
only through the routes — would leave the query-to-model mapping unverified
whenever a route test happens to pass a shape that matches by accident.

## 5. "What would you do differently with more time?"

- Add a real full-text search index once I've confirmed CognoDB supports it.
- Cache `/api/stats` — it currently re-scans all seven labels on every
  request; fine for a small free-tier dataset, wasteful at real scale.
- Add pagination cursors instead of offset/limit for `browseEntities` —
  offset pagination re-scans skipped rows on a large graph.
