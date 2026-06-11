import * as s from "./pageStyles.js";

const styles = {
  grid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
    gap: 16,
  },
  stepBadge: {
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    width: 28,
    height: 28,
    borderRadius: "50%",
    background: "var(--color-accent-soft)",
    color: "var(--color-accent-active)",
    fontFamily: "var(--font-display)",
    fontWeight: 700,
    fontSize: 14,
    flexShrink: 0,
  },
  cardHead: {
    display: "flex",
    alignItems: "center",
    gap: 12,
    marginBottom: 8,
  },
  iconWrap: {
    width: 36,
    height: 36,
    borderRadius: "50%",
    background: "var(--color-idle)",
    border: "2px solid var(--color-idle-border)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    color: "var(--color-accent-active)",
    flexShrink: 0,
  },
  icon: {
    width: 18,
    height: 18,
  },
  arrowRow: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    color: "var(--color-text-muted)",
    fontSize: 22,
    margin: "-4px 0",
  },
  calloutTitle: {
    ...s.sectionTitle,
    color: "var(--color-accent-active)",
  },
};

const iconProps = {
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: "2",
  strokeLinecap: "round",
  strokeLinejoin: "round",
};

const ICONS = {
  preferences: (
    <svg {...iconProps} style={styles.icon}>
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
  ),
  researcher: (
    <svg {...iconProps} style={styles.icon}>
      <circle cx="11" cy="11" r="7" />
      <line x1="21" y1="21" x2="16.65" y2="16.65" />
    </svg>
  ),
  budget: (
    <svg {...iconProps} style={styles.icon}>
      <path d="M21 7H5a2 2 0 0 1 0-4h13v4" />
      <rect x="3" y="7" width="18" height="13" rx="2" />
      <circle cx="16" cy="13.5" r="1.2" fill="currentColor" stroke="none" />
    </svg>
  ),
  logistics: (
    <svg {...iconProps} style={styles.icon}>
      <circle cx="6" cy="19" r="2.5" />
      <circle cx="18" cy="5" r="2.5" />
      <path d="M8.5 19h6a3 3 0 0 0 3-3v-1a3 3 0 0 0-3-3h-5a3 3 0 0 1-3-3v-1a3 3 0 0 1 3-3h2.5" />
    </svg>
  ),
  writer: (
    <svg {...iconProps} style={styles.icon}>
      <path d="M12 20h9" />
      <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4z" />
    </svg>
  ),
  branch: (
    <svg {...iconProps} style={styles.icon}>
      <circle cx="6" cy="6" r="2.5" />
      <circle cx="6" cy="18" r="2.5" />
      <circle cx="18" cy="6" r="2.5" />
      <path d="M6 8.5v7" />
      <path d="M8.5 6h5a3 3 0 0 1 3 3v0" />
    </svg>
  ),
};

const STEPS = [
  {
    id: "preferences",
    name: "Preferences",
    text:
      "Reads your free-text request and turns it into structured preferences — destination, dates, budget, interests. If something critical is missing, like the destination or trip length, the graph branches to a clarifying question instead of guessing.",
  },
  {
    id: "researcher",
    name: "Researcher",
    text:
      "Queries OpenRouteService for real venues that match your interests, then the LLM ranks and filters from those results only. It never invents a place that isn’t actually there.",
  },
  {
    id: "budget",
    name: "Budget",
    text:
      "Code-led greedy allocation fits the best candidates into your budget. The LLM is only consulted for splurge-vs-save judgment calls when things are tight.",
  },
  {
    id: "logistics",
    name: "Logistics",
    text:
      "Pulls a real travel-time matrix from OpenRouteService and runs OR-Tools to solve the optimal visit order and arrival/departure times for each day — zero LLM involvement.",
  },
  {
    id: "writer",
    name: "Writer",
    text:
      "Turns the finalized, ordered itinerary into a friendly day-by-day narrative — prose only, never reordering stops or changing times.",
  },
];

export default function HowItWorks() {
  return (
    <div style={s.page}>
      <header style={s.hero}>
        <div style={s.heroInner}>
          <p style={s.eyebrow}>Under the hood</p>
          <h1 style={s.title}>How it works</h1>
          <p style={s.subtitle}>
            Your trip is planned by a real LangGraph pipeline of five
            specialist agents — each one doing exactly one job, in order,
            with the LLM kept on a short leash.
          </p>
        </div>
      </header>

      <main style={s.main}>
        <div style={styles.grid}>
          {STEPS.map((step, i) => (
            <div key={step.id}>
              <div style={s.card}>
                <div style={styles.cardHead}>
                  <span style={styles.stepBadge}>{i + 1}</span>
                  <div style={styles.iconWrap}>{ICONS[step.id]}</div>
                  <h2 style={{ ...s.sectionTitle, margin: 0, fontSize: "1.1rem" }}>
                    {step.name}
                  </h2>
                </div>
                <p style={s.bodyText}>{step.text}</p>
              </div>
              {i < STEPS.length - 1 && <div style={styles.arrowRow}>&#8595;</div>}
            </div>
          ))}
        </div>

        <div style={s.card}>
          <div style={styles.cardHead}>
            <div style={styles.iconWrap}>{ICONS.branch}</div>
            <h2 style={styles.calloutTitle}>The clarification branch</h2>
          </div>
          <p style={s.bodyText}>
            This is a real branch in the graph, not a scripted dialog. If the
            preferences agent can’t pin down something critical — no
            destination, no sense of dates or trip length — a conditional
            edge routes the run straight to the end and sends back a
            clarifying question. Your answer is appended to the request and
            the graph runs again from the top, this time with enough
            information to continue through researcher, budget, logistics,
            and writer.
          </p>
        </div>

        <div style={s.card}>
          <h2 style={s.sectionTitle}>What you’re actually seeing</h2>
          <p style={s.bodyText}>
            On the home page, the agent arc above the planner lights up
            node-by-node as each of these agents completes — it’s a live
            readout of this exact graph, not a fake loading bar. Real venues
            come from OpenRouteService, the visit order and timing come from
            OR-Tools, and the language model is only ever responsible for
            understanding your request, ranking/filtering real options, and
            writing the final narrative.
          </p>
        </div>
      </main>
    </div>
  );
}
