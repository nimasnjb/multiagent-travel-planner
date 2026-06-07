from langgraph.graph import StateGraph, START, END

from backend.nodes.budget import budget
from backend.nodes.logistics import logistics
from backend.nodes.preferences import preferences
from backend.nodes.researcher import researcher
from backend.nodes.writer import writer
from backend.schemas import Plan


def _route_after_preferences(state: Plan) -> str:
    """The clarification branch: halt at END if preferences couldn't be
    parsed, otherwise continue on to research the destination."""
    if state.preferences and state.preferences.clarification_needed:
        return "clarify"
    return "continue"


def build_graph():
    graph = StateGraph(Plan)

    graph.add_node("preferences", preferences)
    graph.add_node("researcher", researcher)
    graph.add_node("budget", budget)
    graph.add_node("logistics", logistics)
    graph.add_node("writer", writer)

    graph.add_edge(START, "preferences")
    graph.add_conditional_edges(
        "preferences",
        _route_after_preferences,
        {"clarify": END, "continue": "researcher"},
    )
    graph.add_edge("researcher", "budget")
    graph.add_edge("budget", "logistics")
    graph.add_edge("logistics", "writer")
    graph.add_edge("writer", END)

    return graph.compile()
