# 🧠 CPQ Agentic AI Workflow (Flask API)

This project provides a Flask-based backend for the CPQ (Configure, Price, Quote) automation pipeline using Agentic AI strategies such as LangGraph, CrewAI, and AutoGen.

## 🚀 Features

- Upload and preview deal templates for:
  - ITAM Reload
  - Certificate Renewal
  - New Workstation Setup
- Run CPQ pipeline and generate pricing and validation outputs
- Download output as Excel
- Support for LangGraph, CrewAI, and AutoGen strategies

## 📦 API Endpoints

### 1. GET `/cpq/template?task=add_new_workstation`
Returns preview data for a specific deal type (top 10 rows).

### 2. POST `/cpq/predict`
Run CPQ automation workflow.

**Request Body:**
```json
{
  "query": "certificate renewal for customer Company_36",
  "task": "certificate_renewal",
  "strategy": "langgraph"
}
```

**Returns:**
- Deal rows
- Grand total
- Excel output path

### 3. GET `/cpq/download?path=G:/...`
Download the Excel file generated from the pipeline.

---

## 📁 Folder Structure

```
/logic
    application_logic.py
    logger_setup.py
/agents
    task_agents.py
/core_agents
    core_agents.py
/ui
    app.py              <-- Flask API
/excel/
    ITAMRELOAD.xlsx
    cert_renewal.xlsx
    workstation.xlsx
/outputs/
    test_results_YYYY-MM-DD.xlsx
/logs/
    cpq_session_TIMESTAMP.log
```

---

## 🧪 Testing

Run locally:

```bash
python ui/app.py
```

Test using curl:

```bash
curl -X POST http://localhost:5000/cpq/predict -H "Content-Type: application/json" -d '{
  "query": "add workstation for English Group",
  "task": "add_new_workstation",
  "strategy": "langgraph"
}'
```

---

## 🛠 Requirements

```bash
pip install -r requirements.txt
```

## 🌐 Deployment

Can be deployed on:
- AWS Lambda + API Gateway
- Docker Container + EC2
- Any WSGI-compatible web server

---

## 👨‍💻 Maintainer

Ravikiran Jonnalagadda  
Email: [Your Email]  
GitHub: [Your GitHub]