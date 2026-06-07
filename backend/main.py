"""FastAPI app exposing the compiled graph over /plan, plus /health for
Render's health check."""
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.graph import build_graph
from backend.schemas import Plan

load_dotenv()  # populate OPENAI_API_KEY / ORS_API_KEY from .env before any node runs

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://nimasnjb.github.io", "http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_graph = build_graph()


class PlanRequest(BaseModel):
    request: str
    prior_state: Optional[Plan] = None


@app.post("/plan")
def plan(body: PlanRequest) -> Plan:
    state = body.prior_state or Plan()
    state.request = body.request
    result = _graph.invoke(state)
    return Plan.model_validate(result)


@app.get("/health")
def health() -> dict:
    return {"ok": True}
