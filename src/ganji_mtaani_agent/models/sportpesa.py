from dataclasses import dataclass


# =============================================================================
# SportPesa Football Odds Model
# =============================================================================
# This model stores the stable football odds fields we currently understand from
# the live SportPesa football page. It focuses on the main displayed fixtures,
# their identity, and the first four visible betting market groups.
@dataclass(slots=True)
class SportPesaFootballOdds:
    """Structured football odds row extracted from SportPesa.

    Attributes:
        source: Source name. For this parser it will be "sportpesa".
        sport: Sport name. For this parser it will be "football".
        league: League or competition label.
        event_datetime: Date and time string shown on the page.
        game_id: SportPesa internal game identifier from the visible row.
        home_team: Home team name.
        away_team: Away team name.
        home_odds: 3-way home win odds.
        draw_odds: 3-way draw odds.
        away_odds: 3-way away win odds.
        home_or_draw_odds: Double-chance 1 or X odds.
        draw_or_away_odds: Double-chance X or 2 odds.
        home_or_away_odds: Double-chance 1 or 2 odds.
        over_2_5_odds: Over 2.5 goals odds.
        under_2_5_odds: Under 2.5 goals odds.
        btts_yes_odds: Both teams to score yes odds.
        btts_no_odds: Both teams to score no odds.
        game_url: SportPesa game markets URL when available.
        raw_text: Original row text before structured parsing.
        confidence: Extraction confidence score for the row.
    """

    source: str
    sport: str
    league: str
    event_datetime: str
    game_id: str
    home_team: str
    away_team: str
    home_odds: float | None
    draw_odds: float | None
    away_odds: float | None
    home_or_draw_odds: float | None
    draw_or_away_odds: float | None
    home_or_away_odds: float | None
    over_2_5_odds: float | None
    under_2_5_odds: float | None
    btts_yes_odds: float | None
    btts_no_odds: float | None
    game_url: str | None
    raw_text: str
    confidence: float


# =============================================================================
# SportPesa Basketball Odds Model
# =============================================================================
# This model stores the stable basketball odds fields we currently understand
# from the live SportPesa basketball page. Basketball is simpler than football
# for V1 because the visible page is centered around the 2-way market including
# overtime.
@dataclass(slots=True)
class SportPesaBasketballOdds:
    """Structured basketball odds row extracted from SportPesa.

    Attributes:
        source: Source name. For this parser it will be "sportpesa".
        sport: Sport name. For this parser it will be "basketball".
        league: League or competition label.
        event_datetime: Date and time string shown on the page.
        game_id: SportPesa internal game identifier from the visible row.
        home_team: Home team name.
        away_team: Away team name.
        home_odds: 2-way home win odds including overtime.
        away_odds: 2-way away win odds including overtime.
        game_url: SportPesa game markets URL when available.
        raw_text: Original row text before structured parsing.
        confidence: Extraction confidence score for the row.
    """

    source: str
    sport: str
    league: str
    event_datetime: str
    game_id: str
    home_team: str
    away_team: str
    home_odds: float | None
    away_odds: float | None
    game_url: str | None
    raw_text: str
    confidence: float
