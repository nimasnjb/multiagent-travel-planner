import { useState } from "react";
import TripForm from "./components/TripForm.jsx";
import AgentGraph from "./components/AgentGraph.jsx";
import ItineraryMap from "./components/ItineraryMap.jsx";
import ItineraryText from "./components/ItineraryText.jsx";

const s = {
  page: {
    fontFamily: "system-ui, sans-serif",
    maxWidth: 860,
    margin: "0 auto",
    padding: "0 16px 48px",
  },
  hero: {
    padding: "48px 0 32px",
    textAlign: "center",
  },
  title: {
    fontSize: 32,
    fontWeight: 700,
    margin: "0 0 8px",
    color: "#111827",
  },
  subtitle: {
    fontSize: 16,
    color: "#6b7280",
    margin: "0 0 32px",
  },
  divider: {
    border: "none",
    borderTop: "1px solid #e5e7eb",
    margin: "32px 0",
  },
};

export default function App() {
  const [plan, setPlan] = useState(null);

  return (
    <div style={s.page}>
      <header style={s.hero}>
        <h1 style={s.title}>Multi-Agent Travel Planner</h1>
        <p style={s.subtitle}>
          Describe your trip and a team of AI agents will plan it for you.
        </p>
        <TripForm onPlan={setPlan} />
      </header>

      <hr style={s.divider} />

      <AgentGraph plan={plan} />
      <ItineraryMap plan={plan} />
      <ItineraryText plan={plan} />
    </div>
  );
}
