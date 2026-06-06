from __future__ import annotations

import operator
from typing import Annotated, Optional

from pydantic import BaseModel, Field


class Preferences(BaseModel):
    destination: Optional[str] = None
    trip_length_days: int = 1
    party_size: int = 1
    pace: str = ""
    interests: list[str] = Field(default_factory=list)
    budget_total: float = 0.0
    currency: str = "USD"
    must_sees: list[str] = Field(default_factory=list)
    dietary: list[str] = Field(default_factory=list)
    clarification_needed: Optional[str] = None


class Candidate(BaseModel):
    id: str
    name: str
    lat: float
    lng: float
    category: str
    cost_band: str


class Leg(BaseModel):
    minutes: float


class Stop(BaseModel):
    id: str
    name: str
    lat: float
    lng: float
    arrival: Optional[str] = None
    depart: Optional[str] = None
    est_cost: float = 0.0
    leg_to_next: Optional[Leg] = None


class Day(BaseModel):
    day: int
    stops: list[Stop] = Field(default_factory=list)


class Meta(BaseModel):
    agent_log: Annotated[list[dict], operator.add] = Field(default_factory=list)


class Plan(BaseModel):
    request: str = ""
    preferences: Optional[Preferences] = None
    candidates: list[Candidate] = Field(default_factory=list)
    days: list[Day] = Field(default_factory=list)
    narrative: Optional[str] = None
    meta: Meta = Field(default_factory=Meta)
