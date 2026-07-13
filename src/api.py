from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import sys
import os
import uuid
import json

app = FastAPI(title="Groww AI Agent API")

# Allow CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def run_pipeline(job_id: str):
    """Background task that runs the main.py pipeline"""
    env = os.environ.copy()
    env["JOB_ID"] = job_id
    script_path = os.path.join("src", "main.py")
    # Run the orchestrator asynchronously in a separate process
    subprocess.Popen([sys.executable, script_path], env=env)

@app.post("/api/generate")
async def generate_report():
    """Starts the 12-minute AI pipeline in the background"""
    job_id = str(uuid.uuid4())
    run_pipeline(job_id)
    return {"job_id": job_id, "status": "started"}

@app.get("/api/status/{job_id}")
async def get_status(job_id: str):
    """Polls the status of the background job"""
    status_file = os.path.join("data", f"job_{job_id}.json")
    if not os.path.exists(status_file):
        return {"phase": "Initializing", "status": "processing", "percent": 0, "error": ""}
    
    try:
        with open(status_file, "r") as f:
            data = json.load(f)
        return data
    except Exception as e:
        return {"phase": "Unknown", "status": "processing", "percent": 0, "error": str(e)}

@app.get("/api/report/{job_id}")
async def get_report(job_id: str):
    """Returns the final markdown report if completed"""
    report_file = os.path.join("data", "weekly_pulse_report.md")
    
    # First check if the job actually finished
    status_file = os.path.join("data", f"job_{job_id}.json")
    if os.path.exists(status_file):
        with open(status_file, "r") as f:
            status_data = json.load(f)
            if status_data.get("status") != "done":
                raise HTTPException(status_code=400, detail="Report is not finished generating yet.")
    else:
        raise HTTPException(status_code=404, detail="Job not found.")

    if not os.path.exists(report_file):
        raise HTTPException(status_code=404, detail="Report file missing.")

    with open(report_file, "r", encoding="utf-8") as f:
        content = f.read()

    return {"report": content}
