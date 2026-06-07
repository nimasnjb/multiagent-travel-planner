import json
import time

from backend.llm import llm
from backend.schemas import Candidate, Day, Plan, Stop

# Rough per-stop cost estimates by ORS cost_band. Code-led: the LLM never sets
# prices, it only helps choose which optional stops to keep when the pool is
# too expensive to fit whole.
_COST_BAND_ESTIMATES = {"free": 0.0, "low": 20.0, "medium": 50.0, "high": 120.0}

_SYSTEM = """You are a travel-budget assistant. The candidate venues cost more
in total than the trip budget allows, so some optional (non-must-see) venues
have to be dropped. You are given the traveler's preferences and the optional
venues that remain to be decided on (each with id, name, category, and an
estimated cost).

Decide which venues are worth splurging on and which to save money by skipping.
Order the venue ids from most-worth-keeping to least-worth-keeping.

Return ONLY a JSON object: {"priority_ids": [<id>, ...]}

Rules:
- priority_ids may contain ONLY ids that appear in the venue list given to you.
- Never invent an id — you are prioritizing real venues, not generating new ones.
- Favor venues that match the traveler's interests; prefer a couple of
  memorable splurges over many low-value stops when money is tight."""


def _est_cost(candidate: Candidate) -> float:
    return _COST_BAND_ESTIMATES.get(candidate.cost_band, 30.0)


def _prioritize_with_llm(prefs, optional: list[Candidate]) -> list[Candidate]:
    by_id = {c.id: c for c in optional}
    user = json.dumps({
        "destination": prefs.destination,
        "interests": prefs.interests,
        "budget_total": prefs.budget_total,
        "currency": prefs.currency,
        "venues": [{"id": c.id, "name": c.name, "category": c.category,
                    "est_cost": _est_cost(c)} for c in optional],
    })
    raw = llm.complete_json(_SYSTEM, user)
    priority_ids = json.loads(raw).get("priority_ids", [])

    # Anti-hallucination guarantee: only honor ids that were actually offered.
    ordered = [by_id[pid] for pid in priority_ids if pid in by_id]
    seen = {c.id for c in ordered}
    ordered += [c for c in optional if c.id not in seen]
    return ordered


def _split_into_days(stops: list[Stop], n_days: int) -> list[Day]:
    days = [Day(day=i + 1) for i in range(n_days)]
    if not days:
        return days
    for idx, stop in enumerate(stops):
        days[idx % len(days)].stops.append(stop)
    return days


def budget(state: Plan) -> dict:
    t0 = time.monotonic()
    prefs = state.preferences
    candidates = state.candidates

    # Must-sees are kept unconditionally — they survive even when money is
    # tight. Everything else is "optional" and subject to the budget greedy.
    must_see_names = set(prefs.must_sees)
    must_sees = [c for c in candidates if c.name in must_see_names]
    optional = [c for c in candidates if c.name not in must_see_names]

    selected = list(must_sees)
    spent = sum(_est_cost(c) for c in selected)

    pool_total = spent + sum(_est_cost(c) for c in optional)
    if pool_total > prefs.budget_total:
        order = _prioritize_with_llm(prefs, optional)
    else:
        order = optional

    for candidate in order:
        cost = _est_cost(candidate)
        if spent + cost <= prefs.budget_total:
            selected.append(candidate)
            spent += cost

    stops = [Stop(id=c.id, name=c.name, lat=c.lat, lng=c.lng, est_cost=_est_cost(c))
             for c in selected]
    days = _split_into_days(stops, prefs.trip_length_days)

    ms = int((time.monotonic() - t0) * 1000)
    log_entry = {"agent": "budget", "status": "done",
                 "summary": f"selected {len(stops)} stops totalling "
                            f"{spent:g} {prefs.currency} (budget {prefs.budget_total:g})",
                 "ms": ms}
    return {
        "days": days,
        "meta": {"agent_log": [log_entry]},
    }
