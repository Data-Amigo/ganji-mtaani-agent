# Data Flow

This document defines how data should move through gAnji Mtaani.

## High-Level Flow

```text
Website or Market Source
  -> Scraper Engine
  -> Raw Snapshot
  -> Parser
  -> Normalized Records
  -> PostgreSQL
  -> Prediction or Market Intelligence Engine
  -> Decision Agent
  -> Streamlit / Telegram
```

## Step 1: Source to Scraper Engine

The scraper engine opens the target page or source endpoint and collects raw content.

Initial sources:
- Forebet
- Polymarket

Forebet is used to prove the first betting-prediction workflow.

Polymarket is treated as a broader market-intelligence source because it contains rich information across many topics that can support future trading, research, and analytics projects.

## Step 2: Raw Snapshot

For debugging and learning, each scraper run should be able to save a snapshot.

Snapshot examples:
- raw HTML or JSON
- page title
- source URL
- timestamp
- scraper status
- error message if failed

Snapshots help the Scraper Agent review failures later.

## Step 3: Parser

The parser converts raw content into structured records.

General parser outputs should include:
- source
- event or market name
- category
- market type
- selection or outcome
- odds, price, or probability
- event time or market close time if available
- extraction confidence

Polymarket parser outputs should eventually include richer market fields:
- volume
- liquidity
- market status
- tags
- description
- related markets
- historical movement when available

## Step 4: Database

PostgreSQL stores cleaned records and run history.

Initial tables will likely include:
- scraper_runs
- sources
- events
- markets
- odds_snapshots
- market_snapshots
- betting_signals

The `market_snapshots` concept is especially important for Polymarket because prices, probabilities, volume, and liquidity can change over time.

## Step 5: Prediction and Market Intelligence Engine

The first betting prediction engine should be simple and explainable.

Example logic:
- convert odds into implied probability
- compare source confidence and market indicators
- calculate an edge score
- assign Gold, Silver, or Bronze

For Polymarket, the system should also support market-intelligence analysis:
- trending markets
- unusual volume changes
- sentiment shifts
- event-risk summaries
- finance or stock-market-related themes

## Step 6: Decision Agent

The Decision Agent should only reason over structured records and scoring output.

It should explain:
- why a signal exists
- what risks are present
- whether confidence is strong or weak
- what data might be missing
- what markets or themes deserve attention

## Step 7: Delivery

Signals and summaries are delivered through:
- Streamlit dashboard
- Telegram bot

The dashboard comes first because it helps us debug, learn, and inspect rich scraped data.
