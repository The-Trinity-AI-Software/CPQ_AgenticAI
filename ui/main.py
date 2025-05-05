# -*- coding: utf-8 -*-
"""
Created on Tue Apr 15 18:33:01 2025

@author: Ravikiran Jonnalagadda
"""

import sys
import os
import time
from flask import Flask, request, jsonify, send_file, render_template, Response
import pandas as pd
from datetime import datetime
from logic.application_logic import stream_cpq_pipeline
from logic.logger_setup import setup_logger




# Add project root path to sys.path so we can import logic, agents, core_agents etc.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

app = Flask(__name__, template_folder='../templates')
logger = setup_logger()

TEMPLATE_MAP = {
    "itam_reload": r"G:/MVP/mnt/data/CPQ_AgenticAI/excel/ITAMRELOAD.xlsx",
    "certificate_renewal": r"G:/MVP/mnt/data/CPQ_AgenticAI/excel/cert_renewal.xlsx",
    "add_new_workstation": r"G:/MVP/mnt/data/CPQ_AgenticAI/excel/workstation.xlsx"
}

TEMPLATE_CACHE = {
    k: pd.read_excel(v) for k, v in TEMPLATE_MAP.items() if os.path.exists(v)
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/cpq/stream")
def stream():
    query = request.args.get("query")
    task_type = request.args.get("task")
    strategy = request.args.get("strategy")
    sample_path = TEMPLATE_MAP.get(task_type)

    def event_stream():
        for msg in stream_cpq_pipeline(query, sample_path, strategy):
            yield f"data: {msg}\n\n"

    return Response(event_stream(), mimetype='text/event-stream')
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
    try:
        data = request.get_json(force=True)
        query = data.get("query")
        task_type = data.get("task")
        strategy = data.get("strategy")
        sample_path = TEMPLATE_MAP.get(task_type)

        if not query or not task_type or not strategy:
            return jsonify({"error": "Missing required fields: query, task, or strategy."}), 400

        if not os.path.exists(sample_path):
            return jsonify({"error": "File path not found."}), 404

        return Response(stream_cpq_pipeline(query, sample_path, strategy), mimetype='text/plain')

    except Exception as e:
        logger.exception("❌ Error in /cpq/predict endpoint:")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route("/cpq/download", methods=["GET"])
def download():
    path = request.args.get("path")
    if not path or not os.path.exists(path):
        return jsonify({"error": "Download path invalid."}), 404
    return send_file(path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, port=8081)
