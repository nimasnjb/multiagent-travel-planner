const PIPELINE = ["preferences", "researcher", "budget", "logistics", "writer"];

const styles = {
  graph: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    padding: "16px 8px",
    gap: 0,
  },
  node: (done) => ({
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: 6,
  }),
  circle: (done) => ({
    width: 48,
    height: 48,
    borderRadius: "50%",
    background: done ? "#22c55e" : "#d1d5db",
    border: `2px solid ${done ? "#16a34a" : "#9ca3af"}`,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    transition: "background 0.3s, border-color 0.3s",
  }),
  icon: (done) => ({
    fontSize: 20,
    color: done ? "#fff" : "#6b7280",
  }),
  label: (done) => ({
    fontSize: 11,
    fontWeight: 600,
    textTransform: "capitalize",
    color: done ? "#16a34a" : "#9ca3af",
    letterSpacing: "0.02em",
  }),
  connector: (done) => ({
    flex: "0 0 32px",
    height: 2,
    background: done ? "#22c55e" : "#d1d5db",
    alignSelf: "center",
    marginBottom: 22,
    transition: "background 0.3s",
  }),
};

const ICONS = {
  preferences: "🧭",
  researcher:  "🔍",
  budget:      "💰",
  logistics:   "🗺️",
  writer:      "✍️",
};

export default function AgentGraph({ plan }) {
  if (!plan) return null;

  const log = plan.meta?.agent_log ?? [];
  const lit = new Set(log.map((entry) => entry.agent));

  return (
    <div style={styles.graph} aria-label="Agent pipeline">
      {PIPELINE.flatMap((name, i) => {
        const done = lit.has(name);
        const node = (
          <div key={name} style={styles.node(done)}>
            <div style={styles.circle(done)} title={name}>
              <span style={styles.icon(done)}>{ICONS[name]}</span>
            </div>
            <span style={styles.label(done)}>{name}</span>
          </div>
        );
        if (i < PIPELINE.length - 1) {
          const connDone = done && lit.has(PIPELINE[i + 1]);
          return [node, <div key={`${name}-conn`} style={styles.connector(connDone)} />];
        }
        return [node];
      })}
    </div>
  );
}
