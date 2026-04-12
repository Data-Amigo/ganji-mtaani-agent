# Scraper UI Design

This document defines the first Streamlit scraper interface for gAnji Mtaani.

## Purpose

The Scraper UI is the control room for the scraping system.

It should help us:
- choose a source
- run a scraper manually
- inspect scraper status
- preview extracted data
- inspect raw content
- review warnings and errors
- later trigger Scraper Agent review

The first UI is mainly for development, debugging, and learning. Later it can become an operations dashboard.

## V1 Goal

The first version should prove this loop:

```text
User selects source
  -> user clicks Run Scraper
  -> scraper fetches page data
  -> parser extracts structured records
  -> UI displays results
```

V1 should not depend on PostgreSQL or agents yet. It should make the scraper visible and testable first.

## V1 Layout

```text
gAnji Mtaani Scraper Console

Sidebar
  - Source selector
  - Target URL
  - Save snapshot checkbox
  - Run scraper button

Main page
  - Run status panel
  - Extracted data preview
  - Raw content preview
  - Warnings and errors
  - Future Scraper Agent panel placeholder
```

## Sidebar Controls

### Source

Initial options:
- Forebet
- Polymarket

Forebet is the first source for proving the betting workflow.

Polymarket is a strategic market-intelligence source and should eventually receive deeper extraction.

### Target URL

The target URL should be prefilled based on the selected source but remain editable.

This allows us to test different pages without changing code.

### Save Snapshot

When enabled, the scraper should save raw HTML or JSON output for debugging.

Snapshots are important because they help us inspect failures and later support the Scraper Agent.

### Run Scraper

Starts the scraper flow.

For V1, this runs manually only.

## Run Status Panel

The UI should show the current state of the scrape.

Suggested statuses:
- idle
- running
- success
- partial_success
- failed

Each run should display:
- source
- target URL
- started time
- finished time
- duration
- records extracted
- warning count
- error message if failed
- snapshot path if saved

## Extracted Data Preview

This is the most important section of the scraper UI.

The output should be shown as a table.

### Forebet Preview Fields

Initial fields:
- source
- league
- home_team
- away_team
- prediction
- odds
- probability
- event_time
- confidence
- raw_text

### Polymarket Preview Fields

Polymarket should be designed as a richer market-intelligence dataset.

Initial fields:
- source
- market_title
- category
- description
- outcome
- price
- probability
- volume
- liquidity
- status
- end_date
- tags
- confidence

Future Polymarket fields:
- related_markets
- historical_price_change
- volume_change
- market_url
- event_risk_theme

## Raw Content Preview

The raw preview helps debug whether the scraper actually collected the expected page.

It should show:
- page title if available
- raw content length
- first 1,000 to 2,000 characters
- snapshot path if saved

This section should be inside an expandable panel to avoid clutter.

## Warnings and Errors

The UI should display parser and scraper issues clearly.

Examples:
- no market rows found
- missing odds field
- missing probability field
- could not parse event time
- low extraction confidence
- page loaded but content appears empty
- possible anti-bot or block page detected

## Future Scraper Agent Panel

This panel should not be fully implemented in V1, but the UI should reserve space for it.

Future output examples:
- likely issue
- failed field
- suggested selector repair
- confidence score
- recommended next action

Example:

```text
Scraper Agent Review
Likely issue: selector mismatch
Failed field: market_title
Suggested action: inspect market card selector
Confidence: 0.72
Recommended next step: save snapshot and review parser
```

## Future Auto-Refresh

Auto-refresh is useful for dashboards, but it should not directly trigger scraper runs in V1.

Better production design:

```text
Scheduler
  -> Scraper Pipeline
  -> PostgreSQL
  -> Streamlit reads latest data from DB
  -> Streamlit auto-refreshes display
```

Avoid this design:

```text
Streamlit auto-refresh
  -> directly runs scraper every refresh
```

Reason:
A UI refresh could accidentally trigger too many scraper runs.

## Future Scheduling

Scheduled scraping should be added after manual scraping and database storage work.

Possible schedule strategy:
- Forebet: run before important match windows or every few hours
- Polymarket: run more frequently because market prices, volume, and liquidity change often

Possible scheduler options:
- APScheduler for simple local scheduling
- GitHub Actions cron for lightweight scheduled jobs
- server cron for VPS deployment
- Celery and Redis for heavier production workloads

Recommended first scheduler:
APScheduler, after PostgreSQL is integrated.

## V1 Acceptance Criteria

V1 is complete when:
- user can select Forebet or Polymarket
- user can edit the target URL
- user can run the scraper manually
- UI displays status clearly
- UI displays extracted rows in a table
- UI displays raw preview
- UI displays warnings and errors
- UI includes a placeholder for future Scraper Agent review
