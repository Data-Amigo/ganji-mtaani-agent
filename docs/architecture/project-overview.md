# Project Overview

## Product Name

gAnji Mtaani

## Repository Name

ganji-mtaani-agent

## Product Goal

Build a scraper-first market intelligence and betting analytics platform that collects betting, prediction, and market data, stores it cleanly, generates explainable signals, and uses agents to improve scraping and decision support.

## Main Systems

- Scraper Engine: deterministic website fetching and extraction.
- Scraper UI: Streamlit interface to run and inspect scraping.
- Scraper Agent: reviews failures, suggests selector fixes, and supports extraction validation.
- Data Layer: PostgreSQL storage for historical observations and pipeline runs.
- Prediction Engine: explainable scoring and tiering.
- Decision Agent: reasoning layer for signals, risk, and user-facing explanations.
- Delivery Layer: dashboard and Telegram publishing.

## Source Strategy

Forebet and Polymarket are both important, but they serve different purposes.

Forebet is the first narrow betting source. It helps us prove the football prediction flow and build the first end-to-end scraper, parser, database, and signal pipeline.

Polymarket is a major strategic source. It contains broad prediction-market data across politics, economics, finance, crypto, culture, sports, and world events. For gAnji Mtaani, Polymarket should be treated as reusable market-intelligence infrastructure, not just a betting add-on.

Polymarket data can support:
- betting-style market analysis
- stock trader sentiment research
- macro event tracking
- crypto and political risk monitoring
- future analytics products outside this first project

## MVP Scope

The first useful version of gAnji Mtaani should prove one complete loop:

1. run a scraper from the Streamlit UI
2. extract data from one source, starting with Forebet
3. parse the result into a shared internal structure
4. show the extracted records in the UI
5. save the cleaned records to PostgreSQL
6. generate simple explainable signals
7. show those signals in the dashboard

After that loop is stable, Polymarket gets deeper extraction because its long-term value is broader and more reusable.

## Polymarket Scope

Polymarket extraction should eventually be broad and detailed.

Target data categories:
- market title
- market category
- event description
- outcomes
- prices or probabilities
- volume
- liquidity
- market status
- start and end dates
- tags or topic labels
- related markets
- historical changes where available

The long-term goal is to build a reusable Polymarket intelligence dataset that can support this product and future trading or research products.

## Non-MVP Scope

These are intentionally delayed until the data pipeline is reliable:

- fully autonomous selector repair
- advanced machine learning models
- automated betting execution
- paid subscription flows
- multi-user access control

## Agent Boundary

The Scraper Agent and Decision Agent should operate on evidence, not guesswork.

Scraper Agent inputs:
- target URL
- scraper run logs
- raw page snapshot summary
- parser errors
- previous successful selectors

Scraper Agent outputs:
- extraction confidence
- likely failure reason
- suggested selector changes
- human-review notes

Decision Agent inputs:
- structured events
- structured markets
- odds snapshots
- generated signals
- scoring rationale

Decision Agent outputs:
- signal explanation
- risk notes
- confidence commentary
- summary suitable for dashboard or Telegram

## Build Principle

The scraper must work first. Agents improve the workflow, but they should not replace reliable parsing, validation, and storage.

## Safety Principle

The system should help users make informed decisions, not promise guaranteed betting outcomes. All prediction outputs should be treated as analytical signals, not financial certainty.
