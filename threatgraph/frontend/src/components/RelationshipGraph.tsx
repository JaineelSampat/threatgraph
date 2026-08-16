import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ENTITY_TYPE_META } from "../lib/entityTypeMeta";
import type { GraphEdge, GraphNode } from "../types/api";

interface Point {
  x: number;
  y: number;
  vx: number;
  vy: number;
}

const WIDTH = 640;
const HEIGHT = 420;
const CENTER = { x: WIDTH / 2, y: HEIGHT / 2 };

// Physics constants for the force simulation below.
const REPULSION = 2200; // how strongly every pair of nodes pushes apart (Coulomb-style)
const SPRING_LENGTH = 130; // resting length of an edge (Hooke's law)
const SPRING_STRENGTH = 0.02;
const CENTERING = 0.002; // gentle pull back toward the middle of the canvas
const DAMPING = 0.82;
const MAX_TICKS = 220;
const SETTLE_THRESHOLD = 0.05;

/**
 * A small, self-contained force-directed graph: every node repels every
 * other node, edges act as springs pulling connected nodes together, and
 * a weak centering force keeps the whole thing on-canvas. This is the
 * one place in the app that owns real interaction design - nodes are
 * draggable, and clicking a non-focus node navigates to its detail page.
 *
 * Written by hand instead of pulling in d3-force: for a graph this small
 * (under ~20 nodes) a ~60-line simulation is easy to defend line-by-line,
 * and it avoids a dependency whose internals nobody on this project has
 * to reason about in an interview.
 */
export function RelationshipGraph({
  nodes,
  edges,
  focusId,
}: {
  nodes: GraphNode[];
  edges: GraphEdge[];
  focusId?: string;
}) {
  const positionsRef = useRef<Record<string, Point>>({});
  const draggingRef = useRef<string | null>(null);
  const pointerDownRef = useRef<{ id: string; x: number; y: number } | null>(null);
  const [, bumpRenderTick] = useState(0);
  const navigate = useNavigate();

  useEffect(() => {
    const existing = positionsRef.current;
    const next: Record<string, Point> = {};
    nodes.forEach((n, i) => {
      if (existing[n.id]) {
        next[n.id] = existing[n.id];
        return;
      }
      const angle = (i / Math.max(nodes.length, 1)) * Math.PI * 2;
      const radius = n.id === focusId ? 0 : 130;
      next[n.id] = {
        x: CENTER.x + Math.cos(angle) * radius,
        y: CENTER.y + Math.sin(angle) * radius,
        vx: 0,
        vy: 0,
      };
    });
    positionsRef.current = next;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [nodes, focusId]);

  useEffect(() => {
    let frame: number;
    let ticks = 0;

    function tick() {
      const positions = positionsRef.current;
      const ids = nodes.map((n) => n.id);

      for (let i = 0; i < ids.length; i++) {
        for (let j = i + 1; j < ids.length; j++) {
          const a = positions[ids[i]];
          const b = positions[ids[j]];
          if (!a || !b) continue;
          const dx = a.x - b.x;
          const dy = a.y - b.y;
          const distSq = Math.max(dx * dx + dy * dy, 40);
          const force = REPULSION / distSq;
          const dist = Math.sqrt(distSq);
          const fx = (dx / dist) * force;
          const fy = (dy / dist) * force;
          a.vx += fx;
          a.vy += fy;
          b.vx -= fx;
          b.vy -= fy;
        }
      }

      edges.forEach((e) => {
        const a = positions[e.source];
        const b = positions[e.target];
        if (!a || !b) return;
        const dx = b.x - a.x;
        const dy = b.y - a.y;
        const dist = Math.max(Math.sqrt(dx * dx + dy * dy), 1);
        const force = (dist - SPRING_LENGTH) * SPRING_STRENGTH;
        const fx = (dx / dist) * force;
        const fy = (dy / dist) * force;
        a.vx += fx;
        a.vy += fy;
        b.vx -= fx;
        b.vy -= fy;
      });

      let maxDisplacement = 0;
      ids.forEach((id) => {
        const p = positions[id];
        if (!p || draggingRef.current === id) return;
        p.vx += (CENTER.x - p.x) * CENTERING;
        p.vy += (CENTER.y - p.y) * CENTERING;
        p.vx *= DAMPING;
        p.vy *= DAMPING;
        p.x += p.vx;
        p.y += p.vy;
        p.x = Math.min(Math.max(p.x, 24), WIDTH - 24);
        p.y = Math.min(Math.max(p.y, 24), HEIGHT - 24);
        maxDisplacement = Math.max(maxDisplacement, Math.abs(p.vx) + Math.abs(p.vy));
      });

      ticks += 1;
      bumpRenderTick((n) => n + 1);

      if (ticks < MAX_TICKS && maxDisplacement > SETTLE_THRESHOLD) {
        frame = requestAnimationFrame(tick);
      }
    }

    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [nodes, edges]);

  function handlePointerDown(id: string, e: React.PointerEvent) {
    draggingRef.current = id;
    pointerDownRef.current = { id, x: e.clientX, y: e.clientY };
  }
  function handlePointerUp() {
    draggingRef.current = null;
  }
  function handlePointerMove(e: React.PointerEvent<SVGSVGElement>) {
    const id = draggingRef.current;
    if (!id) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const p = positionsRef.current[id];
    if (!p) return;
    p.x = ((e.clientX - rect.left) / rect.width) * WIDTH;
    p.y = ((e.clientY - rect.top) / rect.height) * HEIGHT;
    p.vx = 0;
    p.vy = 0;
    bumpRenderTick((n) => n + 1);
  }
  function handleNodeClick(id: string, e: React.PointerEvent) {
    const start = pointerDownRef.current;
    const moved = start && start.id === id ? Math.hypot(e.clientX - start.x, e.clientY - start.y) : 0;
    if (moved < 4 && id !== focusId) {
      navigate(`/entity/${encodeURIComponent(id)}`);
    }
  }

  const positions = positionsRef.current;

  return (
    <svg
      viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
      className="h-full w-full touch-none select-none"
      onPointerMove={handlePointerMove}
      onPointerUp={handlePointerUp}
      onPointerLeave={handlePointerUp}
      role="img"
      aria-label="Relationship graph"
    >
      {[80, 150, 210].map((r) => (
        <circle key={r} cx={CENTER.x} cy={CENTER.y} r={r} fill="none" stroke="#1A232B" strokeWidth={1} />
      ))}
      {edges.map((e, i) => {
        const a = positions[e.source];
        const b = positions[e.target];
        if (!a || !b) return null;
        return (
          <g key={`${e.source}-${e.target}-${i}`}>
            <line x1={a.x} y1={a.y} x2={b.x} y2={b.y} stroke="#2A3742" strokeWidth={1.5} />
            <text
              x={(a.x + b.x) / 2}
              y={(a.y + b.y) / 2 - 4}
              textAnchor="middle"
              fontSize={8}
              className="fill-ink-faint font-mono"
            >
              {e.relationship_type}
            </text>
          </g>
        );
      })}
      {nodes.map((n) => {
        const p = positions[n.id];
        if (!p) return null;
        const meta = ENTITY_TYPE_META[n.entity_type];
        const isFocus = n.id === focusId;
        return (
          <g
            key={n.id}
            transform={`translate(${p.x}, ${p.y})`}
            onPointerDown={(e) => handlePointerDown(n.id, e)}
            onPointerUp={(e) => handleNodeClick(n.id, e)}
            className={isFocus ? "cursor-default" : "cursor-pointer"}
          >
            <circle
              r={isFocus ? 13 : 8}
              fill={meta.color}
              fillOpacity={isFocus ? 0.95 : 0.75}
              stroke={isFocus ? "#E7ECF0" : "none"}
              strokeWidth={1.5}
            />
            <text y={isFocus ? 27 : 20} textAnchor="middle" fontSize={9} className="fill-ink font-mono">
              {n.label.length > 18 ? `${n.label.slice(0, 16)}…` : n.label}
            </text>
          </g>
        );
      })}
    </svg>
  );
}
