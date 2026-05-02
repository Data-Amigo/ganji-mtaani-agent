from dataclasses import dataclass


# =============================================================================
# Betika Football Odds Model
# =============================================================================
# This model stores the stable football odds fields we currently understand from
# the rendered Betika football page text. The first parser version focuses on
# league identity, kickoff text, 1/X/2 odds, and the extra market count.
@dataclass(slots=True)
class BetikaFootballOdds:
    """Structured football odds row extracted from Betika.

    Attributes:
        source: Source name. For this parser it will be "betika".
        sport: Sport name. For this parser it will be "football".
        league: League or competition label.
        event_datetime_text: Start text shown by Betika, such as
            "Starts today at 5:00 PM".
        home_team: Home team name.
        away_team: Away team name.
        home_odds: 1x2 home win odds.
        draw_odds: 1x2 draw odds.
        away_odds: 1x2 away win odds.
        extra_market_count: Additional market count shown as values like "+85".
        raw_text: Original match block text before structured parsing.
        confidence: Extraction confidence score for the row.
    """

    source: str
    sport: str
    league: str
    event_datetime_text: str
    home_team: str
    away_team: str
    home_odds: float | None
    draw_odds: float | None
    away_odds: float | None
    extra_market_count: int | None
    raw_text: str
    confidence: float


# =============================================================================
# Betika Basketball Odds Model
# =============================================================================
# This model stores the stable basketball odds fields we currently understand
# from the rendered Betika basketball page text. The current Betika basketball
# page still exposes three winner-style odds in its visible row blocks, so the
# V1 model preserves those values as shown on the page.
@dataclass(slots=True)
class BetikaBasketballOdds:
    """Structured basketball odds row extracted from Betika.

    Attributes:
        source: Source name. For this parser it will be "betika".
        sport: Sport name. For this parser it will be "basketball".
        league: League or competition label.
        event_datetime_text: Start text shown by Betika.
        home_team: Home team name.
        away_team: Away team name.
        home_odds: First visible winner-style odds value.
        draw_odds: Second visible winner-style odds value.
        away_odds: Third visible winner-style odds value.
        extra_market_count: Additional market count shown as values like "+39".
        raw_text: Original match block text before structured parsing.
        confidence: Extraction confidence score for the row.
    """

    source: str
    sport: str
    league: str
    event_datetime_text: str
    home_team: str
    away_team: str
    home_odds: float | None
    draw_odds: float | None
    away_odds: float | None
    extra_market_count: int | None
    raw_text: str
    confidence: float
