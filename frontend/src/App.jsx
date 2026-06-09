import { useState } from "react";
import TripForm from "./components/TripForm.jsx";
import AgentGraph from "./components/AgentGraph.jsx";

export default function App() {
  const [plan, setPlan] = useState(null);

  return (
    <div>
      <TripForm
        onPlan={(p) => {
          setPlan(p);
          window.__lastPlan = p;
        }}
      />
      <AgentGraph plan={plan} />
    </div>
  );
}
