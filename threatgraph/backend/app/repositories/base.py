"""
Shared conversion helpers used by every repository.

Every query in this project explicitly returns `labels(n)[0] AS entity_type`
alongside node properties, rather than passing raw driver Node objects
around. That keeps repositories working with plain dicts (easy to unit
test with a fake driver) instead of coupling the whole codebase to
neo4j-driver's internal types.
"""
from typing import Any

from app.models.entities import DISPLAY_PROPERTY, EntityType
from app.models.responses import EntitySummary

SUBTITLE_PROPERTY: dict[EntityType, str] = {
    "ThreatActor": "motivation",
    "Malware": "type",
    "Vulnerability": "severity",
    "Technique": "tactic",
    "Campaign": "year",
    "Organization": "industry",
    "Indicator": "type",
}


def to_entity_summary(properties: dict[str, Any], entity_type: EntityType) -> EntitySummary:
    label_prop = DISPLAY_PROPERTY[entity_type]
    subtitle_prop = SUBTITLE_PROPERTY.get(entity_type)
    return EntitySummary(
        id=properties["id"],
        entity_type=entity_type,
        label=str(properties.get(label_prop, properties.get("id"))),
        subtitle=str(properties[subtitle_prop]) if subtitle_prop and properties.get(subtitle_prop) is not None else None,
        properties=properties,
    )
