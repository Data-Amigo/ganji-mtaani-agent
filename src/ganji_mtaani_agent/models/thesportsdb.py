from dataclasses import dataclass
from typing import Any


# =============================================================================
# TheSportsDB Event Result Model
# =============================================================================
# This model stores the core ground-truth event result fields we need for the
# first evaluation phase of the project. It is the main bridge between scraped
# predictions/odds and actual completed outcomes.
@dataclass(slots=True)
class TheSportsDBEventResult:
    """Structured event result record normalized from TheSportsDB.

    Attributes:
        source: Source name. For this model it will be "thesportsdb".
        sport: Sport name such as "Soccer" or "Basketball".
        event_id: TheSportsDB unique event identifier.
        league_id: TheSportsDB unique league identifier.
        league: League or competition name.
        season: Season label when available.
        event_name: Human-readable event name.
        event_date: Scheduled or recorded event date.
        event_time: Scheduled or recorded event start time.
        home_team_id: TheSportsDB home team identifier.
        away_team_id: TheSportsDB away team identifier.
        home_team: Home team name.
        away_team: Away team name.
        home_score: Final or current home score when available.
        away_score: Final or current away score when available.
        status: Event status code or text such as NS, FT, Q1, or HT.
        progress: Human-readable progress text when available.
        venue: Venue or stadium name when available.
        winner: Derived winner label such as "home", "away", "draw", or None.
        raw_record: Original API payload for debugging and future enrichment.
        confidence: Normalization confidence score for this record.
    """

    source: str
    sport: str | None
    event_id: str
    league_id: str | None
    league: str | None
    season: str | None
    event_name: str | None
    event_date: str | None
    event_time: str | None
    home_team_id: str | None
    away_team_id: str | None
    home_team: str | None
    away_team: str | None
    home_score: int | None
    away_score: int | None
    status: str | None
    progress: str | None
    venue: str | None
    winner: str | None
    raw_record: dict[str, Any]
    confidence: float


# =============================================================================
# TheSportsDB Event Stat Model
# =============================================================================
# Match statistics vary a lot by sport and even by league, so this model keeps
# stats flexible and row-based instead of trying to force them into one rigid
# schema too early.
@dataclass(slots=True)
class TheSportsDBEventStat:
    """Structured event stat record normalized from TheSportsDB.

    Attributes:
        source: Source name. For this model it will be "thesportsdb".
        sport: Sport name such as "Soccer" or "Basketball".
        event_id: TheSportsDB unique event identifier.
        stat_name: Name of the statistic, such as possession or shots on target.
        home_value: Home side value for the statistic.
        away_value: Away side value for the statistic.
        raw_record: Original API payload for debugging and future enrichment.
        confidence: Normalization confidence score for this record.
    """

    source: str
    sport: str | None
    event_id: str
    stat_name: str
    home_value: str | int | float | None
    away_value: str | int | float | None
    raw_record: dict[str, Any]
    confidence: float


# =============================================================================
# TheSportsDB Event Lineup Player Model
# =============================================================================
# This model connects players to a specific event. It gives us the foundation
# for lineups, player-event participation, and later player-performance views.
@dataclass(slots=True)
class TheSportsDBEventLineupPlayer:
    """Structured lineup/player-event record normalized from TheSportsDB.

    Attributes:
        source: Source name. For this model it will be "thesportsdb".
        sport: Sport name such as "Soccer" or "Basketball".
        event_id: TheSportsDB unique event identifier.
        team_id: Team identifier for the player in this event.
        team_name: Team name for the player in this event.
        player_id: TheSportsDB player identifier.
        player_name: Player name.
        position: Positional label when available.
        shirt_number: Shirt or squad number when available.
        role: Event role such as starter, substitute, bench, or coach when available.
        status: Participation status text when available.
        raw_record: Original API payload for debugging and future enrichment.
        confidence: Normalization confidence score for this record.
    """

    source: str
    sport: str | None
    event_id: str
    team_id: str | None
    team_name: str | None
    player_id: str | None
    player_name: str | None
    position: str | None
    shirt_number: str | None
    role: str | None
    status: str | None
    raw_record: dict[str, Any]
    confidence: float


# =============================================================================
# TheSportsDB Player Profile Model
# =============================================================================
# This profile model is useful for the larger platform vision: player research,
# likely-to-score logic, former-team context, and richer player dashboards.
# Even if we do not use every field immediately, defining the shape now helps us
# keep the long-term architecture in mind.
@dataclass(slots=True)
class TheSportsDBPlayerProfile:
    """Structured player profile record normalized from TheSportsDB.

    Attributes:
        source: Source name. For this model it will be "thesportsdb".
        sport: Sport name such as "Soccer" or "Basketball".
        player_id: TheSportsDB unique player identifier.
        player_name: Player name.
        team_id: Current team identifier when available.
        team_name: Current team name when available.
        nationality: Player nationality when available.
        date_of_birth: Date of birth when available.
        position: Primary playing position when available.
        height: Height when available.
        weight: Weight when available.
        gender: Gender when available.
        description: Short player biography or description when available.
        former_teams: Former teams or club history summary when available.
        honours: Honours or awards summary when available.
        raw_record: Original API payload for debugging and future enrichment.
        confidence: Normalization confidence score for this record.
    """

    source: str
    sport: str | None
    player_id: str
    player_name: str | None
    team_id: str | None
    team_name: str | None
    nationality: str | None
    date_of_birth: str | None
    position: str | None
    height: str | None
    weight: str | None
    gender: str | None
    description: str | None
    former_teams: list[str]
    honours: list[str]
    raw_record: dict[str, Any]
    confidence: float
