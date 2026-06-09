"""Shared fixtures. The key idea: unit tests must NOT hit real OpenAI or ORS.

We inject fakes so tests are deterministic, free, and fast. The real clients
live behind llm.py and ors.py; tests pass fakes with the same interface.
"""
import pytest
from backend.schemas import Plan, Preferences, Candidate


@pytest.fixture
def base_preferences() -> Preferences:
    return Preferences(
        destination="Kyoto, Japan",
        trip_length_days=2,
        party_size=2,
        pace="relaxed",
        interests=["food", "temples"],
        budget_total=400,
        currency="EUR",
        must_sees=["Fushimi Inari"],
        dietary=[],
        clarification_needed=None,
    )


@pytest.fixture
def candidate_pool() -> list[Candidate]:
    # A realistic researcher output: more candidates than fit the budget,
    # including the must-see, so budget/logistics have something to chew on.
    return [
        Candidate(id="p1", name="Fushimi Inari", lat=34.9671, lng=135.7727,
                  category="temple", cost_band="free"),
        Candidate(id="p2", name="Nishiki Market", lat=35.0050, lng=135.7649,
                  category="food", cost_band="low"),
        Candidate(id="p3", name="Kikunoi", lat=35.0036, lng=135.7818,
                  category="food", cost_band="high"),
        Candidate(id="p4", name="Kinkaku-ji", lat=35.0394, lng=135.7292,
                  category="temple", cost_band="low"),
        Candidate(id="p5", name="Gion district", lat=35.0037, lng=135.7752,
                  category="neighborhood", cost_band="free"),
    ]


class FakeLLM:
    """Returns canned JSON per call. Each test configures .responses."""
    def __init__(self, responses: list[str]):
        self._responses = list(responses)
    def complete_json(self, system: str, user: str) -> str:
        return self._responses.pop(0)


class FakeORS:
    """Deterministic geo data. Matrix is symmetric minutes between points."""
    def search_pois(self, query, near, max_results=10):
        return []  # tests that need candidates inject them directly
    def matrix(self, coords):
        n = len(coords)
        return [[0 if i == j else 10 + abs(i - j) * 5
                 for j in range(n)] for i in range(n)]
    def directions(self, start, end):
        # A simple multi-point road-following path: start, midpoint, end,
        # in ORS's [lng, lat] order.
        (s_lat, s_lng), (e_lat, e_lng) = start, end
        mid = [(s_lng + e_lng) / 2, (s_lat + e_lat) / 2]
        return [[s_lng, s_lat], mid, [e_lng, e_lat]]


@pytest.fixture
def fake_ors() -> FakeORS:
    return FakeORS()


def wire_fake_graph(monkeypatch, *, preferences_response: str,
                    researcher_responses: list[str] = (),
                    budget_responses: list[str] = (),
                    writer_responses: list[str] = (),
                    fake_ors: FakeORS | None = None) -> FakeORS:
    """Monkeypatch every node's module-level llm/ors singleton with fakes, so
    a full graph.invoke() never touches the network — for graph-level (e2e)
    tests that exercise more than one node per run.

    Each `*_responses` list feeds that node's FakeLLM in call order; leave a
    node's list empty when the scenario never reaches it (e.g. the
    clarification branch never runs past `preferences`, so its FakeLLM is
    simply never asked to pop a response).

    Returns the FakeORS in use, so callers can further tailor `search_pois`
    for their scenario before invoking the graph.
    """
    import backend.nodes.budget as budget_mod
    import backend.nodes.logistics as logistics_mod
    import backend.nodes.preferences as preferences_mod
    import backend.nodes.researcher as researcher_mod
    import backend.nodes.writer as writer_mod

    fake_ors = fake_ors or FakeORS()
    monkeypatch.setattr(preferences_mod, "llm", FakeLLM([preferences_response]))
    monkeypatch.setattr(researcher_mod, "llm", FakeLLM(list(researcher_responses)))
    monkeypatch.setattr(researcher_mod, "ors", fake_ors)
    monkeypatch.setattr(budget_mod, "llm", FakeLLM(list(budget_responses)))
    monkeypatch.setattr(logistics_mod, "ors", fake_ors)
    monkeypatch.setattr(writer_mod, "llm", FakeLLM(list(writer_responses)))
    return fake_ors
