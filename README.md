# Multi-Agent Travel Planner

Describe a trip in plain language and a five-agent LangGraph pipeline turns it into a day-by-day itinerary with a real, walkable route on the map.

**[Live demo](https://nimasnjb.github.io/multiagent-travel-planner/)** · [API](https://multiagent-travel-planner-backend.onrender.com)

> The API runs on Render's free tier and spins down when idle — the first request after a while can take 30–60s to wake up.

![Demo: a Kyoto trip request animating through the agent pipeline, drawing a route on the map, and producing a narrative itinerary](docs/demo.gif)

*(Drop the recorded gif at `docs/demo.gif` — Kyoto request → agent arc animating → map drawing street routes → narrative text panel.)*

## Architecture

A request flows through a `StateGraph` of five agents, each one a pure function over a shared `Plan` state object:

```
START
  -> preferences --[clarification needed?]--> END (ask user)
                  \-> researcher -> budget -> logistics -> writer -> END
```

| Agent | Responsibility |
|---|---|
| **preferences** | Parses the free-text request into structured trip preferences (destination, length, budget, interests). If anything essential is missing or ambiguous, it sets `clarification_needed` and the graph short-circuits to `END` so the API can ask a follow-up question. |
| **researcher** | Queries OpenRouteService's POI endpoint for real venues near the destination matching the user's interests. |
| **budget** | Selects which candidates fit within the stated budget. |
| **logistics** | Solves stop ordering and timing with OR-Tools (TSP with time windows), using ORS's travel-time matrix and directions for real route geometry. |
| **writer** | Turns the finalized day-by-day plan into a narrative itinerary. |

### The core design principle

**The LLM does language and judgment — never the facts.** It parses intent and writes prose, but:

- It never invents places — every venue comes from OpenRouteService's real POI data.
- It never decides visit order — OR-Tools solves the routing as a constrained optimization problem.
- It never edits times — arrival/departure times are computed from the routing solution, not generated text.

This separation is the whole point: an LLM is fluent but unreliable at facts and arithmetic, while a solver and a places API are reliable but can't write a paragraph. Each agent does only the part it's good at, and the `Plan` schema is validated at every step so a malformed handoff fails loudly instead of silently corrupting the itinerary.

## Tech stack

**Backend** — Python, FastAPI + uvicorn, LangGraph (agent pipeline), OpenAI (`gpt-4o-mini`, language/judgment only), OpenRouteService (places, travel-time matrix, directions), OR-Tools (routing/TSP solver), deployed on Render.

**Frontend** — React + Vite, react-router (HashRouter), Leaflet + react-leaflet (map), react-markdown (narrative rendering), deployed on GitHub Pages.

## Project structure

```
multiagent-travel-planner/
  backend/
    main.py          # FastAPI app: /plan, /health
    graph.py          # LangGraph StateGraph wiring
    schemas.py        # Plan — the data contract, validated at every node
    nodes/            # preferences, researcher, budget, logistics, writer
    llm.py            # OpenAI client wrapper
    ors.py            # OpenRouteService client wrapper
    tests/
  frontend/
    src/
      pages/          # Home, How it works, About
      ...              # TripForm, AgentGraph, ItineraryMap, ItineraryText
  render.yaml          # Render Blueprint (backend deploy)
  .github/workflows/   # GitHub Pages deploy (frontend)
```

## Running locally

**Backend**
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env   # fill in OPENAI_API_KEY and ORS_API_KEY
uvicorn backend.main:app --reload --port 8000   # run from repo root
```

**Frontend**
```bash
cd frontend
npm install
npm run dev   # defaults to http://127.0.0.1:8000 for the API
```
