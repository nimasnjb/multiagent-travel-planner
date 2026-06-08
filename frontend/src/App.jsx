import TripForm from "./components/TripForm.jsx";

// Throwaway mount for exercising TripForm in the browser — replaced by the real App later.
export default function App() {
  return (
    <TripForm
      onPlan={(plan) => {
        console.log("PLAN:", plan);
        window.__lastPlan = plan;
      }}
    />
  );
}
