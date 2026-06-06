"""Writer node. Fuzzy prose, so property assertions only. The crucial contract:
it presents, it does not re-plan. We verify it changed nothing structural."""
from backend.nodes.writer import writer
from backend.schemas import Plan, Day, Stop
from conftest import FakeLLM


def _planned():
    stops = [Stop(id="p1", name="Fushimi Inari", lat=34.96, lng=135.77,
                  arrival="09:00", depart="10:30", est_cost=0),
             Stop(id="p2", name="Nishiki Market", lat=35.0, lng=135.76,
                  arrival="11:00", depart="12:00", est_cost=15)]
    return [Day(day=1, stops=stops)]


def test_narrative_mentions_every_stop(monkeypatch, base_preferences):
    fake = FakeLLM(["Day 1: start at Fushimi Inari, then Nishiki Market for lunch."])
    monkeypatch.setattr("backend.nodes.writer.llm", fake)
    p = Plan(request="x", preferences=base_preferences, days=_planned())
    out = writer(p)
    for stop in p.days[0].stops:
        assert stop.name in out["narrative"]


def test_writer_does_not_mutate_plan(monkeypatch, base_preferences):
    fake = FakeLLM(["Day 1: Fushimi Inari then Nishiki Market."])
    monkeypatch.setattr("backend.nodes.writer.llm", fake)
    p = Plan(request="x", preferences=base_preferences, days=_planned())
    before = [(s.name, s.arrival) for s in p.days[0].stops]
    writer(p)
    after = [(s.name, s.arrival) for s in p.days[0].stops]
    assert before == after            # order + times untouched
