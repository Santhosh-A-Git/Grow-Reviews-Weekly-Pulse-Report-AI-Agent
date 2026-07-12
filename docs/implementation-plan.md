# Phase-Wise Implementation Plan

Based on the [Context](Context.md) and [System Architecture](architecture.md), this document outlines a step-by-step approach to building the AI Agent for mobile app review processing.

## Phase 1: Foundation & Data Ingestion
**Goal:** Set up the project environment and ingest raw review data.
- **Task 1.1:** Initialize the project repository (e.g., Python or Node.js environment).
- **Task 1.2:** Programmatically scrape 5,000 to 8,000 live reviews from the Google Play Store (App Store excluded).
- **Task 1.3:** Create a `Data Ingestion Module` to fetch and standardize the live data format (rating, title, text, date).
- **Task 1.4:** Implement date-filtering logic to isolate reviews from the last 8–12 weeks.

## Phase 2: Data Sanitization & PII Stripping
**Goal:** Ensure absolute data privacy before sending any information to the LLM.
- **Task 2.1:** Implement a `PII Stripping Module`. Use regex or local NLP models to identify and redact usernames, email addresses, phone numbers, and device IDs from review text.
- **Task 2.2:** Create unit tests using dummy PII-laden reviews to verify that the stripping module is 100% effective.
- **Task 2.3:** Filter out spam to improve signal-to-noise ratio. Drop reviews that:
  - Have fewer than 8 words.
  - Contain any emojis.
  - Are written in non-English languages (e.g., Hindi) using language detection.
- **Task 2.4:** Execute the `PII Stripping Module` on the live ingested dataset (`groww_live_reviews.csv`) to produce a fully sanitized dataset (`groww_live_reviews_clean.csv`) ready for LLM processing.

## Phase 3: Core AI Agent & LLM Integration
**Goal:** Process the sanitized reviews to generate the weekly pulse content and use Groq LLM for final generation.
- **Task 3.1:** Integrate the **Groq Python SDK** and prepare the Map-Reduce pipeline architecture to handle the 1,125+ reviews without context overflow.
- **Task 3.2:** **Map Phase (Chunking):** Split reviews into batches of ~100 to stay under the `llama-3.1-8b-instant` free tier limits. Design and test the **Theming Prompt** to extract local themes and quotes for each chunk.
- **Task 3.3:** **Reduce Phase (Global Synthesis):** Aggregate the local themes. Design and test the **Summarization Prompt** using Groq `llama-3.3-70b-versatile` to extract top 3 themes, 3 quotes, and 3 actionable steps. **Crucial Constraint:** The 70b model has strict free-tier limits (30 RPM, 1K TPM, 12K RPD, 100K TPD). We must strictly enforce token constraints on the aggregated input to avoid hitting the 1K Tokens Per Minute limit during synthesis.
- **Task 3.4:** Use Groq to format this synthesized data into the final weekly pulse report (scannable note of ≤250 words) and draft the final email payload.

## Phase 4: MCP Integration (Google Workspace)
**Goal:** Deliver the generated markdown pulse report via Google Docs and Gmail by connecting to our remotely hosted MCP server.
- **Task 4.1:** Integrate the official `mcp` and `httpx_sse` packages into the project dependencies to support remote Server-Sent Events (SSE) connections.
- **Task 4.2:** **Google Docs Delivery:** Create `src/mcp_delivery.py`. Connect to the remote MCP Server (`https://mcp-server-production-57b3.up.railway.app/sse`) using the `sse_client` transport. Execute the `gdocs_append_content` tool call to append the contents of `data/weekly_pulse_report.md` to a rolling Weekly Pulse Google Document.
- **Task 4.3:** **Gmail Delivery:** Within `mcp_delivery.py`, execute the `gmail_create_draft` (or `gmail_send_email`) tool call exposed by the remote MCP server to draft an email addressed to the stakeholders, containing the summarized pulse text and a link to the Google Doc.

## Phase 5: End-to-End Orchestration & Testing
**Goal:** Tie all standalone modules together into a single, automated execution pipeline.
- **Task 5.1:** Build `src/main.py`, a master orchestrator script that sequentially executes the sub-modules: `ingestion.py` → `sanitization.py` → `llm_engine.py` (Map-Reduce) → `mcp_delivery.py`.
- **Task 5.2:** Run an end-to-end integration test on the live Groww dataset to ensure the pipeline successfully flows from fetching 8,000 raw Play Store reviews to saving the final draft in Gmail.
- **Task 5.3:** Manually review the final generated Google Doc and Gmail draft to ensure formatting, the 250-word constraint, and strict PII privacy constraints were maintained perfectly.
- **Task 5.4:** (Optional) Set up a weekly trigger mechanism (e.g., Windows Task Scheduler or cron job) to run `src/main.py` automatically.
