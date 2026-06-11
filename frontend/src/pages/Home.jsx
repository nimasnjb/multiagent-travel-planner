import { useState } from "react";
import TripForm from "../components/TripForm.jsx";
import AgentGraph from "../components/AgentGraph.jsx";
import ItineraryMap from "../components/ItineraryMap.jsx";
import ItineraryText from "../components/ItineraryText.jsx";
import * as s from "./pageStyles.js";

export default function Home() {
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(false);

  return (
    <div style={s.page}>
      <header style={s.hero}>
        <div style={s.heroInner}>
          <p style={s.eyebrow}>Your trip, planned by AI agents</p>
          <h1 style={s.title}>Multi-Agent</h1>
          <h1 style={s.title}>Travel Planner</h1>
          <p style={s.subtitle}>
            Plan less. Experience more. Tell us your trip and a team of AI agents will research, budget, and route a day-by-day itinerary for you.
          </p>
          <TripForm onPlan={setPlan} onLoadingChange={setLoading} />
        </div>
      </header>

      <main style={s.main}>
        <AgentGraph plan={plan} loading={loading} />
        <ItineraryMap plan={plan} />
        <ItineraryText plan={plan} />
      </main>
    </div>
  );
}
