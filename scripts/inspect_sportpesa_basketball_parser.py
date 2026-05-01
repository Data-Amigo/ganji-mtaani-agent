"""This is the inspect_sportpesa_basketball_parser.py file.

Author: Data-Amigo
Date: 2026-05-01
Description:
This script fetches the live SportPesa basketball page through the shared
browser layer, parses the stable basketball odds fields, and prints a small
structured preview so we can validate the first parser pass.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ganji_mtaani_agent.parsers.sportpesa import parse_sportpesa_basketball
from ganji_mtaani_agent.scrapers.browser import fetch_page
from ganji_mtaani_agent.scrapers.sources import get_source_config, get_source_target


# =============================================================================
# Main Inspection Function
# =============================================================================
def main() -> None:
    """Fetch the live SportPesa basketball page and inspect parsed rows."""

    parser = argparse.ArgumentParser(description="Inspect the SportPesa basketball parser output.")
    parser.add_argument("--limit", type=int, default=5, help="Number of parsed rows to print.")
    parser.add_argument("--settle-ms", type=int, default=None, help="Override extra wait after page load.")
    parser.add_argument("--timeout-ms", type=int, default=60000, help="Maximum page load timeout.")
    args = parser.parse_args()

    source = get_source_config("sportpesa")
    target = get_source_target(source, "basketball_today")
    settle_ms = args.settle_ms if args.settle_ms is not None else source.default_settle_ms

    result = fetch_page(
        target.url,
        timeout_ms=args.timeout_ms,
        wait_until=source.default_wait_until,
        settle_ms=settle_ms,
        headless=False,
    )

    print(f"source: {source.display_name}")
    print(f"target: {target.display_name}")
    print(f"sport: {target.sport}")
    print(f"url: {result.url}")
    print(f"status: {result.status}")
    print(f"title: {result.title}")
    print(f"html_length: {result.html_length}")

    if result.error:
        print(f"error: {result.error}")
        return

    parsed_rows = parse_sportpesa_basketball(result.html)
    print(f"parsed_rows: {len(parsed_rows)}")

    for index, row in enumerate(parsed_rows[: args.limit], start=1):
        print("---")
        print(f"row_{index}:")
        print(f"  league: {row.league}")
        print(f"  event_datetime: {row.event_datetime}")
        print(f"  game_id: {row.game_id}")
        print(f"  home_team: {row.home_team}")
        print(f"  away_team: {row.away_team}")
        print(f"  home_odds: {row.home_odds}")
        print(f"  away_odds: {row.away_odds}")
        print(f"  game_url: {row.game_url}")
        print(f"  confidence: {row.confidence}")


if __name__ == "__main__":
    main()
