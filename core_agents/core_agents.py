# core_agents.py placeholder

# Full logic for orchestration_agent, discovery_agent, validation_agent for core_agents.py

import pandas as pd
import time
from utils.normalize import normalize_column_mapping
from prompts.agent_prompts import ORCHESTRATION_PROMPT, DISCOVERY_AGENT_PROMPT

from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from logic.logger_setup import setup_logger
logger = setup_logger()

def show_handshake(agent_name, message):
    logger.info(f"{agent_name}: {message}")




def orchestrator_agent(state):
    logger.info("Orchestrator triggered for user query: %s", state["user_input"])
    
    if "itam" in state["user_input"].lower():
        state["task"] = "itam_reload"
    elif "certificate" in state["user_input"].lower():
        state["task"] = "certificate_renewal"
    elif "workstation" in state["user_input"].lower():
        state["task"] = "add_new_workstation"
    else:
        state["task"] = "unknown"
        logger.warning("Unknown task detected: %s", state["user_input"])
        logger.debug("Received task: %s", state.get("task"))
        logger.debug("Matched DF shape: %s", state.get("matched_df", pd.DataFrame()).shape)

    
    return state

def discovery_agent(state):
    show_handshake("Discovery Agent", DISCOVERY_AGENT_PROMPT.strip())
    df = pd.read_excel(state["filepath"])
    col_map = normalize_column_mapping(df)
    query = state["user_input"].lower()
    matched_df = df.copy()
    matched = False
    for key in col_map.values():
        if key in matched_df.columns:
            best_match = process.extractOne(query, matched_df[key].astype(str), scorer=fuzz.partial_ratio)
            if best_match and best_match[1] > 80:
                matched_df = matched_df[matched_df[key].astype(str).str.contains(best_match[0], case=False)]
                matched = True
                break
    if not matched:
        matched_df = pd.DataFrame(columns=df.columns)
    state["matched_df"] = matched_df
    return state

def validation_agent(state):
    logger.info("Validation Agent: Verifying result integrity...")
    df = state.get("result_df", pd.DataFrame())
    if df.empty or df.isnull().values.any():
        logger.warning("Validation Agent: Missing or empty values detected.")
    else:
        logger.info("Validation Agent: All values verified successfully.")
    return state



