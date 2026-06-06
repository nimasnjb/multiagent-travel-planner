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


@pytest.fixture
def fake_ors() -> FakeORS:
    return FakeORS()
