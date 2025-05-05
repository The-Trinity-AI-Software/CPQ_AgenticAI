
import sys
import os

# Ensure the base directory is in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)


from langgraph.graph import StateGraph
from typing import TypedDict
import pandas as pd
from agents.task_agents import (itam_reload_agent, workstation_agent, certificate_renewal_agent)
from core_agents.core_agents import orchestrator_agent, discovery_agent, validation_agent

class CPQState(TypedDict):
    task: str
    filepath: str
    user_input: str
    matched_df: pd.DataFrame
    result_df: pd.DataFrame

def run_langgraph_cpq(user_query: str, filepath: str):
    builder = StateGraph(CPQState)
    builder.add_node("orchestrator", orchestrator_agent)
    builder.add_node("discovery", discovery_agent)
    builder.add_node("itam_reload", itam_reload_agent)
    builder.add_node("workstation", workstation_agent)
    builder.add_node("certificate_renewal", certificate_renewal_agent)
    #builder.add_node("firewall_replacement", firewall_replacement_agent)
    builder.add_node("validation", validation_agent)

    builder.set_entry_point("orchestrator")
    builder.add_edge("orchestrator", "discovery")
    builder.add_conditional_edges("discovery", lambda state: state["task"], {
        "itam_reload": "itam_reload",
        "add_new_workstation": "workstation",
        "certificate_renewal": "certificate_renewal",
        #"firewall_replacement": "firewall_replacement",
        "unknown": "validation"
    })
    builder.add_edge("itam_reload", "validation")
    builder.add_edge("workstation", "validation")
    builder.add_edge("certificate_renewal", "validation")
    #builder.add_edge("firewall_replacement", "validation")

    graph = builder.compile()
    final_state = graph.invoke({
        "task": "",
        "filepath": filepath,
        "user_input": user_query
    })
    return final_state

