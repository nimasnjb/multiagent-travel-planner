import json
import time

from backend.llm import llm
from backend.schemas import Plan, Preferences

_SYSTEM = """You are a travel-planning assistant. Parse the user's trip request into JSON.
Return ONLY a JSON object with these fields:
  destination (string or null),
  trip_length_days (int),
  party_size (int),
  pace (string: "relaxed"|"moderate"|"packed"),
  interests (list of strings),
  budget_total (number),
  currency (string, ISO code),
  must_sees (list of strings),
  dietary (list of strings),
  clarification_needed (string or null)

Rules:
- If destination is missing or unclear, set destination to null and set clarification_needed to the question you need answered.
- If trip length is missing, set clarification_needed.
- Never guess a destination; ask instead."""


def preferences(state: Plan) -> dict:
    t0 = time.monotonic()
    raw = llm.complete_json(_SYSTEM, state.request)
    data = json.loads(raw)
    prefs = Preferences(**data)
    ms = int((time.monotonic() - t0) * 1000)
    log_entry = {"agent": "preferences", "status": "done",
                 "summary": f"parsed preferences for {prefs.destination}", "ms": ms}
    return {
        "preferences": prefs,
        "meta": {"agent_log": [log_entry]},
    }
