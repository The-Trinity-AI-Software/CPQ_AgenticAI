# application_logic.py placeholder


# Rebuilding application_logic.py to include run_cpq_pipeline and run_agent_with_prompt

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core_agents.core_agents import (orchestrator_agent, discovery_agent, validation_agent)
from agents.task_agents import (
    itam_reload_agent,
    certificate_renewal_agent,
    workstation_agent
    )

from prompts.agent_prompts import (
    ITAM_RELOAD_PROMPT,
    CERTIFICATE_RENEWAL_PROMPT,
    ADD_WORKSTATION_PROMPT,
    ORCHESTRATION_PROMPT,
    DISCOVERY_AGENT_PROMPT
)

from llm_strategies.langgraph_CPQ import run_langgraph_cpq
from llm_strategies.crewai_CPQ import run_crewai_cpq
from llm_strategies.autogen_CPQ import run_autogen_cpq
#from llm_strategies.langgraph_CPQ import run_langgraph_cpq

from logic.logger_setup import setup_logger
logger = setup_logger()

import pandas as pd
import logging
#from llm_strategies.langgraph_CPQ import build_langgraph_pipeline
#from llm_strategies.crewai_CPQ import build_crewai_pipeline
#from llm_strategies.autogen_CPQ import build_autogen_pipeline





logger = logging.getLogger("CPQLogger")

def run_cpq_pipeline(user_query, filepath, strategy):
    logger.info("CPQ pipeline started with strategy: %s | File: %s", strategy, filepath)

    try:
        # Run respective pipeline based on selected strategy
        if strategy == "langgraph":
            state = run_langgraph_cpq(user_query=user_query, filepath=filepath)
        elif strategy == "crewai":
            state = run_crewai_cpq(user_query=user_query, filepath=filepath)
        elif strategy == "autogen":
            state = run_autogen_cpq(user_query=user_query, filepath=filepath)
        else:
            logger.error("Unknown strategy provided: %s", strategy)
            return None

        if not state:
            logger.warning("Pipeline returned None or empty state.")
            return None

        logger.info("Pipeline executed successfully for strategy: %s", strategy)
        logger.debug("Final state before return: %s", state)

        return {
            "task": state.get("task", ""),
            "matched_df": state.get("matched_df", pd.DataFrame()),
            "result_df": state.get("result_df", pd.DataFrame())
        }

    except Exception as e:
        logger.error("Pipeline failed with error: %s", str(e))
        return None


def run_agent_with_prompt(agent_key: str, state: dict):
    def log_prompt(agent_name: str):
        PROMPTS = {
            "itam_reload": ITAM_RELOAD_PROMPT,
            "certificate_renewal": CERTIFICATE_RENEWAL_PROMPT,
            "add_new_workstation": ADD_WORKSTATION_PROMPT,
            "orchestrator": ORCHESTRATION_PROMPT,
            "discovery": DISCOVERY_AGENT_PROMPT,
            "validation": "The Validation Agent ensures that the final results are consistent, complete, and ready for reporting."
        }
        if agent_name in PROMPTS:
            print(f"--- Prompt: {agent_name} ---\\n{PROMPTS[agent_name]}\\n")

    log_prompt(agent_key)
    
    if agent_key == "orchestrator":
        return orchestrator_agent(state)
    elif agent_key == "discovery":
        return discovery_agent(state)
    elif agent_key == "itam_reload":
        return itam_reload_agent(state)
    elif agent_key == "certificate_renewal":
        return certificate_renewal_agent(state)
    elif agent_key == "add_new_workstation":
        return workstation_agent(state)
    elif agent_key == "firewall_replacement":
        return firewall_replacement_agent(state)
    elif agent_key == "validation":
        return validation_agent(state)
    else:
        raise ValueError(f"Unknown agent: {agent_key}")


# Overwrite the logic/application_logic.py with full pipeline and prompt logic
#app_logic_path = os.path.join(base_dir, "logic", "application_logic.py")
#with open(app_logic_path, "w", encoding="utf-8") as f:
#    f.write(final_application_logic)

#app_logic_path
