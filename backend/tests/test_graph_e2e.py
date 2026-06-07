"""End-to-end: the compiled graph with fakes. Asserts the whole pipeline yields
a valid Plan, AND that the clarification branch actually halts the graph."""
from backend.graph import build_graph
from backend.schemas import Plan
from conftest import wire_fake_graph


def test_happy_path_produces_valid_plan(monkeypatch, fake_ors):
    # Wire fakes into every node's module-level client, then run the graph.
    fake_ors.search_pois = lambda *a, **k: [
        {"id": "p1", "name": "Fushimi Inari", "lat": 34.9671, "lng": 135.7727,
         "category": "temple", "cost_band": "free"},
        {"id": "p2", "name": "Nishiki Market", "lat": 35.0050, "lng": 135.7649,
         "category": "food", "cost_band": "low"},
        {"id": "p4", "name": "Kinkaku-ji", "lat": 35.0394, "lng": 135.7292,
         "category": "temple", "cost_band": "low"},
    ]
    wire_fake_graph(
        monkeypatch, fake_ors=fake_ors,
        preferences_response=(
            '{"destination":"Kyoto, Japan","trip_length_days":2,"party_size":2,'
            '"pace":"relaxed","interests":["food","temples"],"budget_total":400,'
            '"currency":"EUR","must_sees":["Fushimi Inari"],"dietary":[],'
            '"clarification_needed":null}'),
        researcher_responses=['{"ranked_ids":["p1","p2","p4"]}'],
        writer_responses=["Day 1: start at Fushimi Inari, then Nishiki Market for "
                          "lunch. Day 2: explore Kinkaku-ji."],
    )
    graph = build_graph()
    result = graph.invoke(Plan(request="2 relaxed days in Kyoto, food + temples, 400 eur"))
    final = Plan.model_validate(result)
    assert final.narrative                       # writer ran
    assert final.days and all(d.stops for d in final.days)
    assert len(final.meta.agent_log) == 5        # all five nodes logged


def test_clarification_branch_halts_before_researcher(monkeypatch):
    # Wire every node anyway (belt-and-braces): if a regression ever routes
    # past `preferences` on this branch, the unconfigured FakeLLMs raise
    # immediately instead of silently reaching out to the real network.
    wire_fake_graph(
        monkeypatch,
        preferences_response=(
            '{"destination":null,"trip_length_days":3,"party_size":1,'
            '"pace":"moderate","interests":["food"],"budget_total":500,'
            '"currency":"EUR","must_sees":[],"dietary":[],'
            '"clarification_needed":"Which city are you visiting?"}'),
    )
    graph = build_graph()
    result = graph.invoke(Plan(request="some days somewhere, I like food"))
    final = Plan.model_validate(result)
    assert final.preferences.clarification_needed is not None
    assert not final.candidates                  # researcher never ran
    assert len(final.meta.agent_log) == 1        # only preferences logged
