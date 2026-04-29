"""This is the forebet.py parser file.

Author: Data-Amigo
Date: 2026-04-29
Description:
This parser module extracts the first stable basketball prediction fields from a
saved Forebet HTML snapshot. It intentionally focuses on the stable core fields
first and stores the rest of the row in remaining_tokens for later refinement.
"""

from __future__ import annotations

from dataclasses import dataclass

from bs4 import BeautifulSoup

from ganji_mtaani_agent.models.forebet import ForebetBasketballPrediction


# =============================================================================
# Basketball Row Parsing Constants
# =============================================================================
# These positions represent the stable part of the Forebet basketball row that
# we have already inspected manually from the saved snapshot.
LEAGUE_INDEX = 0
HOME_TEAM_INDEX = 1
AWAY_TEAM_INDEX = 2
EVENT_DATETIME_INDEX = 3
PROB_1_INDEX = 4
PROB_2_INDEX = 5
PRED_OUTCOME_INDEX = 6
PREDICTED_HOME_SCORE_INDEX = 7
DASH_SEPARATOR_INDEX = 8
PREDICTED_AWAY_SCORE_INDEX = 9
AVG_POINTS_INDEX = 12
COEF_1_INDEX = 13
COEF_2_INDEX = 14
COEF_3_INDEX = 15
MINIMUM_EXPECTED_TOKENS = 16


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
# Row Tokenizer
# =============================================================================
# Each basketball row is a div.rcnt block. We flatten its text into tokens using
# a pipe separator so the parser can map fixed positions reliably.
def tokenize_basketball_row_text(row_text: str) -> list[str]:
    """Split one Forebet basketball row into cleaned text tokens."""

    return [token.strip() for token in row_text.split("|") if token.strip()]


# =============================================================================
# Single Row Parser
# =============================================================================
# This function parses only the stable row core that we understand today.
# It ignores the dash token and stores everything after the stable core in
# remaining_tokens for later work.
def parse_basketball_row(row_text: str) -> ForebetBasketballPrediction | None:
    """Parse one flattened Forebet basketball row into a model object.

    Args:
        row_text: One row of flattened text from a div.rcnt element.

    Returns:
        ForebetBasketballPrediction when parsing succeeds, otherwise None.
    """

    tokens = tokenize_basketball_row_text(row_text)
    if len(tokens) < MINIMUM_EXPECTED_TOKENS:
        return None

    # The dash token is only a visual score separator, so we skip it logically.
    if tokens[DASH_SEPARATOR_INDEX] != "-":
        confidence = 0.75
    else:
        confidence = 1.0

    return ForebetBasketballPrediction(
        source="forebet",
        sport="basketball",
        league=tokens[LEAGUE_INDEX],
        home_team=tokens[HOME_TEAM_INDEX],
        away_team=tokens[AWAY_TEAM_INDEX],
        event_datetime=tokens[EVENT_DATETIME_INDEX],
        prob_1=_to_int(tokens[PROB_1_INDEX]),
        prob_2=_to_int(tokens[PROB_2_INDEX]),
        pred_outcome=tokens[PRED_OUTCOME_INDEX],
        predicted_home_score=_to_int(tokens[PREDICTED_HOME_SCORE_INDEX]),
        predicted_away_score=_to_int(tokens[PREDICTED_AWAY_SCORE_INDEX]),
        avg_points=_to_float(tokens[AVG_POINTS_INDEX]),
        coef_1=_to_float(tokens[COEF_1_INDEX]),
        coef_2=_to_float(tokens[COEF_2_INDEX]),
        coef_3=_to_float(tokens[COEF_3_INDEX]),
        remaining_tokens=tokens[16:],
        raw_text=row_text,
        confidence=confidence,
    )


# =============================================================================
# Snapshot Parser
# =============================================================================
# This helper reads the real basketball container from the HTML and parses all
# repeated div.rcnt blocks into structured prediction objects.
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
