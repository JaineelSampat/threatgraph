export function LoadingState({ label = "Loading…" }: { label?: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-20 text-ink-muted">
      <div className="h-8 w-8 animate-spin rounded-full border-2 border-border border-t-accent-cyan" />
      <p className="font-mono text-sm tracking-wide">{label}</p>
    </div>
  );
}

export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-lg border border-accent-red/30 bg-accent-red/5 px-6 py-16 text-center">
      <p className="font-mono text-sm text-accent-red">Something went wrong</p>
      <p className="max-w-md text-sm text-ink-muted">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-2 rounded-md border border-border px-4 py-1.5 text-sm text-ink transition hover:border-accent-cyan hover:text-accent-cyan"
        >
          Try again
        </button>
      )}
    </div>
  );
}

export function EmptyState({ title, description }: { title: string; description?: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 rounded-lg border border-dashed border-border px-6 py-16 text-center">
      <p className="font-mono text-sm text-ink-muted">{title}</p>
      {description && <p className="max-w-md text-sm text-ink-faint">{description}</p>}
    </div>
  );
}
