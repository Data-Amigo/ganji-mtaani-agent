-- =============================================================================
-- gAnji Mtaani Phase 1 PostgreSQL Schema
-- =============================================================================
-- This schema creates the first three foundation tables for the platform:
-- 1. source_runs       -> ingestion/audit tracking
-- 2. bookmaker_odds    -> shared bookmaker odds storage
-- 3. sports_results    -> ground-truth event results from TheSportsDB
--
-- The goal is to create a practical, query-friendly starting point before we
-- add the rest of the prediction, stats, lineup, and player tables.

-- =============================================================================
-- Source Runs Table
-- =============================================================================
CREATE TABLE IF NOT EXISTS source_runs (
    id BIGSERIAL PRIMARY KEY,
    source_name TEXT NOT NULL,
    target_name TEXT,
    source_type TEXT NOT NULL,
    status TEXT NOT NULL,
    started_at TIMESTAMPTZ NOT NULL,
    finished_at TIMESTAMPTZ,
    duration_ms INTEGER,
    records_found INTEGER,
    warnings_count INTEGER DEFAULT 0,
    error_message TEXT,
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_source_runs_source_name
    ON source_runs (source_name);

CREATE INDEX IF NOT EXISTS idx_source_runs_started_at
    ON source_runs (started_at DESC);


-- =============================================================================
-- Bookmaker Odds Table
-- =============================================================================
CREATE TABLE IF NOT EXISTS bookmaker_odds (
    id BIGSERIAL PRIMARY KEY,
    run_id BIGINT REFERENCES source_runs(id) ON DELETE SET NULL,
    source_name TEXT NOT NULL,
    sport TEXT NOT NULL,
    league TEXT,
    event_datetime_text TEXT,
    event_datetime_utc TIMESTAMPTZ,
    home_team TEXT NOT NULL,
    away_team TEXT NOT NULL,
    game_id TEXT,
    match_status TEXT,
    score_text TEXT,
    market_type TEXT,
    home_odds DOUBLE PRECISION,
    draw_odds DOUBLE PRECISION,
    away_odds DOUBLE PRECISION,
    home_or_draw_odds DOUBLE PRECISION,
    draw_or_away_odds DOUBLE PRECISION,
    home_or_away_odds DOUBLE PRECISION,
    over_2_5_odds DOUBLE PRECISION,
    under_2_5_odds DOUBLE PRECISION,
    btts_yes_odds DOUBLE PRECISION,
    btts_no_odds DOUBLE PRECISION,
    extra_market_count INTEGER,
    raw_text TEXT,
    confidence DOUBLE PRECISION NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_bookmaker_odds_source_name
    ON bookmaker_odds (source_name);

CREATE INDEX IF NOT EXISTS idx_bookmaker_odds_sport
    ON bookmaker_odds (sport);

CREATE INDEX IF NOT EXISTS idx_bookmaker_odds_run_id
    ON bookmaker_odds (run_id);

CREATE INDEX IF NOT EXISTS idx_bookmaker_odds_event_datetime_text
    ON bookmaker_odds (event_datetime_text);

CREATE INDEX IF NOT EXISTS idx_bookmaker_odds_teams
    ON bookmaker_odds (home_team, away_team);


-- =============================================================================
-- Sports Results Table
-- =============================================================================
CREATE TABLE IF NOT EXISTS sports_results (
    id BIGSERIAL PRIMARY KEY,
    run_id BIGINT REFERENCES source_runs(id) ON DELETE SET NULL,
    source_name TEXT NOT NULL,
    sport TEXT,
    event_id TEXT NOT NULL,
    league_id TEXT,
    league TEXT,
    season TEXT,
    event_name TEXT,
    event_date DATE,
    event_time TEXT,
    event_datetime_utc TIMESTAMPTZ,
    home_team_id TEXT,
    away_team_id TEXT,
    home_team TEXT,
    away_team TEXT,
    home_score INTEGER,
    away_score INTEGER,
    status TEXT,
    progress TEXT,
    venue TEXT,
    winner TEXT,
    raw_record_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    confidence DOUBLE PRECISION NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_sports_results_source_event UNIQUE (source_name, event_id)
);

CREATE INDEX IF NOT EXISTS idx_sports_results_sport
    ON sports_results (sport);

CREATE INDEX IF NOT EXISTS idx_sports_results_event_date
    ON sports_results (event_date);

CREATE INDEX IF NOT EXISTS idx_sports_results_run_id
    ON sports_results (run_id);

CREATE INDEX IF NOT EXISTS idx_sports_results_teams
    ON sports_results (home_team, away_team);
