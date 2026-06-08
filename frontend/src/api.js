const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

/**
 * Calls POST /plan and returns the parsed Plan object.
 * @param {string} request - free-text trip description
 * @param {object|null} [priorState] - previous Plan, sent back after a clarification answer
 * @returns {Promise<object>} the Plan returned by the backend
 */
export async function callPlan(request, priorState = null) {
  const response = await fetch(`${API_URL}/plan`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ request, prior_state: priorState }),
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`POST /plan failed (${response.status}): ${body}`);
  }

  return response.json();
}
