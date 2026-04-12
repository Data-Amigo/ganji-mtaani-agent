# Folder Guide

## docs

Architecture, roadmap, project decisions, and operating notes.

## scripts

Small setup, maintenance, and developer helper scripts.

## src/ganji_mtaani_agent/agents/scraper_agent

Agent workflows that help inspect failed scrapes, suggest selector repairs, and score extraction confidence.

## src/ganji_mtaani_agent/agents/decision_agent

Agent workflows that reason over structured data and produce explanations for betting signals.

## src/ganji_mtaani_agent/scrapers

Source-specific browser or API scraping logic.

## src/ganji_mtaani_agent/parsers

HTML or JSON parsing and normalization logic.

## src/ganji_mtaani_agent/db

Database connection, schema, repositories, and migrations later.

## src/ganji_mtaani_agent/models

Domain models such as events, markets, odds snapshots, predictions, and signals.

## src/ganji_mtaani_agent/prediction

Scoring, ranking, tiering, and eventually model-based prediction logic.

## src/ganji_mtaani_agent/services

External services such as OpenAI, Telegram, scheduler, and notifications.

## src/ganji_mtaani_agent/dashboard

Streamlit UI for scraper operation, dashboard review, and signal inspection.

## src/ganji_mtaani_agent/pipelines

End-to-end workflows such as scrape -> parse -> store -> score -> publish.

## tests

Unit, integration, and scraper tests.
