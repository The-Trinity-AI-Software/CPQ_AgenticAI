# autogen_CPQ.py placeholder


import sys
import os
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core_agents.core_agents import orchestrator_agent, discovery_agent, validation_agent
from agents.task_agents import (
    itam_reload_agent, workstation_agent, certificate_renewal_agent
)
import logging

logger = logging.getLogger("CPQLogger")

def run_autogen_cpq(user_query: str, filepath: str):
    logger.info("Starting AutoGen CPQ pipeline...")
    
    state = {
        "task": "",
        "filepath": filepath,
        "user_input": user_query
    }

    try:
        # Step 1: Orchestrator
        state = orchestrator_agent(state)
        logger.info("Orchestrator determined task: %s", state.get("task"))

        if not state.get("task"):
            logger.error("No task was detected by the orchestrator.")
            return None

        # Step 2: Discovery
        state = discovery_agent(state)
        logger.info("Discovery agent matched %d rows.", len(state.get("matched_df", [])))

        # Step 3: Task Agent Execution
        agent_map = {
            "itam_reload": itam_reload_agent,
            "add_new_workstation": workstation_agent,
            "certificate_renewal": certificate_renewal_agent
        }

        task_key = state["task"]
        agent_func = agent_map.get(task_key)

        if not agent_func:
            logger.error("No agent function found for task: %s", task_key)
            return None

        state = agent_func(state)
        logger.info("Task agent (%s) executed successfully.", task_key)

        # Step 4: Validation Agent
        state = validation_agent(state)
        logger.info("Validation agent completed successfully.")

        return {
            "task": state.get("task", ""),
            "matched_df": state.get("matched_df", pd.DataFrame()),
            "result_df": state.get("result_df", pd.DataFrame())
        }

    except Exception as e:
        logger.exception("AutoGen pipeline failed with exception: %s", str(e))
        return None
