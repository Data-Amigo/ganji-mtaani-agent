from dataclasses import dataclass


# =============================================================================
# Forebet Basketball Prediction Model
# =============================================================================
# This model stores the stable fields we currently understand from a Forebet
# basketball row. Anything beyond the stable core is kept in remaining_tokens
# until we fully understand the live/finished game structure.
@dataclass(slots=True)
class ForebetBasketballPrediction:
    """Structured basketball prediction row extracted from Forebet.

    Attributes:
        source: Source name. For this parser it will be "forebet".
        sport: Sport name. For this parser it will be "basketball".
        league: League code or competition label, for example "NBA".
        home_team: Home team name.
        away_team: Away team name.
        event_datetime: Date and time string as seen in the snapshot.
        prob_1: First probability column, likely home-win probability.
        prob_2: Second probability column, likely away-win probability.
        pred_outcome: Predicted outcome marker, usually "1" or "2".
        predicted_home_score: Predicted home team score.
        predicted_away_score: Predicted away team score.
        avg_points: Average total points value.
        coef_1: First coefficient-style value.
        coef_2: Second coefficient-style value.
        coef_3: Third coefficient-style value.
        remaining_tokens: Tokens after the stable core. We keep these for later
            live-score and quarter parsing.
        raw_text: Original row text before structured parsing.
        confidence: Extraction confidence score for the row.
    """

    source: str
    sport: str
    league: str
    home_team: str
    away_team: str
    event_datetime: str
    prob_1: int | None
    prob_2: int | None
    pred_outcome: str | None
    predicted_home_score: int | None
    predicted_away_score: int | None
    avg_points: float | None
    coef_1: float | None
    coef_2: float | None
    coef_3: float | None
    remaining_tokens: list[str]
    raw_text: str
    confidence: float
