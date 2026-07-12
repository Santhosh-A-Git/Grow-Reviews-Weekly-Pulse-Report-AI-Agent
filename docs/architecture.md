# System Architecture

## Overview
The architecture is designed to automate the ingestion, analysis, and distribution of mobile app reviews. It leverages a central AI Agent that interacts with Large Language Models (LLMs) for natural language processing and utilizes the Model Context Protocol (MCP) to seamlessly communicate with Google Workspace tools without the need for bespoke OAuth/REST integrations.

## High-Level Architecture Diagram
```mermaid
graph TD
    subgraph Data Sources
        B[Google Play Store (Live Scraped)]
    end

    subgraph Core AI Agent System
        C[Data Ingestion & Pre-processing]
        D[PII Stripping & Anonymization]
        E[LLM Engine / Prompting]
    end

    subgraph Integration Layer
        F[MCP Server: Google Docs]
        G[MCP Server: Gmail]
    end

    subgraph Outputs
        H[Weekly Pulse Document]
        I[Draft Email]
    end

    B --> C
    C --> D
    D --> E
    E --> F
    E --> G
    F --> H
    G --> I
```

## Component Details

### 1. Data Sources & Ingestion
- **Inputs**: Programmatically scraped reviews (5,000 to 8,000) from the Google Play Store covering the last 8–12 weeks.
- **Format**: Live JSON payloads converted into standardized Pandas DataFrames (rating, title, text, date).
- **Ingestion Module**: A Python script utilizing `google-play-scraper` to pull live data dynamically.

### 2. Data Processing & Anonymization
- **PII Stripping**: Before any data is sent to the LLM or stored in the final output, all Personally Identifiable Information (PII) is removed. This includes usernames, emails, and device IDs.
- **Quality Filtering**: 
  - **Date**: Keep only reviews from the last 8-12 weeks.
  - **Word Count**: Drop reviews with fewer than 8 words.
  - **Emojis**: Drop reviews containing emojis.
  - **Language**: Drop non-English reviews (e.g., Hindi) using `langdetect`.

### 3. Core AI Agent (LLM Engine)
- **Role**: The brain of the system, responsible for analyzing the cleaned reviews and generating the final output.
- **Functions**:
  - **Clustering/Theming**: Analyzes the corpus of reviews and categorizes them into a maximum of 5 distinct themes (e.g., onboarding, payments).
  - **Summarization & Quote Extraction**: Identifies the top 3 themes, extracts 3 verbatim (but anonymized) user quotes, and limits the final text to under 250 words.
  - **Actionable Insights**: Generates 3 concrete action ideas based on the derived themes.
  - **Final Content Generation**: Uses the Groq LLM specifically to write and format the final weekly pulse report and the draft email based on the extracted insights.
  - **Rate Limit Management**: Implements a Map-Reduce batching architecture to strictly adhere to the Groq free-tier limits, particularly the `llama-3.3-70b-versatile` constraints: 30 requests per minute, 1K tokens per minute, 12K requests per day, and 100K tokens per day.

### 4. Integration Layer (MCP Servers)
Instead of hardcoding REST APIs and managing OAuth tokens directly within the core agent, the system utilizes standardized MCP (Model Context Protocol) servers.
- **Google Docs MCP**: Exposes tools allowing the AI Agent to create a new document or append to an existing one. The Agent uses this to save the generated one-page weekly pulse.
- **Gmail MCP**: Exposes tools allowing the AI Agent to create email drafts. The Agent uses this to draft an email containing a link to the generated Google Doc, addressed to the appropriate stakeholders.

## Data Flow & Execution Sequence
1. **Trigger**: The workflow is initiated (e.g., via a weekly cron job or manual trigger).
2. **Read**: The Ingestion Module reads the latest review exports.
3. **Clean**: The data is sanitized to remove PII.
4. **Analyze**: The LLM Engine processes the text, clusters themes, selects quotes, and drafts the pulse and action items.
5. **Format**: The AI Agent formats the output into a scannable structure.
6. **Publish to Docs**: The Agent calls the Google Docs MCP server to create the Weekly Pulse document.
7. **Draft Email**: The Agent calls the Gmail MCP server to generate a draft email linking to the new document.

## Technical Constraints & Security
- **No Direct Google APIs**: All Google integrations must occur via MCP.
- **Public Data Only**: No scraping of private or login-walled stores.
- **Data Privacy**: Absolute strict adherence to PII removal; user quotes must be entirely anonymous.
