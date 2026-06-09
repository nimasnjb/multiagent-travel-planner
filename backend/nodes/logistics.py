"""Logistics node. ORS travel-time matrix + OR-Tools TSP-with-time-windows.
ZERO LLM — the solver decides order and times, never a model.

OR-Tools routing API verified against the current docs/examples at
https://developers.google.com/optimization/routing (RoutingIndexManager /
RoutingModel / AddDimension / time-window dimensions), since several
pre-v1-style snippets floating around are stale.
"""
import time

from ortools.constraint_solver import pywrapcp, routing_enums_pb2

from backend.ors import ors
from backend.schemas import Day, Leg, Plan, Stop

# No real opening-hours data is available (ORS carries none), so every venue
# gets the same generic "open during the day" window and a flat dwell time.
# The solver still has real work to do: pick the order that minimizes total
# travel time while keeping the whole day inside these bounds.
_WORKDAY_START_MIN = 9 * 60   # 09:00
_WORKDAY_END_MIN = 21 * 60    # 21:00
_DWELL_MINUTES = 60


def _format_minutes(total_minutes: float) -> str:
    total = int(round(total_minutes))
    return f"{total // 60:02d}:{total % 60:02d}"


def _solve_day_order(matrix: list[list[float]]) -> tuple[list[int], list[float]]:
    """Solve the open-path TSP-with-time-windows for one day's stops.

    Returns (order, arrival_minutes): `order` is a permutation of
    range(len(matrix)) — the visiting sequence — and `arrival_minutes[k]` is
    the cumulative arrival time (minutes from midnight) at stop `order[k]`.
    """
    n = len(matrix)
    size = n + 1  # + dummy depot at index 0

    # Open-path trick: a route normally has to return to its depot. Real trips
    # don't loop back to the first venue, so we add a dummy depot with zero
    # travel cost to/from every real stop — the solver then "starts" and
    # "ends" there for free, and the path between is the optimal open order.
    extended = [[0.0] * size for _ in range(size)]
    for i in range(n):
        for j in range(n):
            extended[i + 1][j + 1] = matrix[i][j]

    manager = pywrapcp.RoutingIndexManager(size, 1, 0)
    routing = pywrapcp.RoutingModel(manager)

    def time_callback(from_index: int, to_index: int) -> int:
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        dwell = _DWELL_MINUTES if from_node != 0 else 0
        return int(round(extended[from_node][to_node] + dwell))

    transit_index = routing.RegisterTransitCallback(time_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_index)

    routing.AddDimension(
        transit_index,
        _WORKDAY_END_MIN,   # slack: allow waiting for a window to open
        _WORKDAY_END_MIN,   # max cumulative time per vehicle (one day)
        False,              # don't force the cumulative clock to start at 0
        "Time",
    )
    time_dimension = routing.GetDimensionOrDie("Time")
    for node in range(size):
        index = manager.NodeToIndex(node)
        lo = 0 if node == 0 else _WORKDAY_START_MIN
        time_dimension.CumulVar(index).SetRange(lo, _WORKDAY_END_MIN)

    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC

    solution = routing.SolveWithParameters(params)
    if solution is None:
        raise RuntimeError("OR-Tools could not find a route for this day")

    order: list[int] = []
    arrivals: list[float] = []
    index = routing.Start(0)
    while not routing.IsEnd(index):
        node = manager.IndexToNode(index)
        if node != 0:
            order.append(node - 1)
            arrivals.append(solution.Value(time_dimension.CumulVar(index)))
        index = solution.Value(routing.NextVar(index))
    return order, arrivals


def _order_day(day: Day, matrix: list[list[float]]) -> Day:
    order, arrivals = _solve_day_order(matrix)
    stops = day.stops

    ordered: list[Stop] = []
    for position, stop_idx in enumerate(order):
        arrival_min = arrivals[position]
        depart_min = min(arrival_min + _DWELL_MINUTES, _WORKDAY_END_MIN)
        leg = None
        if position < len(order) - 1:
            next_idx = order[position + 1]
            from_stop, to_stop = stops[stop_idx], stops[next_idx]
            try:
                geometry = ors.directions((from_stop.lat, from_stop.lng),
                                           (to_stop.lat, to_stop.lng))
            except Exception:
                geometry = None
            leg = Leg(minutes=matrix[stop_idx][next_idx], geometry=geometry or None)
        ordered.append(stops[stop_idx].model_copy(update={
            "arrival": _format_minutes(arrival_min),
            "depart": _format_minutes(depart_min),
            "leg_to_next": leg,
        }))
    return Day(day=day.day, stops=ordered)


def logistics(state: Plan) -> dict:
    t0 = time.monotonic()

    new_days = []
    for day in state.days:
        coords = [(stop.lat, stop.lng) for stop in day.stops]
        matrix = ors.matrix(coords)
        new_days.append(_order_day(day, matrix))

    ms = int((time.monotonic() - t0) * 1000)
    log_entry = {"agent": "logistics", "status": "done",
                 "summary": f"solved stop order and timing for {len(new_days)} day(s)",
                 "ms": ms}
    return {
        "days": new_days,
        "meta": {"agent_log": [log_entry]},
    }
