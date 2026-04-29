"""This is the forebet.py parser file.

Author: Data-Amigo
Date: 2026-04-29
Description:
This parser module extracts the first stable basketball and football prediction
fields from saved Forebet HTML snapshots. It intentionally focuses on the stable
core fields first and stores the rest of the row in remaining_tokens for later
refinement.
"""

from __future__ import annotations

from bs4 import BeautifulSoup

from ganji_mtaani_agent.models.forebet import (
    ForebetBasketballPrediction,
    ForebetFootballPrediction,
)


# =============================================================================
# Basketball Row Parsing Constants
# =============================================================================
# These positions represent the stable part of the Forebet basketball row that
# we have already inspected manually from the saved snapshot.
BASKETBALL_LEAGUE_INDEX = 0
BASKETBALL_HOME_TEAM_INDEX = 1
BASKETBALL_AWAY_TEAM_INDEX = 2
BASKETBALL_EVENT_DATETIME_INDEX = 3
BASKETBALL_PROB_1_INDEX = 4
BASKETBALL_PROB_2_INDEX = 5
BASKETBALL_PRED_OUTCOME_INDEX = 6
BASKETBALL_PREDICTED_HOME_SCORE_INDEX = 7
BASKETBALL_DASH_SEPARATOR_INDEX = 8
BASKETBALL_PREDICTED_AWAY_SCORE_INDEX = 9
BASKETBALL_AVG_POINTS_INDEX = 12
BASKETBALL_COEF_1_INDEX = 13
BASKETBALL_COEF_2_INDEX = 14
BASKETBALL_COEF_3_INDEX = 15
BASKETBALL_MINIMUM_EXPECTED_TOKENS = 16


# =============================================================================
# Football Row Parsing Constants
# =============================================================================
# These positions represent the stable part of the Forebet football row that we
# inspected manually from the saved football snapshot.
FOOTBALL_LEAGUE_INDEX = 0
FOOTBALL_HOME_TEAM_INDEX = 1
FOOTBALL_AWAY_TEAM_INDEX = 2
FOOTBALL_EVENT_DATETIME_INDEX = 3
FOOTBALL_PROB_1_INDEX = 4
FOOTBALL_PROB_X_INDEX = 5
FOOTBALL_PROB_2_INDEX = 6
FOOTBALL_PRED_OUTCOME_INDEX = 7
FOOTBALL_PREDICTED_HOME_SCORE_INDEX = 8
FOOTBALL_DASH_SEPARATOR_INDEX = 9
FOOTBALL_PREDICTED_AWAY_SCORE_INDEX = 10
FOOTBALL_CORRECT_SCORE_TEXT_INDEX = 11
FOOTBALL_AVG_GOALS_INDEX = 12
FOOTBALL_WEATHER_INDEX = 13
FOOTBALL_COEF_1_INDEX = 14
FOOTBALL_COEF_X_INDEX = 15
FOOTBALL_COEF_2_INDEX = 16
FOOTBALL_COEF_EXTRA_INDEX = 17
FOOTBALL_MINIMUM_EXPECTED_TOKENS = 18


# =============================================================================
# Small Conversion Helpers
# =============================================================================
# These helpers keep the row parser readable and protect it from bad values.
def _to_int(value: str) -> int | None:
    """Convert a token to int when possible."""

    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _to_float(value: str) -> float | None:
    """Convert a token to float when possible."""

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


# =============================================================================
# Row Tokenizers
# =============================================================================
# Each Forebet row is flattened into pipe-separated text before structured parsing.
def tokenize_basketball_row_text(row_text: str) -> list[str]:
    """Split one Forebet basketball row into cleaned text tokens."""

    return [token.strip() for token in row_text.split("|") if token.strip()]


def tokenize_football_row_text(row_text: str) -> list[str]:
    """Split one Forebet football row into cleaned text tokens."""

    return [token.strip() for token in row_text.split("|") if token.strip()]


# =============================================================================
# Single Basketball Row Parser
# =============================================================================
# This function parses only the stable basketball row core that we understand today.
# It ignores the dash token and stores everything after the stable core in
# remaining_tokens for later work.
def parse_basketball_row(row_text: str) -> ForebetBasketballPrediction | None:
    """Parse one flattened Forebet basketball row into a model object."""

    tokens = tokenize_basketball_row_text(row_text)
    if len(tokens) < BASKETBALL_MINIMUM_EXPECTED_TOKENS:
        return None

    if tokens[BASKETBALL_DASH_SEPARATOR_INDEX] != "-":
        confidence = 0.75
    else:
        confidence = 1.0

    return ForebetBasketballPrediction(
        source="forebet",
        sport="basketball",
        league=tokens[BASKETBALL_LEAGUE_INDEX],
        home_team=tokens[BASKETBALL_HOME_TEAM_INDEX],
        away_team=tokens[BASKETBALL_AWAY_TEAM_INDEX],
        event_datetime=tokens[BASKETBALL_EVENT_DATETIME_INDEX],
        prob_1=_to_int(tokens[BASKETBALL_PROB_1_INDEX]),
        prob_2=_to_int(tokens[BASKETBALL_PROB_2_INDEX]),
        pred_outcome=tokens[BASKETBALL_PRED_OUTCOME_INDEX],
        predicted_home_score=_to_int(tokens[BASKETBALL_PREDICTED_HOME_SCORE_INDEX]),
        predicted_away_score=_to_int(tokens[BASKETBALL_PREDICTED_AWAY_SCORE_INDEX]),
        avg_points=_to_float(tokens[BASKETBALL_AVG_POINTS_INDEX]),
        coef_1=_to_float(tokens[BASKETBALL_COEF_1_INDEX]),
        coef_2=_to_float(tokens[BASKETBALL_COEF_2_INDEX]),
        coef_3=_to_float(tokens[BASKETBALL_COEF_3_INDEX]),
        remaining_tokens=tokens[16:],
        raw_text=row_text,
        confidence=confidence,
    )


# =============================================================================
# Single Football Row Parser
# =============================================================================
# This function parses only the stable football row core that we understand today.
# It keeps the uncertain live-state and extra values in remaining_tokens.
def parse_football_row(row_text: str) -> ForebetFootballPrediction | None:
    """Parse one flattened Forebet football row into a model object."""

    tokens = tokenize_football_row_text(row_text)
    if len(tokens) < FOOTBALL_MINIMUM_EXPECTED_TOKENS:
        return None

    if tokens[FOOTBALL_DASH_SEPARATOR_INDEX] != "-":
        confidence = 0.75
    else:
        confidence = 1.0

    return ForebetFootballPrediction(
        source="forebet",
        sport="football",
        league=tokens[FOOTBALL_LEAGUE_INDEX],
        home_team=tokens[FOOTBALL_HOME_TEAM_INDEX],
        away_team=tokens[FOOTBALL_AWAY_TEAM_INDEX],
        event_datetime=tokens[FOOTBALL_EVENT_DATETIME_INDEX],
        prob_1=_to_int(tokens[FOOTBALL_PROB_1_INDEX]),
        prob_x=_to_int(tokens[FOOTBALL_PROB_X_INDEX]),
        prob_2=_to_int(tokens[FOOTBALL_PROB_2_INDEX]),
        pred_outcome=tokens[FOOTBALL_PRED_OUTCOME_INDEX],
        predicted_home_score=_to_int(tokens[FOOTBALL_PREDICTED_HOME_SCORE_INDEX]),
        predicted_away_score=_to_int(tokens[FOOTBALL_PREDICTED_AWAY_SCORE_INDEX]),
        correct_score_text=tokens[FOOTBALL_CORRECT_SCORE_TEXT_INDEX],
        avg_goals=_to_float(tokens[FOOTBALL_AVG_GOALS_INDEX]),
        weather=tokens[FOOTBALL_WEATHER_INDEX],
        coef_1=_to_float(tokens[FOOTBALL_COEF_1_INDEX]),
        coef_x=_to_float(tokens[FOOTBALL_COEF_X_INDEX]),
        coef_2=_to_float(tokens[FOOTBALL_COEF_2_INDEX]),
        coef_extra=_to_float(tokens[FOOTBALL_COEF_EXTRA_INDEX]),
        remaining_tokens=tokens[18:],
        raw_text=row_text,
        confidence=confidence,
    )


# =============================================================================
# Basketball Snapshot Parser
# =============================================================================
def parse_forebet_basketball(html: str) -> list[ForebetBasketballPrediction]:
    """Parse Forebet basketball predictions from a saved HTML snapshot."""

    soup = BeautifulSoup(html, "html.parser")
    container = soup.select_one("div.schema.tbuo.tbbsk")
    if container is None:
        return []

    predictions: list[ForebetBasketballPrediction] = []

    for row in container.select("div.rcnt"):
        row_text = row.get_text(" | ", strip=True)
        parsed = parse_basketball_row(row_text)
        if parsed is not None:
            predictions.append(parsed)

    return predictions


# =============================================================================
# Football Snapshot Parser
# =============================================================================
def parse_forebet_football(html: str) -> list[ForebetFootballPrediction]:
    """Parse Forebet football predictions from a saved HTML snapshot."""

    soup = BeautifulSoup(html, "html.parser")
    rows = soup.select("div.rcnt")
    if not rows:
        return []

    predictions: list[ForebetFootballPrediction] = []

    for row in rows:
        row_text = row.get_text(" | ", strip=True)
        parsed = parse_football_row(row_text)
        if parsed is not None:
            predictions.append(parsed)

    return predictions
