import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen


# =============================================================================
# TheSportsDB API Configuration
# =============================================================================
# We are starting on the free v1 API because it is enough to prove the results,
# stats, and player-enrichment workflow before deciding whether premium is
# worth the monthly upgrade.
THESPORTSDB_V1_BASE_URL = "https://www.thesportsdb.com/api/v1/json/123"
DEFAULT_TIMEOUT_SECONDS = 30.0
DEFAULT_USER_AGENT = "gAnji-Mtaani-Agent/0.1"


# =============================================================================
# Low-Level JSON Fetch Helper
# =============================================================================
def _fetch_json(endpoint: str, params: dict[str, object] | None = None) -> dict[str, object]:
    """Fetch JSON from a TheSportsDB v1 endpoint."""

    params = params or {}
    query_string = urlencode(params)
    url = f"{THESPORTSDB_V1_BASE_URL}{endpoint}"
    if query_string:
        url = f"{url}?{query_string}"

    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": DEFAULT_USER_AGENT,
        },
        method="GET",
    )

    with urlopen(request, timeout=DEFAULT_TIMEOUT_SECONDS) as response:
        payload = json.loads(response.read().decode("utf-8"))

    if not isinstance(payload, dict):
        raise ValueError("Expected TheSportsDB endpoint to return a JSON object.")

    return payload


# =============================================================================
# League and Schedule Endpoints
# =============================================================================
def fetch_events_day(
    event_date: str,
    sport: str | None = None,
    league_id: str | None = None,
) -> dict[str, object]:
    """Fetch all events on a given day, optionally filtered by sport or league."""

    params: dict[str, object] = {"d": event_date}
    if sport:
        params["s"] = sport
    if league_id:
        params["l"] = league_id

    return _fetch_json("/eventsday.php", params)


def fetch_events_past_league(league_id: str) -> dict[str, object]:
    """Fetch previous events for a league by league id."""

    return _fetch_json("/eventspastleague.php", {"id": league_id})


def fetch_events_next_league(league_id: str) -> dict[str, object]:
    """Fetch next events for a league by league id."""

    return _fetch_json("/eventsnextleague.php", {"id": league_id})


def search_all_leagues(country: str, sport: str) -> dict[str, object]:
    """Search all leagues for a given country and sport."""

    return _fetch_json("/search_all_leagues.php", {"c": country, "s": sport})


# =============================================================================
# Event Enrichment Endpoints
# =============================================================================
def fetch_lookup_event(event_id: str) -> dict[str, object]:
    """Fetch one event payload by event id."""

    return _fetch_json("/lookupevent.php", {"id": event_id})


def fetch_event_results(event_id: str) -> dict[str, object]:
    """Fetch event results by event id."""

    return _fetch_json("/eventresults.php", {"id": event_id})


def fetch_event_stats(event_id: str) -> dict[str, object]:
    """Fetch event statistics by event id."""

    return _fetch_json("/lookupeventstats.php", {"id": event_id})


def fetch_event_lineup(event_id: str) -> dict[str, object]:
    """Fetch event lineup by event id."""

    return _fetch_json("/lookuplineup.php", {"id": event_id})


def fetch_event_timeline(event_id: str) -> dict[str, object]:
    """Fetch event timeline by event id."""

    return _fetch_json("/lookuptimeline.php", {"id": event_id})


# =============================================================================
# Player Enrichment Endpoints
# =============================================================================
def fetch_lookup_player(player_id: str) -> dict[str, object]:
    """Fetch one player profile payload by player id."""

    return _fetch_json("/lookupplayer.php", {"id": player_id})


def fetch_player_former_teams(player_id: str) -> dict[str, object]:
    """Fetch former teams for a player by player id."""

    return _fetch_json("/lookupformerteams.php", {"id": player_id})


def fetch_player_honours(player_id: str) -> dict[str, object]:
    """Fetch honours for a player by player id."""

    return _fetch_json("/lookuphonours.php", {"id": player_id})


def fetch_player_results(player_id: str) -> dict[str, object]:
    """Fetch player results for a player by player id."""

    return _fetch_json("/playerresults.php", {"id": player_id})
