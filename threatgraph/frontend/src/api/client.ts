import type {
  CampaignTrailResponse,
  DashboardStats,
  EntityDetail,
  EntityListResponse,
  EntityType,
  HealthResponse,
  ReachabilityResponse,
  SearchResponse,
} from "../types/api";

// In production, set VITE_API_BASE_URL to the deployed backend's URL.
// In local dev this is left empty and Vite's dev server proxy (see
// vite.config.ts) forwards /api and /health to localhost:8000.
const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${BASE_URL}${path}`);
  } catch {
    throw new ApiError("Couldn't reach the ThreatGraph API. Is the backend running?", 0);
  }

  if (!response.ok) {
    let detail = `Request failed with status ${response.status}`;
    try {
      const body = await response.json();
      if (body?.detail) detail = body.detail;
    } catch {
      // response body wasn't JSON - fall back to the generic message above
    }
    throw new ApiError(detail, response.status);
  }

  return response.json() as Promise<T>;
}

export const api = {
  health: () => request<HealthResponse>("/health"),

  stats: () => request<DashboardStats>("/api/stats"),

  browseEntities: (entityType: EntityType, limit: number, offset: number) =>
    request<EntityListResponse>(
      `/api/entities?entity_type=${entityType}&limit=${limit}&offset=${offset}`,
    ),

  getEntity: (id: string) => request<EntityDetail>(`/api/entities/${encodeURIComponent(id)}`),

  search: (query: string, limit = 25) =>
    request<SearchResponse>(`/api/search?q=${encodeURIComponent(query)}&limit=${limit}`),

  campaignTrail: (actorId: string) =>
    request<CampaignTrailResponse>(`/api/investigations/campaign-trail/${encodeURIComponent(actorId)}`),

  reachability: (actorId: string, maxHops: number) =>
    request<ReachabilityResponse>(
      `/api/investigations/reachability/${encodeURIComponent(actorId)}?max_hops=${maxHops}`,
    ),
};
