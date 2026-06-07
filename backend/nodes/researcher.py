import json
import time

from backend.llm import llm
from backend.ors import ors
from backend.schemas import Candidate, Plan

_SYSTEM = """You are a travel-research assistant. You are given a list of real
venues (each with id, name, category) and the traveler's preferences. Select
and rank the venues that best fit the trip.

Return ONLY a JSON object: {"ranked_ids": [<id>, ...]}, most relevant first.

Rules:
- ranked_ids may contain ONLY ids that appear in the venue list given to you.
- Never invent an id — you are ranking real venues, not generating new ones.
- Favor venues that match the traveler's interests and must-sees."""


def researcher(state: Plan) -> dict:
    t0 = time.monotonic()
    prefs = state.preferences

    queries = prefs.interests or ["things to do"]
    venues_by_id: dict[str, dict] = {}
    for query in queries:
        for venue in ors.search_pois(query, near=prefs.destination):
            venues_by_id[venue["id"]] = venue

    user = json.dumps({
        "destination": prefs.destination,
        "interests": prefs.interests,
        "must_sees": prefs.must_sees,
        "venues": [{"id": v["id"], "name": v["name"], "category": v["category"]}
                   for v in venues_by_id.values()],
    })
    raw = llm.complete_json(_SYSTEM, user)
    ranked_ids = json.loads(raw).get("ranked_ids", [])

    # Anti-hallucination guarantee: the LLM may only rank/filter venues ORS
    # actually returned. Drop any id it invented before it becomes a Candidate.
    candidates = [Candidate(**venues_by_id[vid]) for vid in ranked_ids if vid in venues_by_id]

    ms = int((time.monotonic() - t0) * 1000)
    log_entry = {"agent": "researcher", "status": "done",
                 "summary": f"found {len(candidates)} candidates for {prefs.destination}",
                 "ms": ms}
    return {
        "candidates": candidates,
        "meta": {"agent_log": [log_entry]},
    }
