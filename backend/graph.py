from langgraph.graph import StateGraph, START, END

from backend.schemas import Plan


def build_graph():
    graph = StateGraph(Plan)
    graph.add_edge(START, END)
    return graph.compile()
