import pandas as pd
import sys
import os
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.normalize import normalize_column_mapping
from prompts.agent_prompts import ITAM_RELOAD_PROMPT, CERTIFICATE_RENEWAL_PROMPT, ADD_WORKSTATION_PROMPT

def show_handshake(agent_name, message):
    print(f"HANDSHAKE::{agent_name}::{message}")

def calculate_total(result_df, formula):
    result_df['Total'] = formula(result_df)
    grand_total = result_df['Total'].sum()
    total_row = pd.DataFrame([{**{col: "" for col in result_df.columns if col != 'Total'}, "Total": grand_total}], index=[len(result_df)])
    return pd.concat([result_df, total_row])

def itam_reload_agent(state):
    show_handshake("ITAM Reload Agent", "Initiated and processing ITAM data...")
    matched_df = state["matched_df"]
    col_map = normalize_column_mapping(matched_df)
    result_df = matched_df.copy()
    result_df['quantity'] = pd.to_numeric(result_df.get(col_map.get('quantity'), 0), errors='coerce').fillna(0)
    result_df['price'] = pd.to_numeric(result_df.get(col_map.get('price'), 0.0), errors='coerce').fillna(0.0)
    state["result_df"] = calculate_total(result_df, lambda df: df['quantity'] * df['price'])
    show_handshake("ITAM Reload Agent", "Calculated totals and completed processing.")
    return state

def certificate_renewal_agent(state):
    show_handshake("Certificate Renewal Agent", "Initiated and processing certificate data...")
    matched_df = state["matched_df"]
    col_map = normalize_column_mapping(matched_df)
    result_df = matched_df.copy()
    result_df['quantity'] = pd.to_numeric(result_df.get(col_map.get('quantity'), 0), errors='coerce').fillna(0)
    result_df['laborprice'] = pd.to_numeric(result_df.get(col_map.get('laborprice'), 0.0), errors='coerce').fillna(0.0)
    result_df['certprice'] = pd.to_numeric(result_df.get(col_map.get('certprice'), 0.0), errors='coerce').fillna(0.0)
    state["result_df"] = calculate_total(result_df, lambda df: (df['laborprice'] * df['quantity']) + df['certprice'])
    show_handshake("Certificate Renewal Agent", "Calculated totals and completed processing.")
    return state

def workstation_agent(state):
    show_handshake("Workstation Agent", "Initiated and processing workstation data...")
    matched_df = state["matched_df"]
    col_map = normalize_column_mapping(matched_df)
    result_df = matched_df.copy()
    result_df['quantity'] = pd.to_numeric(result_df.get(col_map.get('quantity'), 0), errors='coerce').fillna(0)
    result_df['price'] = pd.to_numeric(result_df.get(col_map.get('price'), 0.0), errors='coerce').fillna(0.0)
    state["result_df"] = calculate_total(result_df, lambda df: df['quantity'] * df['price'])
    show_handshake("Workstation Agent", "Calculated totals and completed processing.")
    return state
