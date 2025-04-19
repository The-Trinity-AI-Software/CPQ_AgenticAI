# Re-run after kernel reset to recreate directory and populate import headers in each relevant file

import pandas as pd
import streamlit as st
import time

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.normalize import normalize_column_mapping
from prompts.agent_prompts import (
    ITAM_RELOAD_PROMPT,
    CERTIFICATE_RENEWAL_PROMPT,
    ADD_WORKSTATION_PROMPT
)

def show_handshake(agent_name, message):
    st.markdown(f"**{agent_name}**: {message}")
    time.sleep(0.6)

def calculate_total(result_df, formula):
    try:
        result_df['Total'] = formula(result_df)
        grand_total = result_df['Total'].sum()
        total_row = pd.DataFrame([{**{col: "" for col in result_df.columns if col != 'Total'}, "Total": grand_total}], index=[len(result_df)])
        return pd.concat([result_df, total_row])
    except Exception as e:
        st.error(f"Error calculating totals: {e}")
        return result_df

def itam_reload_agent(state):
    show_handshake("ITAM Reload Agent", ITAM_RELOAD_PROMPT.strip())
    matched_df = state["matched_df"]
    col_map = normalize_column_mapping(matched_df)
    result_df = matched_df.copy()
    result_df['quantity'] = pd.to_numeric(result_df.get(col_map.get('quantity'), 0), errors='coerce').fillna(0)
    result_df['price'] = pd.to_numeric(result_df.get(col_map.get('price'), 0.0), errors='coerce').fillna(0.0)
    state["result_df"] = calculate_total(result_df, lambda df: df['quantity'] * df['price'])
    return state

def certificate_renewal_agent(state):
    show_handshake("Certificate Renewal Agent", CERTIFICATE_RENEWAL_PROMPT.strip())
    matched_df = state["matched_df"]
    col_map = normalize_column_mapping(matched_df)
    result_df = matched_df.copy()
    result_df['quantity'] = pd.to_numeric(result_df.get(col_map.get('quantity'), 0), errors='coerce').fillna(0)
    result_df['laborprice'] = pd.to_numeric(result_df.get(col_map.get('laborprice'), 0.0), errors='coerce').fillna(0.0)
    result_df['certprice'] = pd.to_numeric(result_df.get(col_map.get('certprice'), 0.0), errors='coerce').fillna(0.0)
    state["result_df"] = calculate_total(result_df, lambda df: (df['laborprice'] * df['quantity']) + df['certprice'])
    return state

def workstation_agent(state):
    show_handshake("Workstation Agent", ADD_WORKSTATION_PROMPT.strip())
    matched_df = state["matched_df"]
    col_map = normalize_column_mapping(matched_df)
    result_df = matched_df.copy()
    result_df['quantity'] = pd.to_numeric(result_df.get(col_map.get('quantity'), 0), errors='coerce').fillna(0)
    result_df['price'] = pd.to_numeric(result_df.get(col_map.get('price'), 0.0), errors='coerce').fillna(0.0)
    state["result_df"] = calculate_total(result_df, lambda df: df['quantity'] * df['price'])
    return state

def firewall_replacement_agent(state):
    show_handshake("Firewall Replacement Agent", "Processing firewall component replacements.")
    matched_df = state["matched_df"]
    col_map = normalize_column_mapping(matched_df)
    result_df = matched_df.copy()
    result_df['quantity'] = pd.to_numeric(result_df.get(col_map.get('quantity'), 0), errors='coerce').fillna(0)
    result_df['price'] = pd.to_numeric(result_df.get(col_map.get('price'), 0.0), errors='coerce').fillna(0.0)
    state["result_df"] = calculate_total(result_df, lambda df: df['quantity'] * df['price'])
    return state


# Overwrite task_agents.py with complete logic
#task_agents_path = os.path.join(base_dir, "agents", "task_agents.py")
#with open(task_agents_path, "w", encoding="utf-8") as f:
    #f.write(final_task_agents_logic)

#task_agents_path