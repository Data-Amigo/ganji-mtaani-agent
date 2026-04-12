# Project Overview

## Product Name

gAnji Mtaani

## Repository Name

ganji-mtaani-agent

## Product Goal

Build a scraper-first betting intelligence platform that collects betting and market data, stores it cleanly, generates explainable signals, and uses agents to improve scraping and decision support.

## Main Systems

- Scraper Engine: deterministic website fetching and extraction.
- Scraper UI: Streamlit interface to run and inspect scraping.
- Scraper Agent: reviews failures, suggests selector fixes, and supports extraction validation.
- Data Layer: PostgreSQL storage for historical observations and pipeline runs.
- Prediction Engine: explainable scoring and tiering.
- Decision Agent: reasoning layer for signals, risk, and user-facing explanations.
- Delivery Layer: dashboard and Telegram publishing.

## Build Principle

The scraper must work first. Agents improve the workflow, but they should not replace reliable parsing, validation, and storage.
