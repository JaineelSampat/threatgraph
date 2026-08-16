import { ENTITY_TYPE_META } from "../lib/entityTypeMeta";
import type { EntityType } from "../types/api";

export function EntityTypeBadge({ entityType, size = "sm" }: { entityType: EntityType; size?: "sm" | "md" }) {
  const meta = ENTITY_TYPE_META[entityType];
  const sizeClasses = size === "sm" ? "text-[10px] px-1.5 py-0.5" : "text-xs px-2 py-1";
  return (
    <span
      className={`inline-flex items-center rounded border font-mono font-medium uppercase tracking-wider ${sizeClasses} ${meta.badgeClass}`}
      title={meta.displayName}
    >
      {meta.abbreviation}
    </span>
  );
}
