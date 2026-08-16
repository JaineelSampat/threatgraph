interface BarChartProps {
  title: string;
  data: Record<string, number>;
  color: string;
}

/**
 * A hand-rolled horizontal bar chart. The dashboard only needs two small,
 * static breakdowns, so pulling in a charting library for this would be
 * the "no unnecessary dependencies" tradeoff the assignment warns about -
 * ~40 lines of SVG does the job and is trivial to explain line-by-line.
 */
export function BarChart({ title, data, color }: BarChartProps) {
  const entries = Object.entries(data).sort((a, b) => b[1] - a[1]);
  const max = Math.max(...entries.map(([, v]) => v), 1);

  return (
    <div className="rounded-lg border border-border bg-surface p-4">
      <p className="mb-3 font-mono text-[11px] uppercase tracking-wider text-ink-muted">{title}</p>
      <div className="flex flex-col gap-2">
        {entries.map(([label, value]) => (
          <div key={label} className="flex items-center gap-3">
            <span className="w-32 shrink-0 truncate text-xs text-ink-muted">{label}</span>
            <div className="h-2 flex-1 rounded-full bg-surface-raised">
              <div
                className="h-2 rounded-full transition-all"
                style={{ width: `${(value / max) * 100}%`, backgroundColor: color }}
              />
            </div>
            <span className="w-6 shrink-0 text-right font-mono text-xs text-ink">{value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
