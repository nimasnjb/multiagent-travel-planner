"""Preferences node. Fuzzy parsing, so we assert PROPERTIES not exact output.
Exact-string assertions on LLM output are brittle and wrong here."""
from backend.nodes.preferences import preferences
from backend.schemas import Plan
from conftest import FakeLLM


def test_complete_request_routes_forward(monkeypatch):
    fake = FakeLLM(['{"destination":"Kyoto, Japan","trip_length_days":2,'
                    '"party_size":2,"pace":"relaxed","interests":["food"],'
                    '"budget_total":400,"currency":"EUR","must_sees":[],'
                    '"dietary":[],"clarification_needed":null}'])
    monkeypatch.setattr("backend.nodes.preferences.llm", fake)
    out = preferences(Plan(request="2 relaxed days in Kyoto, love food, 400 eur"))
    assert out["preferences"].clarification_needed is None
    assert out["preferences"].destination


def test_missing_destination_sets_clarification(monkeypatch):
    # The contract: a request with no destination must NOT be guessed —
    # it must populate clarification_needed so the conditional edge halts.
    fake = FakeLLM(['{"destination":null,"trip_length_days":3,"party_size":1,'
                    '"pace":"moderate","interests":["food"],"budget_total":500,'
                    '"currency":"EUR","must_sees":[],"dietary":[],'
                    '"clarification_needed":"Which city are you visiting?"}'])
    monkeypatch.setattr("backend.nodes.preferences.llm", fake)
    out = preferences(Plan(request="3 days somewhere nice, I like food"))
    assert out["preferences"].clarification_needed is not None


def test_appends_one_agent_log_entry(monkeypatch):
    fake = FakeLLM(['{"destination":"Rome","trip_length_days":1,"party_size":2,'
                    '"pace":"packed","interests":["history"],"budget_total":200,'
                    '"currency":"EUR","must_sees":[],"dietary":[],'
                    '"clarification_needed":null}'])
    monkeypatch.setattr("backend.nodes.preferences.llm", fake)
    out = preferences(Plan(request="one packed day in Rome"))
    log = out["meta"]["agent_log"] if isinstance(out["meta"], dict) else out["meta"].agent_log
    assert len(log) == 1 and log[0]["agent"] == "preferences"
