import { useEffect, useRef, useState } from "react";

const PIPELINE = ["preferences", "researcher", "budget", "logistics", "writer"];

// Total time (ms) for the indeterminate loading sweep to light all five
// nodes preferences -> writer while we wait for the real response. If the
// response arrives first we snap to the true agent_log state; if the sweep
// finishes first, the last node holds in a pulsing "working" state.
const LOADING_SWEEP_MS = 15000;

// Layout is computed in an SVG viewBox, then nodes/connectors are positioned
// as percentages of this box so the whole thing stays responsive.
const VIEW_W = 600;
const VIEW_H = 160;
const ARC_AMPLITUDE = 36; // how high the arc bows above the baseline
const BASE_Y = 110;       // y of the first/last node
const PAD_X = 60;         // horizontal margin before the first / after the last node

// Colors for the "completed" state. Idle styling keeps the warm-neutral
// theme tokens; completed nodes/connectors switch to green.
const DONE_COLOR = "#4f9d6e";
const DONE_COLOR_DARK = "#3c7d56";
const DONE_BORDER = "#3c7d56";

const PULSE_KEYFRAMES = `
@keyframes agent-graph-pulse {
  0%, 100% { opacity: 1; transform: translate(-50%, -50%) scale(1); }
  50% { opacity: 0.55; transform: translate(-50%, -50%) scale(1.08); }
}
`;

// Position of node `i` along a shallow left-to-right arc that peaks in the
// middle (a smooth semicircle-ish sweep).
function nodeCenter(i) {
  const t = i / (PIPELINE.length - 1);
  const x = PAD_X + t * (VIEW_W - 2 * PAD_X);
  const y = BASE_Y - ARC_AMPLITUDE * Math.sin(Math.PI * t);
  return { x, y, t };
}

// A polyline path tracing the same arc between two adjacent nodes, so each
// connector visually continues the curve instead of cutting straight across.
function connectorPath(i) {
  const STEPS = 16;
  const a = nodeCenter(i);
  const b = nodeCenter(i + 1);
  const points = [];
  for (let s = 0; s <= STEPS; s++) {
    const t = a.t + (b.t - a.t) * (s / STEPS);
    const x = PAD_X + t * (VIEW_W - 2 * PAD_X);
    const y = BASE_Y - ARC_AMPLITUDE * Math.sin(Math.PI * t);
    points.push(`${s === 0 ? "M" : "L"}${x.toFixed(2)},${y.toFixed(2)}`);
  }
  return points.join(" ");
}

const pct = (value, total) => `${(value / total) * 100}%`;

const styles = {
  graph: {
    position: "relative",
    width: "100%",
    maxWidth: 640,
    margin: "0 auto",
    aspectRatio: `${VIEW_W} / ${VIEW_H}`,
    padding: "24px 8px",
    background: "var(--color-surface)",
    borderRadius: "var(--radius-lg)",
    boxShadow: "var(--shadow-card)",
  },
  svg: {
    position: "absolute",
    inset: 0,
    width: "100%",
    height: "100%",
  },
  circle: (state, x, y) => ({
    position: "absolute",
    left: pct(x, VIEW_W),
    top: pct(y, VIEW_H),
    transform: "translate(-50%, -50%)",
    width: 48,
    height: 48,
    borderRadius: "50%",
    background: state === "done" ? DONE_COLOR : "var(--color-idle)",
    border: `2px solid ${state === "done" ? DONE_BORDER : "var(--color-idle-border)"}`,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    transition: "background 0.3s, border-color 0.3s",
    animation: state === "working" ? "agent-graph-pulse 1.2s ease-in-out infinite" : "none",
  }),
  icon: (state) => ({
    width: 22,
    height: 22,
    color: state === "done" ? "#fff" : "var(--color-text-muted)",
    transition: "color 0.3s",
  }),
  label: (state, x, y) => ({
    position: "absolute",
    left: pct(x, VIEW_W),
    top: pct(y, VIEW_H),
    transform: "translate(-50%, -50%)",
    fontFamily: "var(--font-body)",
    fontSize: 11,
    fontWeight: 600,
    textTransform: "capitalize",
    color: state === "done" ? DONE_COLOR_DARK : "var(--color-text-muted)",
    letterSpacing: "0.02em",
    whiteSpace: "nowrap",
    transition: "color 0.3s",
  }),
};

// Minimal inline glyphs (feather-style: 24x24, stroke-based, currentColor).
function IconPreferences(props) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
      <line x1="4" y1="21" x2="4" y2="14" />
      <line x1="4" y1="10" x2="4" y2="3" />
      <circle cx="4" cy="12" r="2" />
      <line x1="12" y1="21" x2="12" y2="12" />
      <line x1="12" y1="8" x2="12" y2="3" />
      <circle cx="12" cy="10" r="2" />
      <line x1="20" y1="21" x2="20" y2="16" />
      <line x1="20" y1="12" x2="20" y2="3" />
      <circle cx="20" cy="14" r="2" />
    </svg>
  );
}

function IconResearcher(props) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
      <circle cx="11" cy="11" r="7" />
      <line x1="21" y1="21" x2="16.65" y2="16.65" />
    </svg>
  );
}

function IconBudget(props) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
      <path d="M21 7H5a2 2 0 0 1 0-4h13v4" />
      <rect x="3" y="7" width="18" height="13" rx="2" />
      <circle cx="16" cy="13.5" r="1.2" fill="currentColor" stroke="none" />
    </svg>
  );
}

function IconLogistics(props) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
      <circle cx="6" cy="19" r="2.5" />
      <circle cx="18" cy="5" r="2.5" />
      <path d="M8.5 19h6a3 3 0 0 0 3-3v-1a3 3 0 0 0-3-3h-5a3 3 0 0 1-3-3v-1a3 3 0 0 1 3-3h2.5" />
    </svg>
  );
}

function IconWriter(props) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
      <path d="M12 20h9" />
      <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4z" />
    </svg>
  );
}

const ICONS = {
  preferences: IconPreferences,
  researcher: IconResearcher,
  budget: IconBudget,
  logistics: IconLogistics,
  writer: IconWriter,
};

export default function AgentGraph({ plan, loading }) {
  // `elapsed` drives the indeterminate loading sweep: 0 at the start of a
  // new submit, counting up to LOADING_SWEEP_MS while `loading` is true.
  const [elapsed, setElapsed] = useState(0);
  const rafRef = useRef(null);

  useEffect(() => {
    if (rafRef.current != null) {
      cancelAnimationFrame(rafRef.current);
      rafRef.current = null;
    }

    if (!loading) return undefined;

    const start = performance.now();
    setElapsed(0);

    const tick = (now) => {
      const e = Math.min(now - start, LOADING_SWEEP_MS);
      setElapsed(e);
      if (e < LOADING_SWEEP_MS) {
        rafRef.current = requestAnimationFrame(tick);
      } else {
        rafRef.current = null;
      }
    };
    rafRef.current = requestAnimationFrame(tick);

    return () => {
      if (rafRef.current != null) {
        cancelAnimationFrame(rafRef.current);
        rafRef.current = null;
      }
    };
  }, [loading]);

  if (!loading && !plan) return null;

  const log = plan?.meta?.agent_log ?? [];
  const lit = new Set(log.map((entry) => entry.agent));
  const total = PIPELINE.length;
  const stepDuration = LOADING_SWEEP_MS / total;

  // While loading: indeterminate sweep driven by `elapsed`. Once resolved
  // (loading is false and we have a plan): snap straight to the true
  // agent_log state, no animation.
  function nodeState(i) {
    if (!loading) {
      return lit.has(PIPELINE[i]) ? "done" : "idle";
    }
    const threshold = (i + 1) * stepDuration;
    if (elapsed < threshold) return "idle";
    return i === total - 1 ? "working" : "done";
  }

  function connectorProgress(i) {
    if (!loading) {
      return lit.has(PIPELINE[i]) && lit.has(PIPELINE[i + 1]) ? 1 : 0;
    }
    const threshold = (i + 1) * stepDuration;
    const raw = (elapsed - threshold) / stepDuration;
    return Math.min(1, Math.max(0, raw));
  }

  return (
    <div style={styles.graph} aria-label="Agent pipeline">
      <style>{PULSE_KEYFRAMES}</style>
      <svg style={styles.svg} viewBox={`0 0 ${VIEW_W} ${VIEW_H}`} preserveAspectRatio="none">
        {PIPELINE.slice(0, -1).map((name, i) => {
          const d = connectorPath(i);
          const progress = connectorProgress(i);
          return (
            <g key={`${name}-conn`}>
              <path
                d={d}
                strokeWidth={2}
                style={{ fill: "none", stroke: "var(--color-idle-border)" }}
              />
              {progress > 0 && (
                <path
                  d={d}
                  strokeWidth={2}
                  pathLength={100}
                  strokeDasharray={100}
                  strokeDashoffset={100 - progress * 100}
                  style={{ fill: "none", stroke: DONE_COLOR }}
                />
              )}
            </g>
          );
        })}
      </svg>

      {PIPELINE.map((name, i) => {
        const state = nodeState(i);
        const { x, y } = nodeCenter(i);
        const Icon = ICONS[name];
        return (
          <div key={name}>
            <div style={styles.circle(state, x, y)} title={name}>
              <Icon style={styles.icon(state)} />
            </div>
            <span style={styles.label(state, x, y + 34)}>{name}</span>
          </div>
        );
      })}
    </div>
  );
}
