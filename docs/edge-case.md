# Edge Cases & Corner Scenarios

This document outlines potential edge cases and corner scenarios that the AI Agent might encounter during the execution of the mobile app review pipeline, along with strategies for handling them.

## 1. Data Ingestion & Formatting
| Edge Case | Impact | Handling Strategy |
| :--- | :--- | :--- |
| **No Reviews in Timeframe** | Pipeline has no data to process for the week. | Detect early in the Ingestion Module. Halt the LLM/Groq pipeline and use the MCP server to draft a "No new reviews for the past week" notification. |
| **Extremely Large Export Files** | Exceeds the token context window of the LLM. | Implement a sampling strategy (e.g., sort by 'most helpful' or take a randomized, representative subset of reviews) to fit within context limits. |
| **Malformed CSV/JSON** | Ingestion script crashes. | Wrap file parsing in `try/except` blocks. If parsing fails, trigger a failure alert via the Gmail MCP server. |
| **Missing Review Text (Rating Only)** | Cannot extract themes or quotes. | Filter out reviews that contain empty or null text strings during the initial data standardization phase. |
| **Non-English Reviews** | Theming and quote extraction may fail or mix languages. | Either utilize the LLM's multilingual capabilities to translate and cluster, or add a pre-processing step to filter out non-target languages. |

## 2. Data Sanitization & Privacy
| Edge Case | Impact | Handling Strategy |
| :--- | :--- | :--- |
| **Obfuscated PII** (e.g., "john at gmail dot com") | Regex might miss it, causing a privacy violation. | Use a combination of Regex and an NLP-based PII detection model (like Presidio) before feeding data to the LLM. |
| **Review is entirely PII** | Leaves an empty review post-sanitization. | If a review is scrubbed to the point of being empty or incoherent (e.g., < 3 words remaining), discard it entirely. |

## 3. Core AI Agent & LLM (Including Groq)
| Edge Case | Impact | Handling Strategy |
| :--- | :--- | :--- |
| **LLM Hallucinates Quotes** | Generates fabricated quotes instead of verbatim snippets. | Use strict prompting (e.g., "Respond ONLY with exact substrings from the provided text"). Implement a post-generation validation check that verifies the generated quote exists in the source text. |
| **Word Count Exceeds 250 Words** | Violates the strict scannability requirement. | Add a validation step after Groq LLM generation. If the word count > 250, issue a reprompt to Groq to condense the text, or explicitly set `max_tokens` limits. |
| **Fewer Than 3 Themes Exist** | Forcing 3-5 themes creates redundant or nonsensical categories. | Instruct the LLM to identify *up to* 5 themes, and only highlight the top 3 *if* 3 distinct themes exist. The system should gracefully handle 1 or 2 themes. |
| **API Rate Limits / Timeouts** | LLM or Groq API fails to return a response. | Implement exponential backoff and retry logic for all API calls. Fallback to a secondary model if Groq remains unavailable after maximum retries. |
| **Malformed Output Structure** | Downstream MCP tools cannot parse the LLM output. | Use Structured Outputs (e.g., JSON schema enforcement) during the LLM calls to guarantee the response matches the required data model before formatting. |

## 4. MCP Integrations (Google Docs & Gmail)
| Edge Case | Impact | Handling Strategy |
| :--- | :--- | :--- |
| **MCP Server Unreachable** | Cannot create document or draft email. | Log the error, save the Groq-generated payload locally, and retry the MCP connection on a schedule. |
| **Google Docs Permission Denied** | Cannot append or create the Pulse document. | The Gmail MCP fallback should trigger an email to the administrator containing the raw Pulse note and a warning about the Docs permission failure. |
| **Token Expiry / Auth Failure on MCP Host** | All output delivery fails. | Halt execution gracefully. Send an alert to standard output or a designated monitoring channel requesting manual re-authentication of the MCP servers. |
