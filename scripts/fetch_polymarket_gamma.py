"""This is the fetch_polymarket_gamma.py file.

Author: Data-Amigo
Date: 2026-04-29
Description:
This script fetches live market records from the Polymarket Gamma API,
normalizes the stable V1 fields into the PolymarketMarket model, and prints
an inspection-friendly preview so we can learn the response structure before
building the full ingestion pipeline.
"""

from __future__ import annotations

# =============================================================================
# Imports
# =============================================================================
import argparse
import json
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen


# =============================================================================
# Project Path Setup
# =============================================================================
# Add the src directory to sys.path so the script can be run directly from the
# repo root without requiring package installation first.
ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from ganji_mtaani_agent.models.polymarket import PolymarketMarket


# =============================================================================
# API Configuration
# =============================================================================
GAMMA_API_BASE_URL = "https://gamma-api.polymarket.com"
DEFAULT_MARKETS_ENDPOINT = "/markets"
DEFAULT_TIMEOUT_SECONDS = 30.0
DEFAULT_LIMIT = 5


# =============================================================================
# Parsing Helpers
# =============================================================================
def _to_float(value: Any) -> float | None:
    """Convert a raw value to float when possible.

    The Gamma API may return numbers as strings, integers, floats, or nulls.
    This helper keeps the normalization logic readable and tolerant.
    """

    if value in (None, "", "null"):
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_json_list(raw_value: Any) -> list[Any]:
    """Parse list-like values from the API into a Python list.

    Polymarket often returns `outcomes` and `outcomePrices` as JSON-encoded
    strings rather than native arrays. This helper safely handles both cases.
    """

    if raw_value is None:
        return []

    if isinstance(raw_value, list):
        return raw_value

    if isinstance(raw_value, str):
        raw_value = raw_value.strip()

        if not raw_value:
            return []

        try:
            parsed = json.loads(raw_value)
        except json.JSONDecodeError:
            return [raw_value]

        return parsed if isinstance(parsed, list) else [parsed]

    return [raw_value]


def _parse_tags(raw_value: Any) -> list[str]:
    """Normalize tag-like API values into a list of strings."""

    raw_tags = _parse_json_list(raw_value)
    normalized_tags: list[str] = []

    for item in raw_tags:
        if isinstance(item, dict):
            label = item.get("label") or item.get("slug") or item.get("name")
            if label:
                normalized_tags.append(str(label))
        elif item not in (None, ""):
            normalized_tags.append(str(item))

    return normalized_tags


# =============================================================================
# Normalization Logic
# =============================================================================
def normalize_market_record(raw_record: dict[str, Any]) -> PolymarketMarket:
    """Convert one raw Gamma API market record into our stable V1 model."""

    raw_outcomes = _parse_json_list(raw_record.get("outcomes"))
    raw_prices = _parse_json_list(raw_record.get("outcomePrices"))

    outcomes = [str(item) for item in raw_outcomes if item not in (None, "")]
    outcome_prices = [price for price in (_to_float(item) for item in raw_prices) if price is not None]

    return PolymarketMarket(
        source="polymarket",
        market_id=str(raw_record.get("id", "")),
        event_id=(
            str(raw_record.get("eventId"))
            if raw_record.get("eventId") not in (None, "")
            else None
        ),
        question=str(raw_record.get("question") or ""),
        slug=(str(raw_record.get("slug")) if raw_record.get("slug") not in (None, "") else None),
        category=(
            str(raw_record.get("category"))
            if raw_record.get("category") not in (None, "")
            else None
        ),
        subcategory=(
            str(raw_record.get("subcategory"))
            if raw_record.get("subcategory") not in (None, "")
            else None
        ),
        tags=_parse_tags(raw_record.get("tags")),
        description=(
            str(raw_record.get("description"))
            if raw_record.get("description") not in (None, "")
            else None
        ),
        start_date=(
            str(raw_record.get("startDate"))
            if raw_record.get("startDate") not in (None, "")
            else None
        ),
        end_date=(
            str(raw_record.get("endDate"))
            if raw_record.get("endDate") not in (None, "")
            else None
        ),
        active=bool(raw_record.get("active", False)),
        closed=bool(raw_record.get("closed", False)),
        archived=bool(raw_record.get("archived", False)),
        outcomes=outcomes,
        outcome_prices=outcome_prices,
        liquidity=_to_float(raw_record.get("liquidity")),
        volume=_to_float(raw_record.get("volume")),
        open_interest=_to_float(raw_record.get("openInterest")),
        market_type=(
            str(raw_record.get("ammType") or raw_record.get("marketType"))
            if raw_record.get("ammType") not in (None, "") or raw_record.get("marketType") not in (None, "")
            else None
        ),
        raw_record=raw_record,
        confidence=1.0,
    )


# =============================================================================
# Gamma API Fetch Logic
# =============================================================================
def fetch_gamma_markets(limit: int, active_only: bool) -> list[dict[str, Any]]:
    """Fetch raw market records from the Polymarket Gamma API."""

    params = {
        "limit": limit,
        "closed": "false",
    }

    if active_only:
        params["active"] = "true"

    query_string = urlencode(params)
    url = f"{GAMMA_API_BASE_URL}{DEFAULT_MARKETS_ENDPOINT}?{query_string}"

    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "gAnji-Mtaani-Agent/0.1",
        },
        method="GET",
    )

    with urlopen(request, timeout=DEFAULT_TIMEOUT_SECONDS) as response:
        payload = json.loads(response.read().decode("utf-8"))

    if not isinstance(payload, list):
        raise ValueError("Expected the Gamma API /markets endpoint to return a list.")

    return payload


# =============================================================================
# CLI Helpers
# =============================================================================
def build_argument_parser() -> argparse.ArgumentParser:
    """Build the command-line interface for the inspection script."""

    parser = argparse.ArgumentParser(
        description="Fetch and inspect live Polymarket Gamma API market records."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_LIMIT,
        help="Number of markets to fetch from the API.",
    )
    parser.add_argument(
        "--category",
        type=str,
        default=None,
        help="Optional client-side category filter, for example sports or politics.",
    )
    parser.add_argument(
        "--include-closed",
        action="store_true",
        help="Include closed markets instead of restricting to active ones.",
    )
    return parser


# =============================================================================
# Output Helpers
# =============================================================================
def print_market_preview(markets: list[PolymarketMarket]) -> None:
    """Print a readable summary of normalized Polymarket records."""

    print(f"normalized_markets: {len(markets)}")

    for index, market in enumerate(markets, start=1):
        print("---")
        print(f"market_{index}:")
        print(f"  question: {market.question}")
        print(f"  category: {market.category}")
        print(f"  subcategory: {market.subcategory}")
        print(f"  slug: {market.slug}")
        print(f"  outcomes: {market.outcomes}")
        print(f"  outcome_prices: {market.outcome_prices}")
        print(f"  outcome_map: {market.outcome_map()}")
        print(f"  volume: {market.volume}")
        print(f"  liquidity: {market.liquidity}")
        print(f"  open_interest: {market.open_interest}")
        print(f"  active: {market.active}")
        print(f"  closed: {market.closed}")
        print(f"  archived: {market.archived}")
        print(f"  end_date: {market.end_date}")
        print(f"  tags: {market.tags}")


# =============================================================================
# Main Entry Point
# =============================================================================
def main() -> None:
    """Fetch live Gamma API records and print a normalized preview."""

    parser = build_argument_parser()
    args = parser.parse_args()

    raw_markets = fetch_gamma_markets(limit=args.limit, active_only=not args.include_closed)
    normalized_markets = [normalize_market_record(item) for item in raw_markets]

    if args.category:
        requested_category = args.category.casefold()
        normalized_markets = [
            market
            for market in normalized_markets
            if market.category and market.category.casefold() == requested_category
        ]

    print(f"raw_markets: {len(raw_markets)}")
    print_market_preview(normalized_markets)


if __name__ == "__main__":
    main()
