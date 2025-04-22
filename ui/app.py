import sys
import os
import time
from datetime import datetime

from flask import Flask, request, jsonify, send_file, render_template
import pandas as pd
from flask_cors import CORS

# Add project root to Python path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from logic.application_logic import run_cpq_pipeline
from logic.logger_setup import setup_logger
from agentic_evaluation import compare_strategies

app = Flask(__name__, template_folder='../templates')
CORS(app)

logger = setup_logger()

TEMPLATE_MAP = {
    "itam_reload": r"/home/CPQ_AgenticAI/excel/ITAMRELOAD.xlsx",
    "certificate_renewal": r"/home/CPQ_AgenticAI/excel/cert_renewal.xlsx",
    "add_new_workstation": r"/home/CPQ_AgenticAI/excel/workstation.xlsx"
}

TEMPLATE_CACHE = {
    k: pd.read_excel(v) for k, v in TEMPLATE_MAP.items() if os.path.exists(v)
}


@app.route("/")
def index():
    logger.info("📄 Rendering index.html")
    return render_template("index.html")


@app.route("/cpq/template", methods=["GET"])
def get_template():
    task_type = request.args.get("task")
    logger.info(f"📥 Template requested for task: {task_type}")
    file_path = TEMPLATE_MAP.get(task_type)
    if not file_path or not os.path.exists(file_path):
        logger.warning(f"Template not found for task: {task_type}")
        return jsonify({"error": f"Template for '{task_type}' not found."}), 404

    df = pd.read_excel(file_path).head(10)
    for col in df.columns:
        if "price" in col.lower() or "qty" in col.lower() or "quantity" in col.lower():
            df[col] = ""

    logger.debug(f"📊 Returning template preview for task: {task_type}")
    return df.to_json(orient="records")


@app.route("/cpq/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json(force=True)
        query = data.get("query")
        task_type = data.get("task")
        strategy = data.get("strategy")
        logger.info(f"🔍 Predict request received | Task: {task_type} | Strategy: {strategy}")

        sample_path = TEMPLATE_MAP.get(task_type)
        if not query or not task_type or not strategy:
            logger.error("Missing query, task, or strategy in request.")
            return jsonify({"error": "Missing required fields: query, task, or strategy."}), 400

        if not os.path.exists(sample_path):
            logger.error(f"Sample path does not exist: {sample_path}")
            return jsonify({"error": "File path not found."}), 404

        result = run_cpq_pipeline(user_query=query, filepath=sample_path, strategy=strategy)
        df_result = result.get("result_df")

        if not isinstance(df_result, pd.DataFrame):
            logger.error("Invalid result_df returned from pipeline.")
            return jsonify({"error": "No valid data returned from pipeline."}), 500

        logger.debug(f"🧾 Columns in result_df: {df_result.columns.tolist()}")

        # Handle missing "Total" column
        if "Total" not in df_result.columns:
            logger.warning("⚠️ 'Total' column not found. Attempting to calculate it.")
            price_col = next((col for col in df_result.columns if "price" in col.lower()), None)
            qty_col = next((col for col in df_result.columns if "qty" in col.lower() or "quantity" in col.lower()), None)

            if price_col and qty_col:
                df_result["Total"] = pd.to_numeric(df_result[price_col], errors="coerce") * pd.to_numeric(df_result[qty_col], errors="coerce")
                logger.info(f"🧮 Computed 'Total' using: {price_col} × {qty_col}")
            else:
                logger.error("❌ Cannot calculate 'Total'. No matching price or quantity columns.")
                df_result["Total"] = 0

        df_result["Total"] = pd.to_numeric(df_result["Total"], errors="coerce")

        if "Total" in df_result.columns:
            cols = [col for col in df_result.columns if col != "Total"] + ["Total"]
            df_result = df_result[cols]

        df_result = df_result[df_result.drop("Total", axis=1).apply(lambda x: x.astype(str).str.strip().any(), axis=1)]
        df_result = df_result.reset_index(drop=True)

        grand_total = df_result["Total"].sum()
        total_row = {col: "" for col in df_result.columns}
        total_row["Total"] = grand_total
        df_result.loc[len(df_result)] = total_row

        today = datetime.now().strftime("%Y-%m-%d")
        output_excel_path = f"/home/CPQ_Agentic_Workflow/outputs/test_results_{today}.xlsx"
        output_json_path = f"/home/CPQ_Agentic_Workflow/outputs/test_results_{today}.json"
        df_result.to_excel(output_excel_path, index=False, engine="openpyxl")
        df_result.to_json(output_json_path, orient="records")

        strategies = ["langgraph", "crewai", "autogen"]
        performance_results = []
        best_strategy = None
        min_time = float('inf')

        for strat in strategies:
            start = time.time()
            strat_result = run_cpq_pipeline(user_query=query, filepath=sample_path, strategy=strat)
            duration = round(time.time() - start, 2)
            strat_df = strat_result.get("result_df", pd.DataFrame())
            rows = len(strat_df) if isinstance(strat_df, pd.DataFrame) else 0
            total_amt = strat_df["Total"].sum() if "Total" in strat_df.columns else 0
            performance_results.append({
                "Strategy": strat.title(),
                "Time Taken (s)": duration,
                "Rows Returned": rows,
                "Total Value": float(total_amt)
            })
            if duration < min_time:
                min_time = duration
                best_strategy = strat.title()

        comparison_summary = f"Based on the current task, <b>{best_strategy}</b> was the most efficient, completing in <b>{min_time} seconds</b>."
        logger.info(f"✅ Prediction complete | Best Strategy: {best_strategy}")

        return jsonify({
            "grand_total": float(grand_total),
            "records": df_result.to_dict(orient="records"),
            "download_excel": output_excel_path,
            "download_json": output_json_path,
            "agent_comparison": performance_results,
            "comparison_summary": comparison_summary
        })

    except Exception as e:
        logger.exception("❌ Error in /cpq/predict endpoint:")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route("/cpq/download", methods=["GET"])
def download():
    path = request.args.get("path")
    if not path or not os.path.exists(path):
        logger.warning(f"Invalid download path requested: {path}")
        return jsonify({"error": "Download path invalid."}), 404
    logger.info(f"📤 Sending file: {path}")
    return send_file(path, as_attachment=True)


@app.route("/cpq/performance", methods=["GET"])
def compare_agents():
    task_type = request.args.get("task", "itam_reload")
    query = request.args.get("query", "test")
    sample_path = TEMPLATE_MAP.get(task_type)

    if not sample_path or not os.path.exists(sample_path):
        logger.error(f"Sample path not found for task: {task_type}")
        return jsonify({"error": f"Filepath not found for task: {task_type}"}), 400

    try:
        logger.info(f"🧪 Comparing agent performance | Task: {task_type}")
        comparison_df = compare_strategies(query=query, filepath=sample_path)
        return comparison_df.to_json(orient="records")
    except Exception as e:
        logger.exception("❌ Error in /cpq/performance endpoint:")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


if __name__ == "__main__":
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.DEBUG)
    app.logger.setLevel(logging.DEBUG)
    app.run(host='0.0.0.0', debug=True, port=8000)
