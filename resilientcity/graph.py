from langgraph.graph import END, StateGraph
from .agents import (
    planner_agent, evidence_agent, risk_agent, decision_agent,
    critic_agent, revision_agent, safety_agent, reporter_agent,
)
from .state import ResilientCityState

def critic_route(state: ResilientCityState) -> str:
    return "revise" if state["critic"]["status"] == "REVISE" else "safety"

def build_graph():
    graph = StateGraph(ResilientCityState)
    graph.add_node("planner", planner_agent)
    graph.add_node("evidence", evidence_agent)
    graph.add_node("risk", risk_agent)
    graph.add_node("decision", decision_agent)
    graph.add_node("critic", critic_agent)
    graph.add_node("revision", revision_agent)
    graph.add_node("safety", safety_agent)
    graph.add_node("reporter", reporter_agent)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "evidence")
    graph.add_edge("evidence", "risk")
    graph.add_edge("risk", "decision")
    graph.add_edge("decision", "critic")
    graph.add_conditional_edges("critic", critic_route, {"revise": "revision", "safety": "safety"})
    graph.add_edge("revision", "evidence")
    graph.add_edge("safety", "reporter")
    graph.add_edge("reporter", END)
    return graph.compile()
