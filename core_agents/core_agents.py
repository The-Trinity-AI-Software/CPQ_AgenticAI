import pandas as pd
import time
from utils.normalize import normalize_column_mapping
from prompts.agent_prompts import ORCHESTRATION_PROMPT, DISCOVERY_AGENT_PROMPT
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fuzzywuzzy import fuzz, process
from logic.logger_setup import setup_logger

logger = setup_logger()

def show_handshake(agent_name, message):
    print(f"HANDSHAKE::{agent_name}::{message}")

def orchestrator_agent(state):
    show_handshake("Orchestrator Agent", "Initiated and determining task type...")
    if "itam" in state["user_input"].lower():
        state["task"] = "itam_reload"
    elif "certificate" in state["user_input"].lower():
        state["task"] = "certificate_renewal"
    elif "workstation" in state["user_input"].lower():
        state["task"] = "add_new_workstation"
    else:
        state["task"] = "unknown"

    show_handshake("Orchestrator Agent", f"Determined task → {state['task']}")
    return state

def discovery_agent(state):
    show_handshake("Discovery Agent", "Initiated and loading file for discovery...")
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

    show_handshake("Discovery Agent", f"Identified {len(matched_df)} matched rows.")
    state["matched_df"] = matched_df
    return state

def validation_agent(state):
    show_handshake("Validation Agent", "Initiated and validating results...")
    df = state.get("result_df", pd.DataFrame())
    if df.empty or df.isnull().values.any():
        show_handshake("Validation Agent", "Validation completed with warnings (empty or nulls found).")
    else:
        show_handshake("Validation Agent", "Validation completed successfully with no issues.")
    return state
