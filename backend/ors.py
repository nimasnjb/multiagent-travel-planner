"""Single OpenRouteService client wrapper — the only place that talks to ORS.

Real venues come from the public POI endpoint (POST /pois); travel times come
from the Matrix endpoint. Tests inject a FakeORS with the same two methods
(see tests/conftest.py) so nodes never hit the network in unit tests.

POI endpoint shape verified against:
  https://giscience.github.io/openrouteservice/api-reference/endpoints/poi/
  https://github.com/GIScience/openpoiservice
  https://github.com/GIScience/openrouteservice-py (places.py / geocode.py / client.py)
"""
from __future__ import annotations

import os

import requests

_BASE_URL = "https://api.openrouteservice.org"
_WALKING_PROFILE = "foot-walking"
_SEARCH_RADIUS_METERS = 2000  # ORS caps geometry.buffer at 2000m

# ORS POI category GROUP ids (from the openpoiservice category table). The
# endpoint filters by these fixed numeric ids, not free text, so a user's
# free-text interest ("food", "temples", ...) has to be mapped to the closest
# group. Keyword -> group id; first substring match wins, "tourism" (620) is
# the sensible default for anything that doesn't match a more specific group.
_CATEGORY_GROUPS_BY_KEYWORD: dict[str, int] = {
    "food": 560, "drink": 560, "restaurant": 560, "cafe": 560, "coffee": 560,
    "bar": 560, "pub": 560, "nightlife": 560, "dining": 560, "cuisine": 560,
    "museum": 130, "art": 130, "culture": 130, "theatre": 130, "gallery": 130,
    "history": 220, "historic": 220, "heritage": 220, "temple": 220, "shrine": 220,
    "castle": 220, "ruins": 220,
    "shop": 420, "shopping": 420, "market": 420, "boutique": 420,
    "nature": 330, "park": 330, "garden": 330, "hike": 330, "hiking": 330, "outdoor": 330,
    "entertainment": 260, "leisure": 260, "fun": 260, "amusement": 260,
    "sight": 620, "landmark": 620, "tour": 620, "attraction": 620, "monument": 620,
}
_DEFAULT_CATEGORY_GROUP_ID = 620  # tourism


def _category_group_id(interest: str) -> int:
    lowered = interest.lower()
    for keyword, group_id in _CATEGORY_GROUPS_BY_KEYWORD.items():
        if keyword in lowered:
            return group_id
    return _DEFAULT_CATEGORY_GROUP_ID


class _ORS:
    def __init__(self) -> None:
        self._api_key: str | None = None

    def _key(self) -> str:
        if self._api_key is None:
            self._api_key = os.environ["ORS_API_KEY"]
        return self._api_key

    def _headers(self) -> dict:
        return {"Authorization": self._key()}

    def _geocode(self, place: str) -> tuple[float, float]:
        """Resolve a place name to (lat, lng) via ORS's Pelias-backed /geocode/search."""
        resp = requests.get(
            f"{_BASE_URL}/geocode/search",
            params={"text": place, "size": 1},
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        features = resp.json()["features"]
        if not features:
            raise ValueError(f"ORS could not geocode {place!r}")
        lng, lat = features[0]["geometry"]["coordinates"]
        return lat, lng

    def search_pois(self, query: str, near: str, max_results: int = 10) -> list[dict]:
        """Real venues matching `query` near the place `near`, via ORS's
        public POI endpoint (POST /pois, request type "pois").

        `query` is a free-text interest like "food" or "temples"; the
        endpoint filters by fixed numeric category-group ids rather than
        free text, so we map it to the closest group (see
        _CATEGORY_GROUPS_BY_KEYWORD) and search a buffered point around the
        geocoded destination.

        Returns plain dicts shaped like Candidate (id, name, lat, lng,
        category, cost_band). ORS carries no pricing data, so cost_band is
        honestly reported as "unknown" — never invented.
        """
        lat, lng = self._geocode(near)
        resp = requests.post(
            f"{_BASE_URL}/pois",
            json={
                "request": "pois",
                "geometry": {
                    "geojson": {"type": "Point", "coordinates": [lng, lat]},
                    "buffer": _SEARCH_RADIUS_METERS,
                },
                "filters": {"category_group_ids": [_category_group_id(query)]},
                "limit": max_results,
            },
            headers=self._headers(),
            timeout=15,
        )
        resp.raise_for_status()
        venues = []
        for feature in resp.json()["features"]:
            props = feature["properties"]
            venue_lng, venue_lat = feature["geometry"]["coordinates"]
            name = (props.get("osm_tags") or {}).get("name") or f"Unnamed {query} spot"
            venues.append({
                "id": f"osm-{props['osm_type']}-{props['osm_id']}",
                "name": name,
                "lat": venue_lat,
                "lng": venue_lng,
                "category": query,
                "cost_band": "unknown",
            })
        return venues

    def matrix(self, coords: list[tuple[float, float]]) -> list[list[float]]:
        """N x N travel-time matrix in minutes between (lat, lng) coords."""
        resp = requests.post(
            f"{_BASE_URL}/v2/matrix/{_WALKING_PROFILE}",
            json={
                "locations": [[lng, lat] for lat, lng in coords],
                "metrics": ["duration"],
            },
            headers=self._headers(),
            timeout=15,
        )
        resp.raise_for_status()
        durations = resp.json()["durations"]
        return [[seconds / 60 for seconds in row] for row in durations]


ors = _ORS()


if __name__ == "__main__":
    import sys

    from dotenv import load_dotenv

    sys.stdout.reconfigure(encoding="utf-8")  # venue names may be non-ASCII (e.g. Japanese)
    load_dotenv()
    if "ORS_API_KEY" not in os.environ:
        raise SystemExit("ORS_API_KEY is not set — this smoke test calls the real ORS API.")

    venues = ors.search_pois("food", near="Kyoto, Japan", max_results=5)
    print(f"Kyoto, food -> {len(venues)} venue(s):")
    for v in venues:
        print(f"  {v['id']:<24} {v['name']:<35} ({v['lat']:.4f}, {v['lng']:.4f})  category={v['category']!r}  cost_band={v['cost_band']!r}")

    # Matrix smoke test: feed 4 real Kyoto landmarks through the real ORS
    # matrix endpoint and the real OR-Tools TSPTW solve (logistics node uses
    # this module's `ors` singleton, so it hits the network here too).
    from backend.nodes.logistics import logistics
    from backend.schemas import Day, Plan, Stop

    kyoto_day = Day(day=1, stops=[
        Stop(id="p1", name="Fushimi Inari Taisha", lat=34.9671, lng=135.7727),
        Stop(id="p4", name="Kinkaku-ji", lat=35.0394, lng=135.7292),
        Stop(id="p2", name="Nishiki Market", lat=35.0050, lng=135.7649),
        Stop(id="p5", name="Gion District", lat=35.0037, lng=135.7752),
    ])
    out = logistics(Plan(request="smoke test", days=[kyoto_day]))
    print("\nKyoto day-1 route (ORS matrix + OR-Tools TSP-with-time-windows):")
    for stop in out["days"][0].stops:
        leg = f"{stop.leg_to_next.minutes:5.1f} min -> next" if stop.leg_to_next else "        (end of day)"
        print(f"  {stop.arrival}–{stop.depart}  {stop.name:<22} {leg}")
