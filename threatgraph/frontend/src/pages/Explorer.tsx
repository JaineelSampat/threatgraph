import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api } from "../api/client";
import { EntityCard } from "../components/EntityCard";
import { EmptyState, ErrorState, LoadingState } from "../components/StatusStates";
import { useApi } from "../hooks/useApi";
import { ENTITY_TYPE_META } from "../lib/entityTypeMeta";
import { ALL_ENTITY_TYPES, EntityType } from "../types/api";

const PAGE_SIZE = 12;

export function Explorer() {
  const [searchParams] = useSearchParams();
  const searchQuery = searchParams.get("q");

  if (searchQuery) {
    return <SearchResultsView query={searchQuery} />;
  }
  return <BrowseView />;
}

function SearchResultsView({ query }: { query: string }) {
  const { data, loading, error } = useApi(() => api.search(query, 50), [query]);

  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      <h1 className="font-mono text-lg text-ink">
        Search results for <span className="text-accent-cyan">&ldquo;{query}&rdquo;</span>
      </h1>
      <p className="mt-1 text-sm text-ink-muted">
        {loading ? "Searching…" : `${data?.count ?? 0} matches across all entity types`}
      </p>

      <div className="mt-6">
        {loading && <LoadingState />}
        {error && <ErrorState message={error} />}
        {data && data.results.length === 0 && (
          <EmptyState title="No matches" description="Try a shorter or different term." />
        )}
        {data && data.results.length > 0 && (
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {data.results.map((entity) => (
              <EntityCard key={entity.id} entity={entity} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function BrowseView() {
  const [activeType, setActiveType] = useState<EntityType>("ThreatActor");
  const [offset, setOffset] = useState(0);

  useEffect(() => setOffset(0), [activeType]);

  const { data, loading, error } = useApi(
    () => api.browseEntities(activeType, PAGE_SIZE, offset),
    [activeType, offset],
  );

  const page = Math.floor(offset / PAGE_SIZE) + 1;
  const totalPages = data ? Math.max(1, Math.ceil(data.total / PAGE_SIZE)) : 1;

  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      <h1 className="mb-1 font-mono text-lg text-ink">Explorer</h1>
      <p className="mb-6 text-sm text-ink-muted">Browse every entity in the graph by type.</p>

      <div className="mb-6 flex flex-wrap gap-2 border-b border-border pb-4">
        {ALL_ENTITY_TYPES.map((type) => {
          const meta = ENTITY_TYPE_META[type];
          const active = type === activeType;
          return (
            <button
              key={type}
              onClick={() => setActiveType(type)}
              className={`rounded-md border px-3 py-1.5 font-mono text-xs uppercase tracking-wide transition ${
                active
                  ? "border-accent-cyan/50 bg-accent-cyan/10 text-accent-cyan"
                  : "border-border text-ink-muted hover:text-ink"
              }`}
            >
              {meta.pluralName}
            </button>
          );
        })}
      </div>

      {loading && <LoadingState />}
      {error && <ErrorState message={error} />}

      {data && (
        <>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {data.results.map((entity) => (
              <EntityCard key={entity.id} entity={entity} />
            ))}
          </div>

          <div className="mt-6 flex items-center justify-between text-sm text-ink-muted">
            <span>
              {data.total} total &middot; page {page} of {totalPages}
            </span>
            <div className="flex gap-2">
              <button
                disabled={offset === 0}
                onClick={() => setOffset(Math.max(0, offset - PAGE_SIZE))}
                className="rounded-md border border-border px-3 py-1 disabled:opacity-30"
              >
                Prev
              </button>
              <button
                disabled={offset + PAGE_SIZE >= data.total}
                onClick={() => setOffset(offset + PAGE_SIZE)}
                className="rounded-md border border-border px-3 py-1 disabled:opacity-30"
              >
                Next
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
