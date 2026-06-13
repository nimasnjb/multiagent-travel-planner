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
  aboutGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
    gap: 16,
  },
  blueIconWrap: {
    width: 36,
    height: 36,
    borderRadius: "50%",
    background: "rgba(37, 99, 235, 0.12)",
    border: "2px solid rgba(37, 99, 235, 0.28)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    color: "#2563eb",
    flexShrink: 0,
  },
  blueTitle: {
    ...s.sectionTitle,
    color: "#2563eb",
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
  about: (
    <svg {...iconProps} style={styles.icon}>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 16v-4" />
      <path d="M12 8h.01" />
    </svg>
  ),
  stack: (
    <svg {...iconProps} style={styles.icon}>
      <path d="M12 3 3 8l9 5 9-5-9-5z" />
      <path d="m3 12 9 5 9-5" />
      <path d="m3 16 9 5 9-5" />
    </svg>
  ),
  architecture: (
    <svg {...iconProps} style={styles.icon}>
      <rect x="3" y="3" width="7" height="7" rx="1.5" />
      <rect x="14" y="3" width="7" height="7" rx="1.5" />
      <rect x="8.5" y="14" width="7" height="7" rx="1.5" />
      <path d="M10 6.5h4" />
      <path d="M7.5 10v2.5A1.5 1.5 0 0 0 9 14" />
      <path d="M16.5 10v2.5A1.5 1.5 0 0 1 15 14" />
    </svg>
  ),
  reliability: (
    <svg {...iconProps} style={styles.icon}>
      <path d="M20 6 9 17l-5-5" />
      <path d="M4 19h16" />
    </svg>
  ),
};


const STEPS = [
  {
    id: "preferences",
    name: "Preferences Agent",
    text:
      "The Preferences agent uses OpenAI gpt-4o-mini through the official OpenAI SDK to turn a plain-English trip request into validated Pydantic data: destination, dates or trip length, budget, interests, pace, and must-sees. If a critical detail is missing, it does not guess — LangGraph routes the flow to a clarification branch and asks the user a follow-up question before planning continues. OpenAI API usage is paid per token, so the project keeps all model calls behind one backend wrapper for easier cost control.",
  },
  {
    id: "researcher",
    name: "Researcher Agent",
    text:
      "The Researcher agent connects to OpenRouteService, a free-to-start HeiGIT service, to search for real places of interest near the destination. The LLM can rank and filter those returned venues, but it is not allowed to invent attractions, restaurants, or stops. This keeps the demo grounded in live geographic data instead of hallucinated travel suggestions.",
  },
  {
    id: "budget",
    name: "Budget Agent",
    text:
      "The Budget agent is mostly deterministic Python code. It uses a greedy allocation strategy to fit the strongest candidate stops into the user’s total budget while preserving must-see items where possible. The LLM is only used for judgment calls, such as whether a tight itinerary should prioritize one splurge experience or several lower-cost stops.",
  },
  {
    id: "logistics",
    name: "Logistics Agent",
    text:
      "The Logistics agent handles the route planning without any LLM decision-making. It requests a travel-time matrix and directions geometry from OpenRouteService, then uses Google OR-Tools to solve the optimal visit order for each day, including arrival and departure times. This separates creative language generation from hard routing logic, so the final schedule is produced by code rather than by a model guessing the best order.",
  },
  {
    id: "writer",
    name: "Writer Agent",
    text:
      "The Writer agent turns the finished, ordered plan into a friendly day-by-day itinerary. It uses the LLM for presentation only: it can explain the plan, add helpful travel context, and make the itinerary enjoyable to read, but it cannot reorder stops, change times, or add new venues.",
  },
];

const ABOUT_PROJECT =
  "Multi-Agent Travel Planner is a portfolio web app that shows how an AI travel-planning workflow can be split into specialized agents instead of asking one model to do everything. A user describes a trip in natural language, and a LangGraph StateGraph coordinates five agents: preferences, researcher, budget, logistics, and writer. The result is a structured itinerary, a map route, and a live visualization of the agents handing work to each other.";

const ABOUT_TECH =
  "The backend is built with Python 3.11+, FastAPI, Uvicorn, Pydantic, LangGraph v1, the OpenAI SDK, OpenRouteService, and Google OR-Tools. The frontend uses React with Vite, Leaflet, react-leaflet, and OpenStreetMap tiles. The planned deployment keeps the project inexpensive for a showcase build: the backend can run on Render’s free tier, the frontend can be hosted with GitHub Pages, OpenRouteService offers a free standard API plan with limits, and OpenStreetMap map data is free to use as long as tile usage policies are respected. OpenAI API calls are the main paid usage-based dependency.";

const ABOUT_ARCHITECTURE =
  "The key design idea is that the LLM is not the planner of record. The model parses preferences, ranks real search results, helps with tradeoff language, and writes the final narrative. Real place data comes from OpenRouteService, route order comes from OR-Tools, and every node writes validated state through Pydantic. LangGraph controls the workflow, including the clarification branch, and the frontend animation is driven by the agent log emitted by each node.";

const ABOUT_RELIABILITY =
  "The project is designed to be testable, not just visually impressive. Each agent is implemented as an importable node with fake LLM and OpenRouteService clients available for tests. Deterministic pieces like budgeting and logistics are checked with unit tests, while fuzzy LLM outputs are evaluated with property-style cases. A node is considered done only when the relevant tests are green.";

const ABOUT_SECTIONS = [
  {
    id: "project",
    name: "Project overview",
    icon: ICONS.about,
    text: ABOUT_PROJECT,
  },
  {
    id: "tech",
    name: "Technologies & services",
    icon: ICONS.stack,
    text: ABOUT_TECH,
  },
  {
    id: "architecture",
    name: "Architecture principle",
    icon: ICONS.architecture,
    text: ABOUT_ARCHITECTURE,
  },
  {
    id: "reliability",
    name: "Reliability & testing",
    icon: ICONS.reliability,
    text: ABOUT_RELIABILITY,
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
            </div>
          ))}
        </div>

        <div style={styles.aboutGrid}>
          {ABOUT_SECTIONS.map((section) => (
            <div key={section.id} style={s.card}>
              <div style={styles.cardHead}>
                <div style={styles.blueIconWrap}>{section.icon}</div>
                <h2 style={{ ...styles.blueTitle, margin: 0 }}>
                  {section.name}
                </h2>
              </div>
              <p style={s.bodyText}>{section.text}</p>
            </div>
          ))}
        </div>

        <div style={s.card}>
          <div style={styles.cardHead}>
            <div style={styles.blueIconWrap}>{ICONS.branch}</div>
            <h2 style={styles.blueTitle}>The clarification branch</h2>
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
