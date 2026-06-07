"""Property-based eval cases for the preferences node (a fuzzy LLM-only parser).

Exact-output assertions don't make sense for an LLM parse step — instead each
case states a PROPERTY the parsed Preferences must satisfy, and we check that
property against the real model. Run directly:

    python -m backend.evals.preferences_cases

Requires OPENAI_API_KEY in the environment (this calls the real LLM, unlike
tests/test_preferences.py which injects a FakeLLM).
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Callable

from backend.nodes.preferences import preferences
from backend.schemas import Plan, Preferences
from dotenv import load_dotenv

load_dotenv()  # loads .env from the current working directory

_NIGHTLIFE_TERMS = ("nightlife", "bar", "club", "nightclub", "pub")


def _no_destination_asks_for_clarification(prefs: Preferences) -> bool:
    return prefs.clarification_needed is not None


def _no_trip_length_asks_for_clarification(prefs: Preferences) -> bool:
    return prefs.clarification_needed is not None


def _kids_down_weight_nightlife(prefs: Preferences) -> bool:
    return not any(term in interest.lower() for interest in prefs.interests for term in _NIGHTLIFE_TERMS)


def _complete_request_captures_destination_and_must_see(prefs: Preferences) -> bool:
    return (
        prefs.clarification_needed is None
        and prefs.destination is not None
        and "lisbon" in prefs.destination.lower()
        and any("bel" in must_see.lower() for must_see in prefs.must_sees)
    )


def _captures_dietary_restrictions(prefs: Preferences) -> bool:
    joined = " ".join(prefs.dietary).lower()
    return "vegetarian" in joined and "gluten" in joined


def _captures_local_currency(prefs: Preferences) -> bool:
    return prefs.clarification_needed is None and prefs.currency.upper() == "JPY"


@dataclass
class EvalCase:
    name: str
    request: str
    property: str
    check: Callable[[Preferences], bool]


CASES: list[EvalCase] = [
    EvalCase(
        name="vague_no_destination",
        request="I want to plan a fun trip somewhere relaxing for about a week.",
        property="no destination -> clarification_needed set",
        check=_no_destination_asks_for_clarification,
    ),
    EvalCase(
        name="missing_trip_length",
        request="We want to visit Paris sometime — we love art museums and pastries.",
        property="no trip length -> clarification_needed set",
        check=_no_trip_length_asks_for_clarification,
    ),
    EvalCase(
        name="family_with_young_kids",
        request="Planning a 5-day trip to Orlando with our two young kids (ages 4 and 7); "
                "we love theme parks and kid-friendly restaurants.",
        property="mentions kids -> nightlife down-weighted out of interests",
        check=_kids_down_weight_nightlife,
    ),
    EvalCase(
        name="complete_request_with_must_see",
        request="5 days in Lisbon for 2 adults, moderate pace, love seafood and street art, "
                "budget 1200 EUR, must see Belem Tower.",
        property="fully-specified request -> no clarification; destination and must_see captured",
        check=_complete_request_captures_destination_and_must_see,
    ),
    EvalCase(
        name="dietary_restrictions_captured",
        request="We're vegetarian and gluten-free, planning 4 days in Barcelona, "
                "a food-focused trip for 2 people.",
        property="mentions dietary needs -> dietary list captures them",
        check=_captures_dietary_restrictions,
    ),
    EvalCase(
        name="currency_inferred_from_local_context",
        request="Planning 3 days in Tokyo for two of us, budget around 80000 yen, "
                "we love anime and ramen.",
        property="local-currency phrasing -> currency parsed as JPY",
        check=_captures_local_currency,
    ),
]


def run() -> None:
    if "OPENAI_API_KEY" not in os.environ:
        raise SystemExit("OPENAI_API_KEY is not set — this eval calls the real LLM.")

    passed = 0
    for case in CASES:
        print(f"--- {case.name}: {case.property}")
        print(f"    request: {case.request}")
        try:
            out = preferences(Plan(request=case.request))
        except Exception as exc:
            print(f"[FAIL] {case.name}: node raised {exc!r} instead of returning a Preferences")
            continue
        prefs = out["preferences"]
        ok = case.check(prefs)
        passed += int(ok)
        print(f"[{'PASS' if ok else 'FAIL'}] {case.name}")
        print(f"    parsed:  {prefs.model_dump()}")

    print(f"\n{passed}/{len(CASES)} passed")


if __name__ == "__main__":
    run()
