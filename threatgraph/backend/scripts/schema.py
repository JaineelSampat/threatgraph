"""
Creates one uniqueness constraint per node label, each on the `id`
property. `CREATE CONSTRAINT ... IF NOT EXISTS` makes this safe to run
repeatedly - re-running the seed script never fails because the
constraint already exists.

A separate constraint per label (rather than one global constraint) is
required because Cypher constraints are always scoped to a single
label; `id` values are unique *within* a label by construction (see
scripts/data.py's id schemes: ta-01, mw-01, ...), and are also unique
*across* labels in this dataset, which is what lets entity_repository's
`MATCH (n {id: $id})` lookups work without knowing the label ahead of
time.
"""
from app.db import run_query

LABELS = [
    "ThreatActor",
    "Malware",
    "Vulnerability",
    "Technique",
    "Campaign",
    "Organization",
    "Indicator",
]


def create_constraints() -> None:
    for label in LABELS:
        constraint_name = f"{label.lower()}_id_unique"
        query = (
            f"CREATE CONSTRAINT {constraint_name} IF NOT EXISTS "
            f"FOR (n:{label}) REQUIRE n.id IS UNIQUE"
        )
        run_query(query)
        print(f"  constraint ensured: {constraint_name}")


if __name__ == "__main__":
    from app.db import close_driver, init_driver

    init_driver()
    try:
        create_constraints()
    finally:
        close_driver()
