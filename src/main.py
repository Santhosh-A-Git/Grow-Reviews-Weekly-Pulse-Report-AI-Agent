import asyncio
import os
import time
import sys
import subprocess

def run_step(step_name, script_name):
    print(f"\n{'='*50}")
    print(f"STARTING PHASE: {step_name}")
    print(f"{'='*50}")
    start_time = time.time()
    
    script_path = os.path.join("src", script_name)
    exit_code = subprocess.call([sys.executable, script_path])
    
    elapsed = time.time() - start_time
    if exit_code == 0:
        print(f"\n[SUCCESS] {step_name} COMPLETED SUCCESSFULLY (took {elapsed:.2f}s)\n")
    else:
        print(f"\n[FAILED] {step_name} FAILED with exit code {exit_code}")
        exit(1)

def main():
    print("GROWW AI AGENT: WEEKLY PULSE ORCHESTRATION PIPELINE")
    print("This pipeline will scrape reviews, sanitize PII, generate an LLM report, and deliver via MCP.")
    
    # 1. Ingestion Phase
    run_step("Data Ingestion", "ingestion.py")
    
    # 2. Sanitization Phase
    run_step("Data Sanitization & PII Stripping", "sanitization.py")
    
    # 3. LLM Engine (Map-Reduce) Phase
    run_step("LLM Engine (Pulse Report Generation)", "llm_engine.py")
    
    # 4. MCP Delivery Phase
    run_step("MCP Google Workspace Delivery", "mcp_delivery.py")
    
    print("END-TO-END PIPELINE COMPLETED SUCCESSFULLY!")
    print("Please check your Google Doc and Gmail Drafts to see the results.")

if __name__ == "__main__":
    main()
