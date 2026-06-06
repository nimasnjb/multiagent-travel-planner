"""End-to-end: the compiled graph with fakes. Asserts the whole pipeline yields
a valid Plan, AND that the clarification branch actually halts the graph."""
from backend.graph import build_graph
from backend.schemas import Plan


def test_happy_path_produces_valid_plan(monkeypatch, fake_ors):
    # Wire fakes into every node's module-level client, then run the graph.
    # (Helper assumed in conftest or graph test utils; see SPEC definition of done.)
    graph = build_graph()
    result = graph.invoke(Plan(request="2 relaxed days in Kyoto, food + temples, 400 eur"))
    final = Plan.model_validate(result)
    assert final.narrative                       # writer ran
    assert final.days and all(d.stops for d in final.days)
    assert len(final.meta.agent_log) == 5        # all five nodes logged


def test_clarification_branch_halts_before_researcher(monkeypatch):
    graph = build_graph()
    result = graph.invoke(Plan(request="some days somewhere, I like food"))
    final = Plan.model_validate(result)
    assert final.preferences.clarification_needed is not None
    assert not final.candidates                  # researcher never ran
    assert len(final.meta.agent_log) == 1        # only preferences logged
