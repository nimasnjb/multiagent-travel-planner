import { useState } from "react";
import { callPlan } from "../api";

/**
 * Takes the free-text trip request, calls the backend, and lifts the
 * resulting Plan to the parent. Handles the clarification round-trip
 * (asking the follow-up question, re-calling with prior_state) but does
 * not look inside the resolved Plan beyond preferences.clarification_needed.
 */
export default function TripForm({ onPlan, onLoadingChange }) {
  const [request, setRequest] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [clarification, setClarification] = useState(null);
  const [priorState, setPriorState] = useState(null);

  async function runPlan(text, prior) {
    setLoading(true);
    onLoadingChange?.(true);
    setError(null);
    try {
      const plan = await callPlan(text, prior);
      const question = plan.preferences?.clarification_needed ?? null;
      setPriorState(question ? plan : null);
      setClarification(question);
      onPlan(plan);
      if (!question) {
        setAnswer("");
      }
    } catch (err) {
      setError(err.message ?? String(err));
    } finally {
      setLoading(false);
      onLoadingChange?.(false);
    }
  }

  function handleRequestSubmit(event) {
    event.preventDefault();
    if (!request.trim() || loading) return;
    runPlan(request, null);
  }

  function handleAnswerSubmit(event) {
    event.preventDefault();
    if (!answer.trim() || loading) return;
    runPlan(answer, priorState);
  }

  return (
    <div className="trip-form">
      <form onSubmit={handleRequestSubmit}>
        <input
          type="text"
          value={request}
          onChange={(event) => setRequest(event.target.value)}
          placeholder="Describe your trip (Barcelona, paella, 3 days, 500 euros)"
          disabled={loading}
        />
        <button type="submit" disabled={loading}>
          Plan my trip
        </button>
      </form>

      {clarification && (
        <form onSubmit={handleAnswerSubmit}>
          <p>{clarification}</p>
          <input
            type="text"
            value={answer}
            onChange={(event) => setAnswer(event.target.value)}
            placeholder="Your answer…"
            disabled={loading}
          />
          <button type="submit" disabled={loading}>
            Send answer
          </button>
        </form>
      )}

      {error && <p className="trip-form-error" role="alert">{error}</p>}
    </div>
  );
}
