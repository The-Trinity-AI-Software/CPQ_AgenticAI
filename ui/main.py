# -*- coding: utf-8 -*-
"""
Created on Tue Apr 15 18:33:01 2025

@author: Ravikiran jonnalagadda
"""

from flask import Flask, request, jsonify, send_file
import pandas as pd
import os
from datetime import datetime
from logic.application_logic import run_cpq_pipeline
from logic.logger_setup import setup_logger
from agentic_evaluation import compare_strategies

app = Flask(__name__)
logger = setup_logger()

TEMPLATE_MAP = {
    "itam_reload": r"G:/MVP/mnt/data/CPQ_Agentic_Workflow/excel/ITAMRELOAD.xlsx",
    "certificate_renewal": r"G:/MVP/mnt/data/CPQ_Agentic_Workflow/excel/cert_renewal.xlsx",
    "add_new_workstation": r"G:/MVP/mnt/data/CPQ_Agentic_Workflow/excel/workstation.xlsx"
}

@app.route("/cpq/template", methods=["GET"])
def get_template():
    task_type = request.args.get("task")
    file_path = TEMPLATE_MAP.get(task_type)
    if not file_path or not os.path.exists(file_path):
        return jsonify({"error": f"Template for '{task_type}' not found."}), 404
    df = pd.read_excel(file_path).head(10)
    for col in df.columns:
        if "price" in col.lower() or "qty" in col.lower() or "quantity" in col.lower():
            df[col] = ""
    return df.to_json(orient="records")

@app.route("/cpq/predict", methods=["POST"])
def predict():
    data = request.get_json()
    query = data.get("query")
    task_type = data.get("task")
    strategy = data.get("strategy")
    sample_path = TEMPLATE_MAP.get(task_type)

    if not query or not task_type or not strategy:
        return jsonify({"error": "Missing required fields: query, task, or strategy."}), 400

    if not os.path.exists(sample_path):
        return jsonify({"error": "File path not found."}), 404

    result = run_cpq_pipeline(user_query=query, filepath=sample_path, strategy=strategy)
    if not result or result.get("result_df") is None or result["result_df"].empty:
        return jsonify({"error": "No valid data returned from pipeline."}), 500

    df_result = result["result_df"]
    df_result["Total"] = pd.to_numeric(df_result["Total"], errors="coerce")
    grand_total = df_result["Total"].sum()

    df_result = df_result[df_result.drop("Total", axis=1).apply(lambda x: x.astype(str).str.strip().any(), axis=1)]
    total_row = pd.DataFrame([{col: "" for col in df_result.columns}], index=["Grand Total"])
    total_row["Total"] = grand_total
    df_result = pd.concat([df_result, total_row]).reset_index(drop=True)

    today = datetime.now().strftime("%Y-%m-%d")
    output_path = f"G:/MVP/mnt/data/CPQ_Agentic_Workflow/outputs/test_results_{today}.xlsx"
    df_result.to_excel(output_path, index=False, engine="openpyxl")

    return jsonify({
        "grand_total": grand_total,
        "records": df_result.to_dict(orient="records"),
        "download": output_path
    })

@app.route("/cpq/download", methods=["GET"])
def download():
    path = request.args.get("path")
    if not path or not os.path.exists(path):
        return jsonify({"error": "Download path invalid."}), 404
    return send_file(path, as_attachment=True)

@app.route("/cpq/performance", methods=["GET"])
def compare_agents():
    comparison_df = compare_strategies()
    return comparison_df.to_json(orient="records")

if __name__ == "__main__":
    app.run(debug=True, port=8000)
