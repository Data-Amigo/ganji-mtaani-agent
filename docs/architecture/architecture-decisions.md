# Architecture Decisions

This document records important decisions so we can remember why the system is built this way.

## ADR 001: Build Scraper First

Decision:
The first major system will be the scraper engine and scraper UI.

Reason:
The whole product depends on reliable source data. If scraping is unstable, prediction and agents will not be trustworthy.

Consequence:
Prediction and advanced agent features are delayed until at least one source can be scraped and parsed repeatedly.

## ADR 002: Keep Scraping and Parsing Separate

Decision:
Scrapers fetch raw content. Parsers convert raw content into structured data.

Reason:
This makes failures easier to debug. A scraper can succeed while a parser fails, and vice versa.

Consequence:
Each source should have both scraper logic and parser logic.

## ADR 003: Use Streamlit Early

Decision:
Build a Streamlit scraper UI early in the project.

Reason:
The UI will help inspect raw outputs, extracted rows, errors, and confidence. It also makes the scraper feel like a real product module.

Consequence:
The dashboard starts as an internal operations tool before becoming a user-facing analytics product.

## ADR 004: Agents Assist, They Do Not Replace Core Logic

Decision:
Agents will support scraper recovery and decision explanations, but deterministic code remains responsible for fetching, parsing, storing, and scoring.

Reason:
Deterministic logic is easier to test, debug, and trust.

Consequence:
Agent outputs should be reviewed or constrained before changing production behavior.

## ADR 005: Forebet First, Polymarket Deep Second

Decision:
Forebet is the first source for proving the end-to-end betting prediction flow. Polymarket is the second major source, but it should receive deeper extraction because it has broader long-term value.

Reason:
Forebet aligns directly with the original football betting prediction idea and is useful for building the first pipeline. Polymarket contains rich prediction-market data that can support traders, researchers, and future analytics products beyond this first betting use case.

Consequence:
The first MVP focuses on one end-to-end Forebet flow, but the architecture must not treat Polymarket as an afterthought. The database and parsers should be designed to support rich market snapshots and historical analysis.
