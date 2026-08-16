import { Link, useParams } from "react-router-dom";
import { api } from "../api/client";
import { EntityTypeBadge } from "../components/EntityTypeBadge";
import { RelationshipGraph } from "../components/RelationshipGraph";
import { ErrorState, LoadingState } from "../components/StatusStates";
import { useApi } from "../hooks/useApi";
import { ENTITY_TYPE_META } from "../lib/entityTypeMeta";
import type { GraphEdge, GraphNode } from "../types/api";

const HIDDEN_PROPERTIES = new Set(["id", "search_text"]);

export function EntityDetail() {
  const { id = "" } = useParams();
  const { data, loading, error } = useApi(() => api.getEntity(id), [id]);

  if (loading) return <LoadingState label="Loading entity…" />;
  if (error) return <ErrorState message={error} />;
  if (!data) return null;

  const { entity, related } = data;
  const meta = ENTITY_TYPE_META[entity.entity_type];

  const graphNodes: GraphNode[] = [
    { id: entity.id, entity_type: entity.entity_type, label: entity.label },
    ...related.map((r) => ({ id: r.entity.id, entity_type: r.entity.entity_type, label: r.entity.label })),
  ];
  const graphEdges: GraphEdge[] = related.map((r) => ({
    source: r.direction === "outgoing" ? entity.id : r.entity.id,
    target: r.direction === "outgoing" ? r.entity.id : entity.id,
    relationship_type: r.relationship_type,
  }));

  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      <Link to="/explorer" className="text-sm text-ink-muted hover:text-accent-cyan">
        ← Back to explorer
      </Link>

      <div className="mt-4 grid grid-cols-1 gap-6 lg:grid-cols-[380px_1fr]">
        <div className="flex flex-col gap-4">
          <div className="rounded-lg border border-border bg-surface p-5">
            <div className="flex items-center gap-2">
              <EntityTypeBadge entityType={entity.entity_type} size="md" />
              <span className="font-mono text-xs text-ink-faint">{entity.id}</span>
            </div>
            <h1 className="mt-3 text-lg font-semibold text-ink">{entity.label}</h1>
            <p className="mt-1 text-xs uppercase tracking-wide text-ink-muted">{meta.displayName}</p>

            <dl className="mt-4 flex flex-col gap-2 border-t border-border pt-4">
              {Object.entries(entity.properties)
                .filter(([key]) => !HIDDEN_PROPERTIES.has(key))
                .map(([key, value]) => (
                  <div key={key} className="flex flex-col gap-0.5">
                    <dt className="font-mono text-[10px] uppercase tracking-wider text-ink-faint">
                      {key.replace(/_/g, " ")}
                    </dt>
                    <dd className="text-sm text-ink">
                      {Array.isArray(value) ? value.join(", ") : String(value)}
                    </dd>
                  </div>
                ))}
            </dl>
          </div>

          <div className="rounded-lg border border-border bg-surface p-5">
            <p className="mb-3 font-mono text-[11px] uppercase tracking-wider text-ink-muted">
              Connected entities ({related.length})
            </p>
            {related.length === 0 && <p className="text-sm text-ink-faint">No known connections.</p>}
            <ul className="flex flex-col gap-2">
              {related.map((r, i) => (
                <li key={i}>
                  <Link
                    to={`/entity/${encodeURIComponent(r.entity.id)}`}
                    className="flex items-center justify-between gap-2 rounded-md px-2 py-1.5 text-sm transition hover:bg-surface-raised"
                  >
                    <span className="flex items-center gap-2 truncate">
                      <EntityTypeBadge entityType={r.entity.entity_type} />
                      <span className="truncate text-ink">{r.entity.label}</span>
                    </span>
                    <span className="shrink-0 font-mono text-[10px] text-ink-faint">
                      {r.direction === "outgoing" ? "→" : "←"} {r.relationship_type}
                    </span>
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="rounded-lg border border-border bg-surface">
          <div className="border-b border-border px-5 py-3">
            <p className="font-mono text-[11px] uppercase tracking-wider text-ink-muted">
              Relationship graph &middot; drag to rearrange, click a node to open it
            </p>
          </div>
          <div className="aspect-[3/2] w-full">
            <RelationshipGraph nodes={graphNodes} edges={graphEdges} focusId={entity.id} />
          </div>
        </div>
      </div>
    </div>
  );
}
