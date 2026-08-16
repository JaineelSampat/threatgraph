import { Link } from "react-router-dom";
import { EntityTypeBadge } from "./EntityTypeBadge";
import type { EntitySummary } from "../types/api";

export function EntityCard({ entity }: { entity: EntitySummary }) {
  return (
    <Link
      to={`/entity/${encodeURIComponent(entity.id)}`}
      className="group flex flex-col gap-2 rounded-lg border border-border bg-surface p-4 transition hover:border-accent-cyan/50 hover:bg-surface-raised hover:shadow-glow"
    >
      <div className="flex items-center justify-between">
        <EntityTypeBadge entityType={entity.entity_type} />
        <span className="font-mono text-[10px] text-ink-faint">{entity.id}</span>
      </div>
      <p className="font-medium text-ink group-hover:text-accent-cyan">{entity.label}</p>
      {entity.subtitle && <p className="text-sm text-ink-muted">{entity.subtitle}</p>}
    </Link>
  );
}
