"""
Pydantic schemas mirroring the seven node labels in the graph.

These are intentionally close to the raw node properties. Keeping the
API-facing shape close to the graph model makes it easy to reason about
what a Cypher query returns and how it lands in a response, which
matters a lot when this project needs to be defended in an interview.
"""
from typing import Literal

from pydantic import BaseModel

EntityType = Literal[
    "ThreatActor",
    "Malware",
    "Vulnerability",
    "Technique",
    "Campaign",
    "Organization",
    "Indicator",
]

ALL_ENTITY_TYPES: tuple[EntityType, ...] = (
    "ThreatActor",
    "Malware",
    "Vulnerability",
    "Technique",
    "Campaign",
    "Organization",
    "Indicator",
)


class ThreatActor(BaseModel):
    id: str
    name: str
    description: str
    aliases: list[str] = []
    motivation: str
    origin: str


class Malware(BaseModel):
    id: str
    name: str
    type: str
    description: str
    platform: str


class Vulnerability(BaseModel):
    id: str
    cve: str
    severity: str
    description: str
    affected_product: str


class Technique(BaseModel):
    id: str
    name: str
    tactic: str
    description: str


class Campaign(BaseModel):
    id: str
    name: str
    description: str
    year: int


class Organization(BaseModel):
    id: str
    name: str
    industry: str
    country: str


class Indicator(BaseModel):
    id: str
    type: str
    value: str
    confidence: str


ENTITY_MODELS: dict[EntityType, type[BaseModel]] = {
    "ThreatActor": ThreatActor,
    "Malware": Malware,
    "Vulnerability": Vulnerability,
    "Technique": Technique,
    "Campaign": Campaign,
    "Organization": Organization,
    "Indicator": Indicator,
}

# The property used to render a human-readable label for each node type,
# and the property searched by the free-text search endpoint.
DISPLAY_PROPERTY: dict[EntityType, str] = {
    "ThreatActor": "name",
    "Malware": "name",
    "Vulnerability": "cve",
    "Technique": "name",
    "Campaign": "name",
    "Organization": "name",
    "Indicator": "value",
}
