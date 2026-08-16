import type { EntityType } from "../types/api";

interface EntityTypeMeta {
  abbreviation: string;
  displayName: string;
  pluralName: string;
  color: string; // tailwind text/border color class suffix-free hex, used inline for the graph canvas
  badgeClass: string; // tailwind classes for chips
}

// One config object drives entity badges everywhere in the app (explorer
// tabs, entity cards, graph node fill) and the force-directed graph's
// node coloring - a single place to change if the taxonomy ever grows.
export const ENTITY_TYPE_META: Record<EntityType, EntityTypeMeta> = {
  ThreatActor: {
    abbreviation: "TA",
    displayName: "Threat Actor",
    pluralName: "Threat Actors",
    color: "#E5484D",
    badgeClass: "bg-accent-red/15 text-accent-red border-accent-red/30",
  },
  Malware: {
    abbreviation: "MW",
    displayName: "Malware",
    pluralName: "Malware",
    color: "#E8A33D",
    badgeClass: "bg-accent-amber/15 text-accent-amber border-accent-amber/30",
  },
  Vulnerability: {
    abbreviation: "VU",
    displayName: "Vulnerability",
    pluralName: "Vulnerabilities",
    color: "#C77DFF",
    badgeClass: "bg-[#C77DFF]/15 text-[#C77DFF] border-[#C77DFF]/30",
  },
  Technique: {
    abbreviation: "TQ",
    displayName: "Technique",
    pluralName: "Techniques",
    color: "#4FB6E8",
    badgeClass: "bg-accent-cyan/15 text-accent-cyan border-accent-cyan/30",
  },
  Campaign: {
    abbreviation: "CM",
    displayName: "Campaign",
    pluralName: "Campaigns",
    color: "#F2789F",
    badgeClass: "bg-[#F2789F]/15 text-[#F2789F] border-[#F2789F]/30",
  },
  Organization: {
    abbreviation: "OG",
    displayName: "Organization",
    pluralName: "Organizations",
    color: "#4CAF7D",
    badgeClass: "bg-accent-green/15 text-accent-green border-accent-green/30",
  },
  Indicator: {
    abbreviation: "IN",
    displayName: "Indicator",
    pluralName: "Indicators",
    color: "#8B98A5",
    badgeClass: "bg-ink-muted/15 text-ink-muted border-ink-muted/30",
  },
};
