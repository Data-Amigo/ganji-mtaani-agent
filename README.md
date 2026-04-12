# gAnji Mtaani Agent

`gAnji Mtaani Agent` is the production build of project gAnji.

The old POC remains a learning/reference project. This repo is the clean production system.

## Product Goal

Build a scraper-first betting and market-intelligence platform with two agent layers:

1. Scraper Agent: assists with extraction quality, selector recovery, and scraping review.
2. Decision Agent: reasons over structured data and produces explainable signals.

## Core Build Order

1. Project setup and documentation
2. Scraper engine with Streamlit UI
3. Parsing and data normalization
4. PostgreSQL storage
5. Prediction engine
6. Telegram and dashboard delivery
7. Scraper Agent and Decision Agent
8. Production hardening

## Key Docs

- `docs/architecture/project-overview.md`
- `docs/architecture/folder-guide.md`
- `docs/architecture/data-flow.md`
- `docs/architecture/architecture-decisions.md`
- `docs/architecture/scraper-ui-design.md`
- `docs/roadmap/daily-2-hour-plan.md`
- `docs/roadmap/production-timeline.md`
- `docs/operations/working-rules.md`

## Current Milestone

We are finalizing the scraper UI design before implementation. The next implementation milestone is the first Streamlit scraper console and the first Forebet scraper flow.
