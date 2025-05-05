
import time
import pandas as pd
import sys
import random
from logic.application_logic import run_cpq_pipeline
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def evaluate_strategy(query, filepath, strategy):
    start_time = time.time()
    result = run_cpq_pipeline(user_query=query, filepath=filepath, strategy=strategy)
    end_time = time.time()
    
    
    if not result or result.get("result_df", pd.DataFrame()).empty:
        return {
            "strategy": strategy,
            "accuracy": 0,
            "latency": round(end_time - start_time, 2),
            "completeness": 0,
            "status": "failed"
        }

    df = result["result_df"]
    df = df[df["Component"].str.lower() != "grand total"] if "Component" in df.columns else df
    
    accuracy = 100 if not df.empty else 0
    completeness = len(df)

    return {
        "strategy": strategy,
        "accuracy": accuracy,
        "latency": round(end_time - start_time, 2),
        "completeness": completeness,
        "status": "success"
    }


def compare_strategies(query: str, filepath: str) -> pd.DataFrame:
    # Simulate timings and rows returned
    strategies = ["LangGraph", "CrewAI", "AutoGen"]
    results = []

    for strategy in strategies:
        time_taken = round(random.uniform(1.0, 2.5), 2)
        row_count = random.randint(5, 12)
        total = random.randint(1000, 10000)

        results.append({
            "Strategy": strategy,
            "TimeTaken (s)": time_taken,
            "Rows Returned": row_count,
            "Estimated Total": total
        })

    return pd.DataFrame(results)
