from __future__ import annotations

from typing import Annotated, Optional, Union

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
    agent_log: list[dict] = Field(default_factory=list)


def _append_agent_log(current: Meta, update: Union[Meta, dict]) -> Meta:
    """Reducer for Plan.meta. LangGraph's channel system only reads Annotated
    reducers on the state model's OWN fields — an annotation nested one level
    down on Meta.agent_log is invisible to it, so each node's partial update
    would otherwise replace the whole `meta` (last-write-wins) and clobber the
    entries logged by the nodes that ran before it. This merges instead, so
    every node's one log entry survives — see SPEC.md's agent_log rule."""
    if isinstance(update, dict):
        update = Meta.model_validate(update)
    return Meta(agent_log=current.agent_log + update.agent_log)


class Plan(BaseModel):
    request: str = ""
    preferences: Optional[Preferences] = None
    candidates: list[Candidate] = Field(default_factory=list)
    days: list[Day] = Field(default_factory=list)
    narrative: Optional[str] = None
    meta: Annotated[Meta, _append_agent_log] = Field(default_factory=Meta)
