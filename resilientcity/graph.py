from langgraph.graph import END, StateGraph
from .agents import (planner_agent,evidence_agent,llm_evidence_agent,risk_agent,decision_agent,
                     critic_agent,llm_critic_agent,revision_agent,safety_agent,reporter_agent)
from .state import ResilientCityState

def critic_route(state):
    return "revise" if state["critic"]["status"]=="REVISE" else "safety"

def build_graph():
    g=StateGraph(ResilientCityState)
    for name,node in [
        ("planner",planner_agent),("evidence",evidence_agent),("llm_evidence",llm_evidence_agent),
        ("risk",risk_agent),("decision",decision_agent),("critic",critic_agent),
        ("llm_critic",llm_critic_agent),("revision",revision_agent),
        ("safety",safety_agent),("reporter",reporter_agent)
    ]: g.add_node(name,node)
    g.set_entry_point("planner")
    g.add_edge("planner","evidence"); g.add_edge("evidence","llm_evidence")
    g.add_edge("llm_evidence","risk"); g.add_edge("risk","decision")
    g.add_edge("decision","critic"); g.add_edge("critic","llm_critic")
    g.add_conditional_edges("llm_critic",critic_route,{"revise":"revision","safety":"safety"})
    g.add_edge("revision","evidence"); g.add_edge("safety","reporter"); g.add_edge("reporter",END)
    return g.compile()
