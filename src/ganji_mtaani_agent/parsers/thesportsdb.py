from __future__ import annotations

from typing import Any

from ganji_mtaani_agent.models.thesportsdb import (
    TheSportsDBEventLineupPlayer,
    TheSportsDBEventResult,
    TheSportsDBEventStat,
    TheSportsDBPlayerProfile,
)


# =============================================================================
# Basic Parsing Helpers
# =============================================================================
def _to_int(value: Any) -> int | None:
    """Convert a raw score-like value to int when possible."""

    if value in (None, "", "null"):
        return None

    try:
        return int(str(value))
    except (TypeError, ValueError):
        return None


def _pick(raw_record: dict[str, Any], *keys: str) -> Any:
    """Return the first non-empty value from a record using multiple key options."""

    for key in keys:
        value = raw_record.get(key)
        if value not in (None, "", "null"):
            return value
    return None


def _extract_records(payload: dict[str, Any], preferred_keys: list[str] | None = None) -> list[dict[str, Any]]:
    """Extract a list of dict records from a TheSportsDB payload."""

    preferred_keys = preferred_keys or []

    for key in preferred_keys:
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]

    for value in payload.values():
        if isinstance(value, list) and all(isinstance(item, dict) for item in value):
            return value

    return []


def _derive_winner(home_score: int | None, away_score: int | None) -> str | None:
    """Derive the winner label from home and away scores when possible."""

    if home_score is None or away_score is None:
        return None
    if home_score > away_score:
        return "home"
    if away_score > home_score:
        return "away"
    return "draw"


# =============================================================================
# Event Result Normalization
# =============================================================================
def normalize_event_result(raw_record: dict[str, Any]) -> TheSportsDBEventResult:
    """Normalize one raw TheSportsDB event record into our result model."""

    home_score = _to_int(_pick(raw_record, "intHomeScore", "intScore", "intScoreHome"))
    away_score = _to_int(_pick(raw_record, "intAwayScore", "intScoreAway"))
    home_team = _pick(raw_record, "strHomeTeam")
    away_team = _pick(raw_record, "strAwayTeam")
    event_name = _pick(raw_record, "strEvent") or (
        f"{home_team} vs {away_team}" if home_team and away_team else None
    )

    return TheSportsDBEventResult(
        source="thesportsdb",
        sport=(_pick(raw_record, "strSport") if _pick(raw_record, "strSport") else None),
        event_id=str(_pick(raw_record, "idEvent") or ""),
        league_id=(str(_pick(raw_record, "idLeague")) if _pick(raw_record, "idLeague") else None),
        league=(str(_pick(raw_record, "strLeague")) if _pick(raw_record, "strLeague") else None),
        season=(str(_pick(raw_record, "strSeason")) if _pick(raw_record, "strSeason") else None),
        event_name=(str(event_name) if event_name else None),
        event_date=(str(_pick(raw_record, "dateEvent", "dateEventLocal")) if _pick(raw_record, "dateEvent", "dateEventLocal") else None),
        event_time=(str(_pick(raw_record, "strTime", "strEventTime", "strTimeLocal")) if _pick(raw_record, "strTime", "strEventTime", "strTimeLocal") else None),
        home_team_id=(str(_pick(raw_record, "idHomeTeam")) if _pick(raw_record, "idHomeTeam") else None),
        away_team_id=(str(_pick(raw_record, "idAwayTeam")) if _pick(raw_record, "idAwayTeam") else None),
        home_team=(str(home_team) if home_team else None),
        away_team=(str(away_team) if away_team else None),
        home_score=home_score,
        away_score=away_score,
        status=(str(_pick(raw_record, "strStatus")) if _pick(raw_record, "strStatus") else None),
        progress=(str(_pick(raw_record, "strProgress")) if _pick(raw_record, "strProgress") else None),
        venue=(str(_pick(raw_record, "strVenue", "strStadium", "strLocation")) if _pick(raw_record, "strVenue", "strStadium", "strLocation") else None),
        winner=_derive_winner(home_score, away_score),
        raw_record=raw_record,
        confidence=1.0,
    )


def normalize_event_results(payload: dict[str, Any]) -> list[TheSportsDBEventResult]:
    """Normalize a TheSportsDB payload into a list of event result records."""

    records = _extract_records(payload, preferred_keys=["events", "results", "event"])
    return [normalize_event_result(record) for record in records if _pick(record, "idEvent")]


# =============================================================================
# Event Stat Normalization
# =============================================================================
def normalize_event_stats(payload: dict[str, Any], event_id: str | None = None, sport: str | None = None) -> list[TheSportsDBEventStat]:
    """Normalize a TheSportsDB payload into event stat rows."""

    records = _extract_records(payload, preferred_keys=["eventstats", "statistics", "stats"])
    normalized: list[TheSportsDBEventStat] = []

    for record in records:
        normalized.append(
            TheSportsDBEventStat(
                source="thesportsdb",
                sport=sport or (str(_pick(record, "strSport")) if _pick(record, "strSport") else None),
                event_id=str(event_id or _pick(record, "idEvent") or ""),
                stat_name=str(_pick(record, "strStat", "strStatistic", "strType") or "unknown_stat"),
                home_value=_pick(record, "strHome", "intHome", "strHomeValue", "intHomeScore", "intHomeStat"),
                away_value=_pick(record, "strAway", "intAway", "strAwayValue", "intAwayScore", "intAwayStat"),
                raw_record=record,
                confidence=1.0,
            )
        )

    return normalized


# =============================================================================
# Event Lineup Normalization
# =============================================================================
def normalize_event_lineup(payload: dict[str, Any], event_id: str | None = None, sport: str | None = None) -> list[TheSportsDBEventLineupPlayer]:
    """Normalize a TheSportsDB payload into lineup/player rows."""

    records = _extract_records(payload, preferred_keys=["lineup", "players", "eventlineup"])
    normalized: list[TheSportsDBEventLineupPlayer] = []

    for record in records:
        normalized.append(
            TheSportsDBEventLineupPlayer(
                source="thesportsdb",
                sport=sport or (str(_pick(record, "strSport")) if _pick(record, "strSport") else None),
                event_id=str(event_id or _pick(record, "idEvent") or ""),
                team_id=(str(_pick(record, "idTeam")) if _pick(record, "idTeam") else None),
                team_name=(str(_pick(record, "strTeam")) if _pick(record, "strTeam") else None),
                player_id=(str(_pick(record, "idPlayer")) if _pick(record, "idPlayer") else None),
                player_name=(str(_pick(record, "strPlayer", "strCutout")) if _pick(record, "strPlayer", "strCutout") else None),
                position=(str(_pick(record, "strPosition")) if _pick(record, "strPosition") else None),
                shirt_number=(str(_pick(record, "strNumber", "intSquadNumber")) if _pick(record, "strNumber", "intSquadNumber") else None),
                role=(str(_pick(record, "strType", "strRole")) if _pick(record, "strType", "strRole") else None),
                status=(str(_pick(record, "strStatus")) if _pick(record, "strStatus") else None),
                raw_record=record,
                confidence=1.0,
            )
        )

    return normalized


# =============================================================================
# Player Profile Normalization
# =============================================================================
def normalize_player_profile(
    player_payload: dict[str, Any],
    former_teams_payload: dict[str, Any] | None = None,
    honours_payload: dict[str, Any] | None = None,
) -> TheSportsDBPlayerProfile | None:
    """Normalize TheSportsDB player and enrichment payloads into one profile model."""

    player_records = _extract_records(player_payload, preferred_keys=["players", "player"])
    if not player_records:
        return None

    player_record = player_records[0]
    former_team_records = _extract_records(former_teams_payload or {}, preferred_keys=["formerteams", "teams"])
    honour_records = _extract_records(honours_payload or {}, preferred_keys=["honours", "awards"])

    former_teams = [
        str(_pick(record, "strTeam", "strFormerTeam", "strClub"))
        for record in former_team_records
        if _pick(record, "strTeam", "strFormerTeam", "strClub")
    ]
    honours = [
        str(_pick(record, "strHonour", "strAchievement", "strTitle"))
        for record in honour_records
        if _pick(record, "strHonour", "strAchievement", "strTitle")
    ]

    return TheSportsDBPlayerProfile(
        source="thesportsdb",
        sport=(str(_pick(player_record, "strSport")) if _pick(player_record, "strSport") else None),
        player_id=str(_pick(player_record, "idPlayer") or ""),
        player_name=(str(_pick(player_record, "strPlayer")) if _pick(player_record, "strPlayer") else None),
        team_id=(str(_pick(player_record, "idTeam")) if _pick(player_record, "idTeam") else None),
        team_name=(str(_pick(player_record, "strTeam")) if _pick(player_record, "strTeam") else None),
        nationality=(str(_pick(player_record, "strNationality")) if _pick(player_record, "strNationality") else None),
        date_of_birth=(str(_pick(player_record, "dateBorn")) if _pick(player_record, "dateBorn") else None),
        position=(str(_pick(player_record, "strPosition")) if _pick(player_record, "strPosition") else None),
        height=(str(_pick(player_record, "strHeight")) if _pick(player_record, "strHeight") else None),
        weight=(str(_pick(player_record, "strWeight")) if _pick(player_record, "strWeight") else None),
        gender=(str(_pick(player_record, "strGender")) if _pick(player_record, "strGender") else None),
        description=(str(_pick(player_record, "strDescriptionEN", "strDescription")) if _pick(player_record, "strDescriptionEN", "strDescription") else None),
        former_teams=former_teams,
        honours=honours,
        raw_record=player_record,
        confidence=1.0,
    )
