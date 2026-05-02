from dataclasses import dataclass


# =============================================================================
# Mozzart Football Odds Model
# =============================================================================
# This model stores the stable football fields we currently understand from the
# Mozzart live football page. It captures the live state shown on the page as
# well as the current 1/X/2 odds when those odds are available.
@dataclass(slots=True)
class MozzartFootballOdds:
    """Structured live football odds row extracted from Mozzart.

    Attributes:
        source: Source name. For this parser it will be "mozzart".
        sport: Sport name. For this parser it will be "football".
        league: League or competition label, such as "England 1".
        match_status: Live status text assembled from the status tokens,
            such as "R H 48:37" or "R H HT".
        home_team: Home team name.
        away_team: Away team name.
        score_text: Visible live score state text, such as "2 0 0 0".
        extra_market_count: Additional market count shown as values like "+224".
        home_odds: Home win odds when available.
        draw_odds: Draw odds when available.
        away_odds: Away win odds when available.
        raw_text: Original row text before structured parsing.
        confidence: Extraction confidence score for the row.
    """

    source: str
    sport: str
    league: str
    match_status: str
    home_team: str
    away_team: str
    score_text: str
    extra_market_count: int | None
    home_odds: float | None
    draw_odds: float | None
    away_odds: float | None
    raw_text: str
    confidence: float
