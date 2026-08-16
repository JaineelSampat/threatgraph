import { FormEvent, useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";

const LINKS = [
  { to: "/", label: "Dashboard", end: true },
  { to: "/explorer", label: "Explorer" },
  { to: "/investigate", label: "Investigate" },
];

export function Nav() {
  const [query, setQuery] = useState("");
  const navigate = useNavigate();

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const trimmed = query.trim();
    if (trimmed.length >= 2) {
      navigate(`/explorer?q=${encodeURIComponent(trimmed)}`);
    }
  }

  return (
    <header className="sticky top-0 z-10 border-b border-border bg-bg/95 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center gap-6 px-4 py-3">
        <NavLink to="/" className="flex items-center gap-2 font-mono text-sm font-semibold tracking-wide text-ink">
          <span className="h-2 w-2 rounded-full bg-accent-cyan shadow-glow" />
          THREATGRAPH
        </NavLink>

        <nav className="flex items-center gap-1">
          {LINKS.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.end}
              className={({ isActive }) =>
                `rounded-md px-3 py-1.5 text-sm transition ${
                  isActive ? "bg-surface-raised text-accent-cyan" : "text-ink-muted hover:text-ink"
                }`
              }
            >
              {link.label}
            </NavLink>
          ))}
        </nav>

        <form onSubmit={handleSubmit} className="ml-auto w-full max-w-xs">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            type="search"
            placeholder="Search actors, malware, CVEs…"
            className="w-full rounded-md border border-border bg-surface px-3 py-1.5 text-sm text-ink placeholder:text-ink-faint focus:border-accent-cyan focus:outline-none"
          />
        </form>
      </div>
    </header>
  );
}
