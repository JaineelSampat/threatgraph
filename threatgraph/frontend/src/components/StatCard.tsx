export function StatCard({ label, value, accent }: { label: string; value: number; accent?: string }) {
  return (
    <div className="rounded-lg border border-border bg-surface p-4">
      <p className="font-mono text-[11px] uppercase tracking-wider text-ink-muted">{label}</p>
      <p className="mt-1 font-mono text-2xl font-semibold" style={accent ? { color: accent } : undefined}>
        {value.toLocaleString()}
      </p>
    </div>
  );
}
