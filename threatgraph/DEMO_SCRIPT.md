# Demo Script

~4 minutes, five stops. Recording checklist: full-screen the browser, zoom to
125% so text reads clearly, and narrate each step out loud before clicking.

## 1. Dashboard (30s)

Land on `/`. Point out the seven entity-count cards, the total relationship
count, and the two breakdown charts (vulnerability severity, technique
tactic). Say: *"This is one Cypher query chaining seven counts plus three
small aggregates — no ORM, no APOC, just portable Cypher, because I didn't
want to assume what CognoDB's free tier supports."*

## 2. Explorer + search (45s)

Click **Explorer**. Switch between a couple of entity-type tabs to show
pagination working. Then use the top-nav search bar — type `granite` and
show it landing on the search results view with the matching malware card.
Say: *"Every node gets a precomputed lowercase search_text field at seed
time, so this one query shape works identically across all seven types."*

## 3. Entity detail + the graph (60s)

Click into a `ThreatActor` card (or a `Malware` card that has a good spread
of connections). Walk through:
- the properties panel on the left
- the **relationship graph** on the right — drag a node to show it's a real
  physics simulation, not a static image, then click a non-focus node to
  show it navigating to that entity's own detail page

Say: *"This is a small hand-written force-directed layout — Coulomb
repulsion between every pair of nodes, Hooke's-law springs along edges. I
wrote it instead of pulling in d3-force because for a graph this small it's
under 100 lines and I can defend every line of it."*

## 4. Investigate — Campaign Trail (45s)

Go to **Investigate**, pick a threat actor from the dropdown. Show the
Campaign Trail tab: actor → campaign → organization rows, with malware
chips underneath. Click through one of the entity links to show it's not
just decorative text. Say: *"This is the mandatory multi-hop query —
ThreatActor connected to Organization through Campaign, with Malware pulled
in as an optional branch so a campaign with no recorded malware still shows
up instead of silently disappearing from results."*

## 5. Investigate — Deep Reachability (45s)

Switch to the Deep Reachability tab. Drag the hop slider from 1 up to 4-5
and narrate the result table growing. Say: *"This is the relationally
awkward one — a variable-length pattern across all eight relationship types
in either direction. In SQL this is a hand-rolled recursive CTE with a new
UNION branch per relationship type; here it's one line of Cypher that stays
correct if the schema grows a ninth relationship type tomorrow."*

## Closing line

*"Everything here is read-only against CognoDB over the Neo4j driver, every
query is parameterized, and the two places a label gets embedded in the
query string are validated against a fixed enum before they ever get there
— that's covered in INTERVIEW_GUIDE.md if you want the specifics."*
