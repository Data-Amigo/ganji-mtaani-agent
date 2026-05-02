from dataclasses import dataclass


# =============================================================================
# Mozzart Football Odds Model
# =============================================================================
# This model stores the stable football fields we currently understand from the
# Mozzart live football page. It captures the live state shown on the page as
# well as the current 1/X/2 odds when those odds are available.
@dataclass(slots=True)
class MozzartFootballOdds:
    """Structured live football odds row extracted from Mozzart."""

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


# =============================================================================
# Mozzart Basketball Odds Model
# =============================================================================
# This model stores the stable basketball fields we currently understand from
# the Mozzart live basketball page. It preserves the live state, visible score
# text, extra markets, and the currently displayed winner-style odds.
@dataclass(slots=True)
class MozzartBasketballOdds:
    """Structured live basketball odds row extracted from Mozzart."""

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
