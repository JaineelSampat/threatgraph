export type EntityType =
  | "ThreatActor"
  | "Malware"
  | "Vulnerability"
  | "Technique"
  | "Campaign"
  | "Organization"
  | "Indicator";

export const ALL_ENTITY_TYPES: EntityType[] = [
  "ThreatActor",
  "Malware",
  "Vulnerability",
  "Technique",
  "Campaign",
  "Organization",
  "Indicator",
];

export interface EntitySummary {
  id: string;
  entity_type: EntityType;
  label: string;
  subtitle: string | null;
  properties: Record<string, unknown>;
}

export interface RelatedEntity {
  relationship_type: string;
  direction: "outgoing" | "incoming";
  entity: EntitySummary;
}

export interface EntityDetail {
  entity: EntitySummary;
  related: RelatedEntity[];
}

export interface SearchResponse {
  query: string;
  count: number;
  results: EntitySummary[];
}

export interface EntityListResponse {
  entity_type: EntityType;
  total: number;
  limit: number;
  offset: number;
  results: EntitySummary[];
}

export interface DashboardStats {
  counts: Record<string, number>;
  total_relationships: number;
  severity_breakdown: Record<string, number>;
  tactic_breakdown: Record<string, number>;
}

export interface GraphNode {
  id: string;
  entity_type: EntityType;
  label: string;
}

export interface GraphEdge {
  source: string;
  target: string;
  relationship_type: string;
}

export interface GraphPath {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface CampaignTrailResult {
  actor: EntitySummary;
  campaign: EntitySummary;
  organization: EntitySummary;
  malware: EntitySummary[];
}

export interface CampaignTrailResponse {
  actor_id: string;
  results: CampaignTrailResult[];
  graph: GraphPath;
}

export interface ReachabilityHit {
  organization: EntitySummary;
  hop_count: number;
  path_labels: string[];
}

export interface ReachabilityResponse {
  actor_id: string;
  max_hops: number;
  hits: ReachabilityHit[];
}

export interface HealthResponse {
  status: "ok" | "degraded";
  database_connected: boolean;
}
