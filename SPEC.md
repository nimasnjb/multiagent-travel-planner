# Multi-Agent Travel Planner — Project Spec (LangGraph v1)
here we go!

This file is the source of truth for ARCHITECTURE and RULES. It is read by the
AI coding assistant every session. It does NOT contain status tracking (that
lives in the human's PLAN.md) and it does NOT contain the tests themselves
(those live in `tests/` as runnable code). When this file conflicts with a
prior assumption, this file wins.

Two companion authorities, each owns one thing:
- `backend/schemas.py` owns the DATA SHAPES (the Pydantic models). This spec
  describes them in prose but `schemas.py` is the truth — never hand-maintain a
  duplicate JSON example that can drift.
- `backend/tests/` owns CORRECTNESS. "Done" means the relevant test is green,
  not that a human eyeballed the output. See "Definition of done" below.

## What we're building

A web app where a user describes a trip in plain language and a LangGraph
multi-agent graph produces: (1) a day-by-day itinerary as text, (2) a map with
the route drawn between stops, and (3) a live graph of the agents handing work
to each other. Portfolio/showcase project — favor clarity and a clean demo over
scale.

## Tech stack (do not substitute without updating this file)

- **Backend**: Python 3.11+, FastAPI, uvicorn.
- **Agent framework**: LangGraph v1.0+ (stable, Oct 2025). Pin the version in
  requirements.txt. Verify the current API against
  https://docs.langchain.com/oss/python/langgraph/graph-api before writing
  graph code — do not rely on training-memory patterns, several pre-v1 APIs
  are deprecated.
- **State**: a Pydantic model (`Plan` in schemas.py) used as the StateGraph
  state schema. Pydantic (not TypedDict) so every node's output is validated at
  the state boundary and malformed output fails loudly.
- **LLM**: OpenAI `gpt-4o-mini` via the `openai` SDK, behind one wrapper
  (`backend/llm.py`) so the model name lives in exactly one place.
- **Places + routing data**: OpenRouteService (one free HeiGIT key) for POI
  search, the travel-time matrix, and directions geometry. Wrapper in `ors.py`.
- **Routing solve**: Google OR-Tools for the TSP-with-time-windows. The LLM
  never decides visit order — code does.
- **Frontend**: React (Vite), Leaflet + react-leaflet, free OSM tiles.
- **Hosting**: backend on Render (free), frontend on GitHub Pages.
- **Repo**: monorepo, `backend/` and `frontend/` side by side.

## Repo layout

```
travel-planner/
  backend/
    main.py            # FastAPI app; exposes the compiled graph over /plan
    graph.py           # builds + compiles the StateGraph (nodes + edges)
    state.py           # the LangGraph state schema (wraps schemas.Plan)
    schemas.py         # Pydantic models — the DATA CONTRACT
    llm.py             # single OpenAI client wrapper
    ors.py             # single OpenRouteService client wrapper
    nodes/
      preferences.py
      researcher.py
      budget.py
      logistics.py
      writer.py
    tests/
      conftest.py      # fixtures: sample inputs, fake LLM/ORS for unit tests
      test_preferences.py
      test_researcher.py
      test_budget.py
      test_logistics.py
      test_writer.py
      test_graph_e2e.py
    evals/
      preferences_cases.py   # property-based eval cases for the fuzzy nodes
      writer_cases.py
    requirements.txt
    .env.example       # OPENAI_API_KEY= , ORS_API_KEY=
  frontend/ ...        # (frontend spec section below)
  README.md  .gitignore  LICENSE  render.yaml
```

## The graph

Five nodes plus a conditional edge. The graph IS the control flow — there is no
orchestrator function. Build it in `graph.py` with `StateGraph(Plan)`, add each
node, add edges, then `.compile()` (forgetting to compile is the #1 beginner
error — the graph raises at runtime).

Topology:

```
START
  -> preferences
      [conditional edge]:
          if state.preferences.clarification_needed is set -> END
            (the API returns the question to the user; a second /plan call
             with the appended answer re-enters the graph)
          else -> researcher
  -> researcher
  -> budget
  -> logistics
  -> writer
  -> END
```

The clarification conditional edge is the showcase piece — it's a real graph
branch, not decoration. Implement it with `add_conditional_edges` from the
preferences node, routing on whether `clarification_needed` is populated.

### Nodes (each is `def node(state: Plan) -> dict` returning a partial update)

1. **preferences** (`nodes/preferences.py`) — LLM only, no external data. Parses
   the free-text request into the `Preferences` model. If a critical field is
   missing (no destination, no dates/length), set `clarification_needed` to the
   question to ask and return — the conditional edge handles routing.

2. **researcher** (`nodes/researcher.py`) — ORS POI search + LLM ranking.
   Queries ORS for real venues matching interests, then the LLM filters/ranks
   ONLY the returned venues. Never invents venues. Writes `candidates`.

3. **budget** (`nodes/budget.py`) — code-led greedy allocation to fit
   `budget_total`; LLM only for splurge-vs-save judgment when tight. Writes the
   selected stops grouped into `days` (still unordered within each day).

4. **logistics** (`nodes/logistics.py`) — ORS matrix + OR-Tools. Per day: get
   the travel-time matrix, solve TSP-with-time-windows for optimal order and
   arrival/departure times. ZERO LLM involvement. Writes ordered stops + legs.

5. **writer** (`nodes/writer.py`) — LLM for prose only. Writes `narrative` from
   the ordered plan. Must not reorder stops or change times.

### State and reducers

State is the `Plan` Pydantic model. Most fields are last-write-wins (a node
fully owns its section). The exception is `meta.agent_log`: it must use an
APPEND reducer so each node adds its entry without clobbering prior ones.
Define this with `Annotated[list, operator.add]` (or a small custom reducer) on
the log field. Each node appends one entry on completion:
`{ "agent": <name>, "status": "done", "summary": <str>, "ms": <int> }`.
The frontend graph animation is driven entirely by this log.

## API surface

- `POST /plan` — body `{ "request": <text>, "prior_state": <optional Plan> }`.
  Invokes the compiled graph. Returns the final `Plan`. If the run ended at the
  clarification branch, the returned Plan has `clarification_needed` set and the
  frontend shows the question; the user's answer comes back in a follow-up call
  via `prior_state`.
- `GET /health` -> `{ "ok": true }` for Render's health check.
- CORS: allow the GitHub Pages origin and `http://localhost:5173`.

## Hard rules (prevent the classic failure modes)

- The LLM never invents places, never decides visit order, never edits times.
  Data is from ORS; ordering is from OR-Tools; the LLM does language + judgment.
- Every LLM call requests strict JSON, strips code fences, parses in try/except,
  retries once with a "valid JSON only" reminder before erroring.
- The graph MUST be compiled before use. State is validated by Pydantic on every
  node return — a node returning a malformed partial update should raise, not
  pass junk downstream.
- Keys only in env vars. `.env` is gitignored; `.env.example` documents names.
- Each node is importable and unit-testable in isolation with a fake LLM/ORS
  (see tests/conftest.py). The graph is testable end-to-end with fakes.

## Definition of done (this is the engineering discipline)

A node is NOT done when it runs — it is done when its test is green.

- Deterministic nodes (researcher wiring, budget, logistics) -> unit tests in
  `tests/` asserting contract properties (schema validity, budget ceiling
  respected, must-sees preserved, route order valid, times monotonic).
- Fuzzy nodes (preferences parsing, writer prose) -> cannot assert exact output.
  Instead, property evals in `evals/`: e.g. "vague request sets
  clarification_needed", "request mentioning kids down-weights nightlife",
  "writer narrative mentions every stop in the plan and reorders nothing".
- The graph -> an e2e test in `test_graph_e2e.py` that runs the compiled graph
  with fakes and asserts a valid final Plan, including one run that hits the
  clarification branch.

Workflow per node: write/maintain the test first -> implement until green -> for
fuzzy nodes also run the eval set -> commit. Do not mark a node done on a visual
check alone.

## Build order

1. Scaffold: schemas.py, state.py, llm.py, ors.py (stubs), main.py with /health,
   and an empty compiled graph (START -> END) that runs. Confirm it compiles.
2. Nodes in dependency order: preferences, researcher, budget, logistics,
   writer. Build logistics' OR-Tools solve FIRST against hardcoded coordinates
   (highest-risk piece) before adding the ORS matrix call. Test each before
   wiring into the graph.
3. Add the conditional clarification edge; run the e2e test including the
   clarification path.
4. Frontend (separate section), then deploy.

## Commit discipline

Initialize the repo before any code. Commit after each green node and each
component. Small, focused messages. Never batch the whole backend into one
commit.
