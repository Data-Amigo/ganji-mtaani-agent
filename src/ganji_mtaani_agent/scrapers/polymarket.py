import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from ganji_mtaani_agent.models.polymarket import PolymarketMarket
from ganji_mtaani_agent.models.polymarket_fetch import PolymarketFetchConfig, PolymarketRawResponse
from ganji_mtaani_agent.parsers.polymarket import normalize_polymarket_markets


# =============================================================================
# Polymarket Gamma API Configuration
# =============================================================================
# Polymarket is API-first for this project, so the main scraper is really a
# structured fetcher that pulls raw JSON from Gamma and then hands it to the
# parser/normalizer layer.
GAMMA_API_BASE_URL = "https://gamma-api.polymarket.com"
MARKETS_ENDPOINT = "/markets"
EVENTS_ENDPOINT = "/events"
DEFAULT_TIMEOUT_SECONDS = 30.0
DEFAULT_USER_AGENT = "gAnji-Mtaani-Agent/0.1"


# =============================================================================
# Low-Level JSON Fetch Helpers
# =============================================================================
def _fetch_json(endpoint: str, params: dict[str, object]) -> object:
    """Fetch JSON from a Polymarket Gamma API endpoint."""

    query_string = urlencode(params)
    url = f"{GAMMA_API_BASE_URL}{endpoint}?{query_string}"

    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": DEFAULT_USER_AGENT,
        },
        method="GET",
    )

    with urlopen(request, timeout=DEFAULT_TIMEOUT_SECONDS) as response:
        return json.loads(response.read().decode("utf-8"))


# =============================================================================
# Raw Polymarket Fetch Functions
# =============================================================================
def fetch_gamma_markets(scan_limit: int, active_only: bool = True) -> list[dict[str, object]]:
    """Fetch raw Polymarket market payloads from the Gamma API."""

    params = {
        "limit": scan_limit,
        "closed": "false",
    }

    if active_only:
        params["active"] = "true"

    payload = _fetch_json(MARKETS_ENDPOINT, params)

    if not isinstance(payload, list):
        raise ValueError("Expected the Gamma API /markets endpoint to return a list.")

    return payload


def fetch_gamma_events(scan_limit: int, active_only: bool = True) -> list[dict[str, object]]:
    """Fetch raw Polymarket event payloads from the Gamma API."""

    params = {
        "limit": max(scan_limit, 50),
        "closed": "false",
    }

    if active_only:
        params["active"] = "true"

    payload = _fetch_json(EVENTS_ENDPOINT, params)

    if not isinstance(payload, list):
        raise ValueError("Expected the Gamma API /events endpoint to return a list.")

    return payload


def fetch_polymarket_raw(config: PolymarketFetchConfig) -> PolymarketRawResponse:
    """Fetch the raw Polymarket market and event payloads for ingestion."""

    raw_markets = fetch_gamma_markets(scan_limit=config.scan_limit, active_only=config.active_only)
    raw_events = fetch_gamma_events(scan_limit=max(config.scan_limit * 5, 50), active_only=config.active_only)

    return PolymarketRawResponse(markets=raw_markets, events=raw_events)


# =============================================================================
# Main Polymarket Ingestion Entry Point
# =============================================================================
def fetch_polymarket_markets(config: PolymarketFetchConfig) -> list[PolymarketMarket]:
    """Fetch, enrich, normalize, and filter Polymarket markets.

    This is the main ingestion function that the dashboard, pipeline, and later
    database layer should call when they need structured Polymarket records.
    """

    raw_response = fetch_polymarket_raw(config)

    return normalize_polymarket_markets(
        raw_markets=raw_response.markets,
        raw_events=raw_response.events,
        category=config.category,
        result_limit=config.result_limit,
    )
