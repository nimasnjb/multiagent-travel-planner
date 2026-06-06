"""Researcher node. Contract: it may only return venues ORS actually returned —
never invented ones. This is the anti-hallucination guarantee, tested directly."""
from backend.nodes.researcher import researcher
from backend.schemas import Plan
from conftest import FakeLLM


def test_only_returns_ors_venues(monkeypatch, base_preferences, fake_ors):
    ors_venues = [{"id": "p1", "name": "Nishiki Market", "lat": 35.0, "lng": 135.7,
                   "category": "food", "cost_band": "low"}]
    fake_ors.search_pois = lambda *a, **k: ors_venues
    # LLM ranks by returning ids; if it hallucinated "p99" the node must drop it.
    fake = FakeLLM(['{"ranked_ids":["p1","p99"]}'])
    monkeypatch.setattr("backend.nodes.researcher.llm", fake)
    monkeypatch.setattr("backend.nodes.researcher.ors", fake_ors)
    out = researcher(Plan(request="x", preferences=base_preferences))
    ids = {c.id for c in out["candidates"]}
    assert ids <= {"p1"}            # p99 was invented -> must not appear
    assert "p99" not in ids
