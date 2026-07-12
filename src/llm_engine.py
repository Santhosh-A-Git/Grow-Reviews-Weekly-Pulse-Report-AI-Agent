import os
import json
import time
import math
from datetime import datetime
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
# pyrefly: ignore [missing-import]
from groq import Groq

# Load environment variables
load_dotenv()

# Ensure GROQ_API_KEY is set
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY environment variable is missing. Please set it in a .env file.")

client = Groq(api_key=api_key)

# Constants
MAP_MODEL = "llama-3.1-8b-instant"
REDUCE_MODEL = "llama-3.3-70b-versatile"
CHUNK_SIZE = 100

def load_reviews(file_path: str) -> list:
    """Loads the cleaned reviews JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def chunk_data(data: list, chunk_size: int) -> list:
    """Splits a list into chunks of a specific size."""
    return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

def run_map_phase(chunk: list, chunk_index: int) -> str:
    """
    Analyzes a chunk of reviews to extract local themes and quotes.
    """
    print(f"Running Map Phase for Chunk {chunk_index} ({len(chunk)} reviews)...")
    
    # Format the chunk into a condensed string
    reviews_text = ""
    for r in chunk:
        reviews_text += f"[Rating: {r.get('score', 0)}/5] {r.get('clean_text', '')}\n"

    system_prompt = (
        "You are an expert product analyst. You will receive a batch of app reviews. "
        "Your goal is to extract the top 3 localized themes from this specific batch and "
        "capture 2 highly representative, verbatim (but anonymized) quotes that highlight these themes. "
        "Return your response in a clear, concise bulleted format. Do not include any conversational filler."
    )

    response = client.chat.completions.create(
        model=MAP_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Here are the reviews:\n\n{reviews_text}"}
        ],
        temperature=0.3,
        max_tokens=1024
    )
    
    return response.choices[0].message.content

def run_reduce_phase(map_outputs: list, date_context: str) -> str:
    """
    Aggregates all chunk summaries and generates the final Weekly Pulse Report.
    """
    print("Running Reduce Phase (Global Synthesis)...")
    
    aggregated_text = "\n\n--- NEXT CHUNK SUMMARY ---\n\n".join(map_outputs)

    system_prompt = (
        "You are a Lead Product Manager. You have been handed several mini-summaries of app reviews "
        "from the past 12 weeks. Your goal is to synthesize these into a single 'Weekly Pulse Report'.\n\n"
        "The report MUST be structured exactly as follows and strictly under 250 words:\n\n"
        "# Weekly Pulse Report\n"
        f"*{date_context}*\n\n"
        "## Top 3 Themes\n"
        "- (Theme 1)\n"
        "- (Theme 2)\n"
        "- (Theme 3)\n\n"
        "## Voice of the Customer (Top 3 Quotes)\n"
        "- \"(Quote 1)\" - [Rating]\n"
        "- \"(Quote 2)\" - [Rating]\n"
        "- \"(Quote 3)\" - [Rating]\n\n"
        "## Actionable Next Steps\n"
        "1. (Action 1)\n"
        "2. (Action 2)\n"
        "3. (Action 3)\n\n"
        "Keep it highly professional, scannable, and actionable. Do not exceed 250 words. Do not include conversational filler."
    )

    response = client.chat.completions.create(
        model=REDUCE_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Here are the localized summaries to synthesize:\n\n{aggregated_text}"}
        ],
        temperature=0.2,
        max_tokens=1500
    )
    
    return response.choices[0].message.content

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_file = os.path.join(base_dir, 'data', 'groww_live_reviews_clean.json')
    output_file = os.path.join(base_dir, 'data', 'weekly_pulse_report.md')
    
    if not os.path.exists(data_file):
        print(f"Error: Data file {data_file} not found. Please run ingestion and sanitization first.")
        return

    print("Loading cleaned reviews...")
    reviews = load_reviews(data_file)
    print(f"Loaded {len(reviews)} reviews.")
    
    chunks = chunk_data(reviews, CHUNK_SIZE)
    print(f"Split data into {len(chunks)} chunks of max {CHUNK_SIZE} reviews each.")
    
    map_results = []
    for i, chunk in enumerate(chunks, 1):
        result = run_map_phase(chunk, i)
        map_results.append(result)
        
        # Groq Free Tier TPM Limit (6000 Tokens per Minute)
        # Sleep for 61 seconds to refresh the TPM quota between chunks
        if i < len(chunks):
            print("Sleeping for 61 seconds to respect Groq rate limits...")
            time.sleep(61)
        
    print(f"Successfully processed {len(map_results)} chunks.")
    
    # Save the localized themes for auditing/transparency
    intermediate_file = os.path.join(base_dir, 'data', 'localized_themes.md')
    aggregated_text = "\n\n--- NEXT CHUNK SUMMARY ---\n\n".join(map_results)
    with open(intermediate_file, 'w', encoding='utf-8') as f:
        f.write("# Localized Themes (Map Phase Output)\n\n" + aggregated_text)
    print(f"Saved localized themes to {intermediate_file}")
    
    # Calculate date range for the report
    dates = [r.get("submitted_at") for r in reviews if r.get("submitted_at")]
    if dates:
        dates.sort()
        start_date = dates[0].split()[0]
        end_date = dates[-1].split()[0]
        report_date = datetime.now().strftime("%Y-%m-%d")
        date_context = f"Report Date: {report_date} | Reviews Collected: {start_date} to {end_date}"
    else:
        date_context = "Report Date: Unknown | Reviews Collected: Unknown"
        
    final_report = run_reduce_phase(map_results, date_context)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(final_report)
        
    print(f"\nFinal Weekly Pulse Report generated and saved to {output_file}!")
    
if __name__ == "__main__":
    main()
