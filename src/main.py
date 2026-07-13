import asyncio
import os
import time
import sys
import subprocess
import json

def update_status(job_id, phase, status, percent, error=""):
    if not job_id: return
    status_file = os.path.join("data", f"job_{job_id}.json")
    data = {}
    if os.path.exists(status_file):
        try:
            with open(status_file, "r") as f:
                data = json.load(f)
        except: pass
    data.update({
        "phase": phase,
        "status": status,
        "percent": percent,
        "error": error
    })
    os.makedirs("data", exist_ok=True)
    with open(status_file, "w") as f:
        json.dump(data, f)

def run_step(step_name, script_name, job_id, percent):
    print(f"\n{'='*50}")
    print(f"STARTING PHASE: {step_name}")
    print(f"{'='*50}")
    
    update_status(job_id, step_name, "processing", percent)
    start_time = time.time()
    
    script_path = os.path.join("src", script_name)
    exit_code = subprocess.call([sys.executable, script_path])
    
    elapsed = time.time() - start_time
    if exit_code == 0:
        print(f"\n[SUCCESS] {step_name} COMPLETED SUCCESSFULLY (took {elapsed:.2f}s)\n")
    else:
        print(f"\n[FAILED] {step_name} FAILED with exit code {exit_code}")
        update_status(job_id, step_name, "failed", percent, f"Failed with exit code {exit_code}")
        sys.exit(1)

def main():
    job_id = os.environ.get("JOB_ID")
    if job_id:
        update_status(job_id, "Initializing", "processing", 5)

    print("GROWW AI AGENT: WEEKLY PULSE ORCHESTRATION PIPELINE")
    
    # 1. Ingestion Phase
    run_step("Data Ingestion", "ingestion.py", job_id, 10)
    
    # 2. Sanitization Phase
    run_step("Data Sanitization & PII Stripping", "sanitization.py", job_id, 30)
    
    # 3. LLM Engine (Map-Reduce) Phase
    # Note: LLM Engine takes ~12 minutes. The UI will sit at 40% for a long time.
    run_step("LLM Engine (Pulse Report Generation)", "llm_engine.py", job_id, 40)
    
    # 4. MCP Delivery Phase
    run_step("MCP Google Workspace Delivery", "mcp_delivery.py", job_id, 95)
    
    if job_id:
        update_status(job_id, "Complete", "done", 100)

    print("END-TO-END PIPELINE COMPLETED SUCCESSFULLY!")
    print("Please check your Google Doc and Gmail Drafts to see the results.")

if __name__ == "__main__":
    main()
