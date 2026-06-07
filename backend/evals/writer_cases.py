"""Property-based eval cases for the writer node (fuzzy LLM prose).

Exact-string assertions don't make sense for narrative prose — instead each
case runs a finalized itinerary through the writer and checks PROPERTIES the
unit test (test_writer.py) can't reach: voice, completeness, anti-
hallucination, and overall coherence. Run directly:

    python -m backend.evals.writer_cases

Requires OPENAI_API_KEY in the environment (this calls the real LLM, unlike
tests/test_writer.py which injects a FakeLLM).
"""
from __future__ import annotations

import json
import os
import re
import unicodedata
from dataclasses import dataclass
from typing import Callable

from dotenv import load_dotenv

from backend.llm import llm
from backend.nodes.writer import writer
from backend.schemas import Day, Plan, Preferences, Stop

load_dotenv()  # loads .env from the current working directory

_SECOND_PERSON_RE = re.compile(r"\byou(?:'re|'ll|'d|r|rs)?\b", re.IGNORECASE)


def _stop(id_: str, name: str, lat: float, lng: float,
          arrival: str, depart: str, cost: float = 0.0) -> Stop:
    return Stop(id=id_, name=name, lat=lat, lng=lng,
                arrival=arrival, depart=depart, est_cost=cost)


def _stop_names(plan: Plan) -> list[str]:
    return [stop.name for day in plan.days for stop in day.stops]


def _fold(text: str) -> str:
    """Lowercase and strip diacritics, e.g. 'Família' -> 'familia'. The model
    sometimes renders accents slightly differently than the source data
    ('Sagrada Familia' vs 'Sagrada Família') without actually omitting the
    venue — an exact substring check would wrongly flag that as missing."""
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(c for c in decomposed if not unicodedata.combining(c)).lower()


# ---- Heuristic properties — cheap, deterministic, no LLM call needed -------

def _is_second_person(plan: Plan, narrative: str) -> bool:
    return bool(_SECOND_PERSON_RE.search(narrative))


def _mentions_every_stop(plan: Plan, narrative: str) -> bool:
    folded = _fold(narrative)
    return all(_fold(name) in folded for name in _stop_names(plan))


# ---- LLM-judged properties — no string heuristic can reliably catch these --

_JUDGE_SYSTEM = """You are an exacting fact-checker reviewing a travel
narrative against the itinerary it claims to describe. Answer ONLY the
question asked, as strict JSON: {"answer": true|false, "reason": <short str>}"""


def _ask_judge(question: str, context: dict) -> tuple[bool, str]:
    raw = llm.complete_json(_JUDGE_SYSTEM, json.dumps({"question": question, **context}))
    data = json.loads(raw)
    return bool(data.get("answer")), str(data.get("reason", "")).strip()


def _invents_no_extra_places(plan: Plan, narrative: str) -> bool:
    invented, reason = _ask_judge(
        "Does the narrative name any specific venue, restaurant, landmark, or "
        "shop that does NOT appear in known_stops? Mentioning the destination "
        "city/neighborhood by name, or vague descriptions like 'a nearby cafe', "
        "does not count as inventing a place — only a distinct named venue does.",
        {"known_stops": _stop_names(plan), "narrative": narrative},
    )
    print(f"        judge: {reason}")
    return not invented


def _reads_as_coherent_day_by_day_prose(plan: Plan, narrative: str) -> bool:
    coherent, reason = _ask_judge(
        "Is the narrative coherent, flowing prose that walks through the trip "
        "day by day — one distinguishable, ordered section per day — rather "
        "than a disjointed list of facts or a jumbled retelling?",
        {"day_count": len(plan.days), "narrative": narrative},
    )
    print(f"        judge: {reason}")
    return coherent


@dataclass
class Property:
    name: str
    description: str
    check: Callable[[Plan, str], bool]


PROPERTIES: list[Property] = [
    Property("second_person", "addresses the traveler directly ('you', 'your')",
             _is_second_person),
    Property("mentions_every_stop", "every stop in the plan is named in the narrative",
             _mentions_every_stop),
    Property("invents_no_extra_places", "no venue appears that isn't in the plan",
             _invents_no_extra_places),
    Property("coherent_day_by_day_prose", "reads as flowing prose, ordered by day",
             _reads_as_coherent_day_by_day_prose),
]


@dataclass
class EvalCase:
    name: str
    plan: Plan


CASES: list[EvalCase] = [
    EvalCase(
        name="kyoto_relaxed_food_and_temples",
        plan=Plan(
            request="2 relaxed days in Kyoto for 2, food and temples, "
                    "must see Fushimi Inari, budget 400 EUR",
            preferences=Preferences(
                destination="Kyoto, Japan", trip_length_days=2, party_size=2,
                pace="relaxed", interests=["food", "temples"], budget_total=400,
                currency="EUR", must_sees=["Fushimi Inari Taisha"], dietary=[]),
            days=[
                Day(day=1, stops=[
                    _stop("p1", "Fushimi Inari Taisha", 34.9671, 135.7727, "09:00", "10:30"),
                    _stop("p2", "Nishiki Market", 35.0050, 135.7649, "11:15", "12:45", 15),
                ]),
                Day(day=2, stops=[
                    _stop("p4", "Kinkaku-ji", 35.0394, 135.7292, "09:30", "11:00"),
                    _stop("p5", "Gion District", 35.0037, 135.7752, "15:00", "17:00"),
                ]),
            ],
        ),
    ),
    EvalCase(
        name="rome_packed_history_day",
        plan=Plan(
            request="1 packed day in Rome for 2 history lovers, must see the Colosseum",
            preferences=Preferences(
                destination="Rome, Italy", trip_length_days=1, party_size=2,
                pace="packed", interests=["history", "architecture"], budget_total=250,
                currency="EUR", must_sees=["Colosseum"], dietary=[]),
            days=[
                Day(day=1, stops=[
                    _stop("r1", "Colosseum", 41.8902, 12.4922, "08:30", "10:00", 25),
                    _stop("r2", "Roman Forum", 41.8925, 12.4853, "10:15", "11:45", 18),
                    _stop("r3", "Trevi Fountain", 41.9009, 12.4833, "13:00", "13:45"),
                    _stop("r4", "Pantheon", 41.8986, 12.4769, "14:15", "15:15"),
                ]),
            ],
        ),
    ),
    EvalCase(
        name="orlando_family_with_kids",
        plan=Plan(
            request="3 days in Orlando with two young kids, theme parks and "
                    "kid-friendly food, must see Magic Kingdom",
            preferences=Preferences(
                destination="Orlando, USA", trip_length_days=3, party_size=4,
                pace="moderate", interests=["theme parks", "family dining"],
                budget_total=1500, currency="USD", must_sees=["Magic Kingdom"], dietary=[]),
            days=[
                Day(day=1, stops=[
                    _stop("o1", "Magic Kingdom", 28.4177, -81.5812, "09:00", "17:00", 180),
                ]),
                Day(day=2, stops=[
                    _stop("o2", "Universal Studios", 28.4743, -81.4677, "09:00", "16:30", 170),
                    _stop("o3", "Hard Rock Cafe Orlando", 28.4744, -81.4679, "18:00", "19:30", 60),
                ]),
                Day(day=3, stops=[
                    _stop("o4", "Gatorland", 28.3850, -81.3970, "10:00", "12:30", 70),
                    _stop("o5", "Lake Eola Park", 28.5447, -81.3712, "15:00", "16:30"),
                ]),
            ],
        ),
    ),
    EvalCase(
        name="barcelona_food_weekend",
        plan=Plan(
            request="2-day food weekend in Barcelona for a vegetarian couple, "
                    "must see La Boqueria",
            preferences=Preferences(
                destination="Barcelona, Spain", trip_length_days=2, party_size=2,
                pace="relaxed", interests=["food", "markets"], budget_total=350,
                currency="EUR", must_sees=["La Boqueria"], dietary=["vegetarian"]),
            days=[
                Day(day=1, stops=[
                    _stop("b1", "La Boqueria", 41.3818, 2.1716, "10:00", "11:30", 20),
                    _stop("b2", "Park Güell", 41.4145, 2.1527, "13:00", "15:00", 10),
                ]),
                Day(day=2, stops=[
                    _stop("b3", "Sagrada Família", 41.4036, 2.1744, "09:30", "11:00", 30),
                    _stop("b4", "Gothic Quarter", 41.3833, 2.1767, "12:00", "14:30", 25),
                ]),
            ],
        ),
    ),
    EvalCase(
        name="lisbon_solo_five_days",
        plan=Plan(
            request="5 days solo in Lisbon, moderate pace, love viewpoints and "
                    "pastries, must see Belem Tower",
            preferences=Preferences(
                destination="Lisbon, Portugal", trip_length_days=5, party_size=1,
                pace="moderate", interests=["viewpoints", "pastries", "history"],
                budget_total=900, currency="EUR", must_sees=["Belem Tower"], dietary=[]),
            days=[
                Day(day=1, stops=[_stop("l1", "Belem Tower", 38.6916, -9.2160, "09:30", "11:00", 6)]),
                Day(day=2, stops=[
                    _stop("l2", "Jerónimos Monastery", 38.6979, -9.2068, "09:30", "11:30", 10),
                    _stop("l3", "Pastéis de Belém", 38.6975, -9.2033, "11:45", "12:30", 8),
                ]),
                Day(day=3, stops=[_stop("l4", "Miradouro da Senhora do Monte", 38.7203, -9.1303, "17:00", "18:30")]),
                Day(day=4, stops=[_stop("l5", "Alfama District", 38.7122, -9.1306, "10:00", "13:00", 15)]),
                Day(day=5, stops=[_stop("l6", "LX Factory", 38.7037, -9.1781, "11:00", "13:30", 20)]),
            ],
        ),
    ),
]


def run() -> None:
    import sys
    sys.stdout.reconfigure(encoding="utf-8")  # narratives may include accented place names

    if "OPENAI_API_KEY" not in os.environ:
        raise SystemExit("OPENAI_API_KEY is not set — this eval calls the real LLM.")

    total = passed = 0
    for case in CASES:
        prefs = case.plan.preferences
        print(f"\n=== {case.name} — {prefs.trip_length_days}-day {prefs.destination} "
              f"({prefs.pace} pace, party of {prefs.party_size}) ===")
        try:
            narrative = writer(case.plan)["narrative"]
        except Exception as exc:
            print(f"[FAIL] {case.name}: writer raised {exc!r}")
            total += len(PROPERTIES)
            continue
        print(f"narrative:\n{narrative}\n")

        for prop in PROPERTIES:
            total += 1
            try:
                ok = prop.check(case.plan, narrative)
            except Exception as exc:
                print(f"    [FAIL] {prop.name} ({prop.description}): check raised {exc!r}")
                continue
            passed += int(ok)
            print(f"    [{'PASS' if ok else 'FAIL'}] {prop.name} — {prop.description}")

    print(f"\n{passed}/{total} property checks passed")


if __name__ == "__main__":
    run()
