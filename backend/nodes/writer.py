import json
import time

from backend.llm import llm
from backend.schemas import Plan

_SYSTEM = """You are a travel-writing assistant. You are given a finalized,
day-by-day itinerary — already ordered and timed by a routing solver — plus
the traveler's preferences, as JSON.

Write a warm, second-person narrative describing the trip, day by day, and
return it as JSON: {"narrative": "<the narrative prose>"}

Rules:
- The "narrative" value must be flowing English prose — sentences and
  paragraphs that a traveler would enjoy reading — never a restatement of the
  input data, a list, or a table.
- Address the traveler directly ("you'll start the morning at...", "your
  afternoon continues at...").
- Mention every stop by its exact name, in the order given.
- State the arrival/departure times exactly as given — never invent or adjust
  them.
- You are describing a plan that is already final: do not reorder stops,
  suggest swaps, or propose a different route.
- Return ONLY the JSON object {"narrative": "..."} — no extra keys, no code
  fences, no commentary outside the prose itself."""


def writer(state: Plan) -> dict:
    t0 = time.monotonic()
    prefs = state.preferences

    user = json.dumps({
        "destination": prefs.destination,
        "pace": prefs.pace,
        "days": [
            {"day": day.day,
             "stops": [{"name": s.name, "arrival": s.arrival, "depart": s.depart}
                       for s in day.stops]}
            for day in state.days
        ],
    })
    raw = llm.complete_json(_SYSTEM, user)

    # The real LLM is forced into JSON-object mode, so it wraps its prose as
    # {"narrative": "..."}; FakeLLM in tests hands back plain prose directly.
    # Unwrap when it's the former, fall back to the raw text for the latter.
    try:
        parsed = json.loads(raw).get("narrative")
    except (json.JSONDecodeError, AttributeError):
        parsed = None
    narrative = parsed if isinstance(parsed, str) and parsed.strip() else raw
    narrative = narrative.strip()

    ms = int((time.monotonic() - t0) * 1000)
    log_entry = {"agent": "writer", "status": "done",
                 "summary": f"wrote narrative for {len(state.days)} day(s)",
                 "ms": ms}
    return {
        "narrative": narrative,
        "meta": {"agent_log": [log_entry]},
    }
