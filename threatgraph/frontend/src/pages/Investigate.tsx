import { useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import { EntityTypeBadge } from "../components/EntityTypeBadge";
import { RelationshipGraph } from "../components/RelationshipGraph";
import { EmptyState, ErrorState, LoadingState } from "../components/StatusStates";
import { useApi } from "../hooks/useApi";

type Tab = "campaign-trail" | "reachability";

export function Investigate() {
  const { data: actorList, loading: actorsLoading } = useApi(
    () => api.browseEntities("ThreatActor", 100, 0),
    [],
  );
  const [actorId, setActorId] = useState<string>("");
  const [tab, setTab] = useState<Tab>("campaign-trail");

  const actors = actorList?.results ?? [];
  const currentActor = actors.find((a) => a.id === actorId);

  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      <h1 className="mb-1 font-mono text-lg text-ink">Investigate</h1>
      <p className="mb-6 text-sm text-ink-muted">
        Pick a threat actor and trace how far their footprint reaches.
      </p>

      <div className="mb-6 flex flex-wrap items-center gap-3">
        <select
          value={actorId}
          onChange={(e) => setActorId(e.target.value)}
          disabled={actorsLoading}
          className="rounded-md border border-border bg-surface px-3 py-2 text-sm text-ink focus:border-accent-cyan focus:outline-none"
        >
          <option value="">{actorsLoading ? "Loading actors…" : "Select a threat actor…"}</option>
          {actors.map((a) => (
            <option key={a.id} value={a.id}>
              {a.label} ({a.id})
            </option>
          ))}
        </select>

        {actorId && (
          <div className="flex gap-1 rounded-md border border-border p-1">
            <TabButton active={tab === "campaign-trail"} onClick={() => setTab("campaign-trail")}>
              Campaign Trail
            </TabButton>
            <TabButton active={tab === "reachability"} onClick={() => setTab("reachability")}>
              Deep Reachability
            </TabButton>
          </div>
        )}
      </div>

      {!actorId && (
        <EmptyState
          title="No actor selected"
          description="Choose a threat actor above to trace their campaigns, targets, and reach."
        />
      )}

      {actorId && currentActor && tab === "campaign-trail" && <CampaignTrailView actorId={actorId} />}
      {actorId && currentActor && tab === "reachability" && <ReachabilityView actorId={actorId} />}
    </div>
  );
}

function TabButton({ active, onClick, children }: { active: boolean; onClick: () => void; children: React.ReactNode }) {
  return (
    <button
      onClick={onClick}
      className={`rounded px-3 py-1.5 text-xs font-medium transition ${
        active ? "bg-accent-cyan/15 text-accent-cyan" : "text-ink-muted hover:text-ink"
      }`}
    >
      {children}
    </button>
  );
}

function CampaignTrailView({ actorId }: { actorId: string }) {
  const { data, loading, error } = useApi(() => api.campaignTrail(actorId), [actorId]);

  if (loading) return <LoadingState label="Tracing campaigns…" />;
  if (error) return <ErrorState message={error} />;
  if (!data) return null;

  if (data.results.length === 0) {
    return (
      <EmptyState
        title="No campaign trail found"
        description="This actor isn't linked to any campaign that targets an organization in the current dataset."
      />
    );
  }

  return (
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1fr_1fr]">
      <div className="flex flex-col gap-3">
        <p className="font-mono text-[11px] uppercase tracking-wider text-ink-muted">
          ThreatActor → Campaign → Organization ({data.results.length})
        </p>
        {data.results.map((r, i) => (
          <div key={i} className="rounded-lg border border-border bg-surface p-4">
            <div className="flex flex-wrap items-center gap-2 text-sm">
              <EntityLink type="ThreatActor" id={r.actor.id} label={r.actor.label} />
              <span className="text-ink-faint">via</span>
              <EntityLink type="Campaign" id={r.campaign.id} label={r.campaign.label} />
              <span className="text-ink-faint">targets</span>
              <EntityLink type="Organization" id={r.organization.id} label={r.organization.label} />
            </div>
            {r.malware.length > 0 && (
              <div className="mt-3 flex flex-wrap items-center gap-2 border-t border-border pt-3">
                <span className="text-xs text-ink-faint">Malware used:</span>
                {r.malware.map((m) => (
                  <EntityLink key={m.id} type="Malware" id={m.id} label={m.label} />
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="rounded-lg border border-border bg-surface">
        <div className="border-b border-border px-4 py-3">
          <p className="font-mono text-[11px] uppercase tracking-wider text-ink-muted">Graph view</p>
        </div>
        <div className="aspect-square w-full">
          <RelationshipGraph nodes={data.graph.nodes} edges={data.graph.edges} focusId={actorId} />
        </div>
      </div>
    </div>
  );
}

function ReachabilityView({ actorId }: { actorId: string }) {
  const [maxHops, setMaxHops] = useState(3);
  const { data, loading, error } = useApi(() => api.reachability(actorId, maxHops), [actorId, maxHops]);

  return (
    <div>
      <div className="mb-4 flex items-center gap-3">
        <label className="text-sm text-ink-muted" htmlFor="hops">
          Max hops
        </label>
        <input
          id="hops"
          type="range"
          min={1}
          max={5}
          value={maxHops}
          onChange={(e) => setMaxHops(Number(e.target.value))}
          className="w-40"
        />
        <span className="font-mono text-sm text-accent-cyan">{maxHops}</span>
      </div>

      {loading && <LoadingState label="Walking the graph…" />}
      {error && <ErrorState message={error} />}

      {data && data.hits.length === 0 && (
        <EmptyState title="Nothing reachable" description="No organization sits within this many hops of the actor." />
      )}

      {data && data.hits.length > 0 && (
        <div className="overflow-hidden rounded-lg border border-border">
          <table className="w-full text-left text-sm">
            <thead className="bg-surface-raised text-xs uppercase tracking-wider text-ink-muted">
              <tr>
                <th className="px-4 py-2 font-medium">Organization</th>
                <th className="px-4 py-2 font-medium">Hops</th>
                <th className="px-4 py-2 font-medium">Path</th>
              </tr>
            </thead>
            <tbody>
              {data.hits.map((hit) => (
                <tr key={hit.organization.id} className="border-t border-border bg-surface">
                  <td className="px-4 py-2">
                    <EntityLink type="Organization" id={hit.organization.id} label={hit.organization.label} />
                  </td>
                  <td className="px-4 py-2 font-mono text-accent-cyan">{hit.hop_count}</td>
                  <td className="px-4 py-2 font-mono text-xs text-ink-faint">{hit.path_labels.join(" → ")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function EntityLink({ type, id, label }: { type: Parameters<typeof EntityTypeBadge>[0]["entityType"]; id: string; label: string }) {
  return (
    <Link to={`/entity/${encodeURIComponent(id)}`} className="inline-flex items-center gap-1.5 hover:text-accent-cyan">
      <EntityTypeBadge entityType={type} />
      <span>{label}</span>
    </Link>
  );
}
