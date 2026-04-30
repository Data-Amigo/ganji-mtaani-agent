"""This is the fetch_polymarket_gamma.py file.

Author: Data-Amigo
Date: 2026-04-30
Description:
This script is a thin inspection runner for the reusable Polymarket ingestion
module. It fetches live market data through the package scraper, normalizes it,
and prints a readable preview for development and learning purposes.
"""

from __future__ import annotations

# =============================================================================
# Imports
# =============================================================================
import argparse
import sys
from pathlib import Path


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
from ganji_mtaani_agent.models.polymarket_fetch import PolymarketFetchConfig
from ganji_mtaani_agent.scrapers.polymarket import fetch_polymarket_markets, fetch_polymarket_raw


# =============================================================================
# CLI Defaults
# =============================================================================
DEFAULT_LIMIT = 5
DEFAULT_SCAN_LIMIT = 100


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
        help="Number of normalized markets to print after filtering.",
    )
    parser.add_argument(
        "--scan-limit",
        type=int,
        default=DEFAULT_SCAN_LIMIT,
        help="Number of raw markets to scan before filtering.",
    )
    parser.add_argument(
        "--category",
        type=str,
        default=None,
        help="Optional category or tag filter, for example sports or politics.",
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
        print(f"  event_id: {market.event_id}")
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

    config = PolymarketFetchConfig(
        result_limit=args.limit,
        scan_limit=args.scan_limit,
        active_only=not args.include_closed,
        category=args.category,
    )
    raw_response = fetch_polymarket_raw(config)
    normalized_markets = fetch_polymarket_markets(config)

    print(f"raw_markets: {len(raw_response.markets)}")
    print(f"raw_events: {len(raw_response.events)}")
    print_market_preview(normalized_markets)


if __name__ == "__main__":
    main()
