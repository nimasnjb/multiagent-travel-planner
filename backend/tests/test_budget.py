"""Budget node. Pure contract properties, fully deterministic, no LLM needed
for the happy path. These are the assertions the spec promises in prose."""
from backend.nodes.budget import budget
from backend.schemas import Plan


def test_respects_budget_ceiling(base_preferences, candidate_pool):
    out = budget(Plan(request="x", preferences=base_preferences,
                      candidates=candidate_pool))
    total = sum(s.est_cost for d in out["days"] for s in d.stops)
    assert total <= base_preferences.budget_total


def test_must_sees_always_kept(base_preferences, candidate_pool):
    out = budget(Plan(request="x", preferences=base_preferences,
                      candidates=candidate_pool))
    names = {s.name for d in out["days"] for s in d.stops}
    for must in base_preferences.must_sees:
        assert must in names      # must-see survives even when budget is tight


def test_days_match_trip_length(base_preferences, candidate_pool):
    out = budget(Plan(request="x", preferences=base_preferences,
                      candidates=candidate_pool))
    assert len(out["days"]) == base_preferences.trip_length_days
