# Project Context

## Overview
The goal of this project is to build an automated workflow that turns raw mobile app store feedback (from Apple App Store and Google Play Store) into a concise, actionable weekly pulse for the product team. The agent will aggregate, theme, summarize, and deliver insights through familiar surfaces: Google Docs for the written pulse and Gmail for an email draft.

## Core Objectives
- **Aggregate**: Pull recent App Store and Play Store reviews (last 8-12 weeks) from public exports.
- **Theme**: Group reviews into a maximum of 5 themes (e.g., onboarding, KYC, payments, etc.).
- **Summarize**: Generate a weekly one-page note (≤250 words) highlighting:
  - Top 3 themes.
  - 3 real user quotes (verbatim, stripped of PII).
  - 3 actionable ideas based on the themes.
- **Deliver**: 
  - Save the note to Google Docs for stakeholders.
  - Draft an email in Gmail containing the note or a link to it, addressed to the creator/alias.

## Key Stakeholders & Value
- **Product / Growth**: Prioritize fixes and improvements from real user signals.
- **Support**: Align messaging with actual user phrasing.
- **Leadership**: Provide a one-page health check without drowning in raw reviews.

## Technical Architecture & Constraints
- **Integration via MCP**: MUST use Model Context Protocol (MCP) servers to interact with Google Docs and Gmail (e.g., creating documents, drafting emails). Do NOT use direct Google API integrations, bespoke OAuth, or REST client wiring.
- **Data Source**: Use public review exports only. No scraping behind logins or violating Terms of Service.
- **Privacy**: No Personally Identifiable Information (PII) is allowed. Exclude usernames, emails, device IDs, etc., from any artifacts (ensure quotes are anonymized).
- **Format**: The final output must be highly scannable and adhere strictly to the length constraints.
