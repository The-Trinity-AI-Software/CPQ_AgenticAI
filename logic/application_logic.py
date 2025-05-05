import io
import contextlib
import json
from datetime import datetime
import pandas as pd
from core_agents.core_agents import orchestrator_agent, discovery_agent, validation_agent
from agents.task_agents import itam_reload_agent, certificate_renewal_agent, workstation_agent
from llm_strategies.langgraph_CPQ import run_langgraph_cpq
from llm_strategies.crewai_CPQ import run_crewai_cpq
from llm_strategies.autogen_CPQ import run_autogen_cpq


def run_cpq_pipeline(user_query, filepath, strategy):
    if strategy == "langgraph":
        return run_langgraph_cpq(user_query=user_query, filepath=filepath)
    elif strategy == "crewai":
        return run_crewai_cpq(user_query=user_query, filepath=filepath)
    elif strategy == "autogen":
        return run_autogen_cpq(user_query=user_query, filepath=filepath)
    else:
        return None


# This function streams handshakes and final results
def stream_cpq_pipeline(user_query, filepath, strategy):
    with io.StringIO() as buf, contextlib.redirect_stdout(buf):
        result = run_cpq_pipeline(user_query, filepath, strategy)
        handshakes = buf.getvalue()

    # send handshake messages first
    for line in handshakes.strip().splitlines():
        yield f"HANDSHAKE::{line}\n"

    if not result:
        yield "HANDSHAKE::❌ No valid data returned from pipeline.\n"
        return

    df_result = result.get("result_df", pd.DataFrame())
    df_result["Total"] = pd.to_numeric(df_result["Total"], errors="coerce")

    if "Total" in df_result.columns:
        cols = [col for col in df_result.columns if col != "Total"] + ["Total"]
        df_result = df_result[cols]

    df_result = df_result[df_result.drop("Total", axis=1).apply(lambda x: x.astype(str).str.strip().any(), axis=1)]
    df_result = df_result.reset_index(drop=True)

    grand_total = df_result["Total"].sum()

    # ✅ Generate Excel and JSON
    today = datetime.now().strftime("%Y-%m-%d")
    output_excel_path = f"G:/MVP/mnt/data/CPQ_Agentic_Workflow/outputs/test_results_{today}.xlsx"
    output_json_path = f"G:/MVP/mnt/data/CPQ_Agentic_Workflow/outputs/test_results_{today}.json"

    df_result.to_excel(output_excel_path, index=False, engine="openpyxl")
    df_result.to_json(output_json_path, orient="records")

    result_data = {
        "grand_total": float(grand_total),
        "records": df_result.to_dict(orient="records"),
        "download_excel": output_excel_path,
        "download_json": output_json_path
    }

    # ✅ Send FINAL result
    yield f"FINAL_RESULT::{json.dumps(result_data)}\n"
