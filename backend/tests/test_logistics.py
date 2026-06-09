"""Logistics node. The OR-Tools solve — ZERO LLM. Highest-risk piece, so the
tightest tests. Build/verify this against these before touching real ORS."""
from backend.nodes.logistics import logistics
from backend.schemas import Leg, Plan, Day, Stop


def _day_with_stops():
    stops = [
        Stop(id="p1", name="A", lat=34.96, lng=135.77),
        Stop(id="p2", name="B", lat=35.00, lng=135.76),
        Stop(id="p3", name="C", lat=35.03, lng=135.72),
    ]
    return [Day(day=1, stops=stops)]


def test_all_stops_preserved(base_preferences, fake_ors, monkeypatch):
    monkeypatch.setattr("backend.nodes.logistics.ors", fake_ors)
    p = Plan(request="x", preferences=base_preferences, days=_day_with_stops())
    out = logistics(p)
    assert len(out["days"][0].stops) == 3      # solver reorders, never drops


def test_times_are_monotonic(base_preferences, fake_ors, monkeypatch):
    monkeypatch.setattr("backend.nodes.logistics.ors", fake_ors)
    p = Plan(request="x", preferences=base_preferences, days=_day_with_stops())
    out = logistics(p)
    times = [s.arrival for s in out["days"][0].stops]
    assert times == sorted(times)              # no time travel within a day


def test_legs_present_between_consecutive_stops(base_preferences, fake_ors, monkeypatch):
    monkeypatch.setattr("backend.nodes.logistics.ors", fake_ors)
    p = Plan(request="x", preferences=base_preferences, days=_day_with_stops())
    out = logistics(p)
    stops = out["days"][0].stops
    for s in stops[:-1]:
        assert s.leg_to_next is not None and s.leg_to_next.minutes >= 0


def test_leg_geometry_is_optional_and_validates():
    assert Leg(minutes=5.0).geometry is None
    leg = Leg(minutes=5.0, geometry=[[135.77, 34.96], [135.76, 35.00]])
    assert leg.geometry == [[135.77, 34.96], [135.76, 35.00]]
