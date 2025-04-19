# crewai_CPQ.py placeholder



import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from crewai import Crew, Agent, Task
from core_agents.core_agents import orchestrator_agent, discovery_agent, validation_agent
from agents.task_agents import (
    itam_reload_agent, workstation_agent, certificate_renewal_agent
)

import pandas as pd


def run_crewai_cpq(user_query: str, filepath: str):
    state = {
        "task": "",
        "filepath": filepath,
        "user_input": user_query
    }

    state = orchestrator_agent(state)
    if not state.get("task"):
        return None

    state = discovery_agent(state)

    task_map = {
        "itam_reload": itam_reload_agent,
        "certificate_renewal": certificate_renewal_agent,
        "add_new_workstation": workstation_agent,
    }

    agent_func = task_map.get(state["task"])
    if not agent_func:
        return None

    state = agent_func(state)
    state = validation_agent(state)

    return {
        "task": state.get("task", ""),
        "matched_df": state.get("matched_df", pd.DataFrame()),
        "result_df": state.get("result_df", pd.DataFrame())
    }

