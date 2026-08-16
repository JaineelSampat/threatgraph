import { Link } from "react-router-dom";
import { api } from "../api/client";
import { BarChart } from "../components/BarChart";
import { StatCard } from "../components/StatCard";
import { ErrorState, LoadingState } from "../components/StatusStates";
import { useApi } from "../hooks/useApi";
import { ENTITY_TYPE_META } from "../lib/entityTypeMeta";
import { ALL_ENTITY_TYPES } from "../types/api";

export function Dashboard() {
  const { data: stats, loading, error } = useApi(() => api.stats(), []);

  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      <div className="mb-8">
        <h1 className="font-mono text-xl font-semibold text-ink">Threat Landscape Overview</h1>
        <p className="mt-1 text-sm text-ink-muted">
          A snapshot of every entity and relationship currently in the graph.
        </p>
      </div>

      {loading && <LoadingState label="Loading stats…" />}
      {error && <ErrorState message={error} />}

      {stats && (
        <>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 lg:grid-cols-7">
            {ALL_ENTITY_TYPES.map((type) => (
              <StatCard
                key={type}
                label={ENTITY_TYPE_META[type].pluralName}
                value={stats.counts[type] ?? 0}
                accent={ENTITY_TYPE_META[type].color}
              />
            ))}
          </div>

          <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2">
            <StatCard label="Total Relationships" value={stats.total_relationships} accent="#4FB6E8" />
            <StatCard
              label="Total Entities"
              value={Object.values(stats.counts).reduce((a, b) => a + b, 0)}
            />
          </div>

          <div className="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-2">
            <BarChart title="Vulnerabilities by Severity" data={stats.severity_breakdown} color="#E5484D" />
            <BarChart title="Techniques by ATT&CK Tactic" data={stats.tactic_breakdown} color="#4FB6E8" />
          </div>

          <div className="mt-8 flex flex-wrap gap-3">
            <Link
              to="/explorer"
              className="rounded-md border border-accent-cyan/40 bg-accent-cyan/10 px-4 py-2 text-sm text-accent-cyan transition hover:bg-accent-cyan/20"
            >
              Browse the graph →
            </Link>
            <Link
              to="/investigate"
              className="rounded-md border border-border px-4 py-2 text-sm text-ink-muted transition hover:text-ink"
            >
              Run an investigation →
            </Link>
          </div>
        </>
      )}
    </div>
  );
}
