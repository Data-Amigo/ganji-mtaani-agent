"""This is the fetch_and_parse_sportpesa.py file.

Author: Data-Amigo
Date: 2026-05-01
Description:
This script fetches a live SportPesa target page with the shared browser layer,
parses the stable odds fields for that sport, and prints a structured preview
for development and verification.
"""

from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ganji_mtaani_agent.parsers.sportpesa import parse_sportpesa_basketball, parse_sportpesa_football
from ganji_mtaani_agent.scrapers.browser import fetch_page
from ganji_mtaani_agent.scrapers.sources import get_source_config, get_source_target


# =============================================================================
# Main Workflow Function
# =============================================================================
def main() -> None:
    """Fetch a live SportPesa page and parse the stable odds rows for its sport."""

    parser = argparse.ArgumentParser(description="Fetch and parse SportPesa odds.")
    parser.add_argument("--target", default="football_today", help="SportPesa target key to fetch.")
    parser.add_argument("--limit", type=int, default=5, help="Number of parsed rows to print.")
    parser.add_argument("--save-snapshot", action="store_true")
    parser.add_argument("--screenshot", action="store_true")
    parser.add_argument("--headed", action="store_true", help="Force a visible browser window.")
    parser.add_argument("--headless", action="store_true", help="Force a hidden browser window.")
    parser.add_argument("--settle-ms", type=int, default=None, help="Override extra wait after page load.")
    parser.add_argument("--timeout-ms", type=int, default=60000, help="Maximum page load timeout.")
    args = parser.parse_args()

    source = get_source_config("sportpesa")
    target = get_source_target(source, args.target)

    headless = source.default_headless
    if args.headed:
        headless = False
    elif args.headless:
        headless = True

    settle_ms = args.settle_ms if args.settle_ms is not None else source.default_settle_ms

    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    artifact_folder = Path("data") / "raw" / "sportpesa" / target.name
    snapshot_path = artifact_folder / f"{timestamp}.html" if args.save_snapshot else None
    screenshot_path = artifact_folder / f"{timestamp}.png" if args.screenshot else None

    result = fetch_page(
        target.url,
        timeout_ms=args.timeout_ms,
        wait_until=source.default_wait_until,
        settle_ms=settle_ms,
        headless=headless,
        snapshot_path=snapshot_path,
        screenshot_path=screenshot_path,
    )

    print(f"source: {source.display_name}")
    print(f"target: {target.display_name}")
    print(f"sport: {target.sport}")
    print(f"url: {result.url}")
    print(f"status: {result.status}")
    print(f"title: {result.title}")
    print(f"html_length: {result.html_length}")
    print(f"duration_ms: {result.duration_ms}")
    print(f"headless: {headless}")
    print(f"snapshot_path: {result.snapshot_path}")
    print(f"screenshot_path: {result.screenshot_path}")

    if result.warnings:
        print("warnings:")
        for warning in result.warnings:
            print(f"- {warning}")

    if result.error:
        print(f"error: {result.error}")
        return

    if target.sport == "football":
        parsed_rows = parse_sportpesa_football(result.html)
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
            print(f"  draw_odds: {row.draw_odds}")
            print(f"  away_odds: {row.away_odds}")
            print(f"  home_or_draw_odds: {row.home_or_draw_odds}")
            print(f"  draw_or_away_odds: {row.draw_or_away_odds}")
            print(f"  home_or_away_odds: {row.home_or_away_odds}")
            print(f"  over_2_5_odds: {row.over_2_5_odds}")
            print(f"  under_2_5_odds: {row.under_2_5_odds}")
            print(f"  btts_yes_odds: {row.btts_yes_odds}")
            print(f"  btts_no_odds: {row.btts_no_odds}")
            print(f"  game_url: {row.game_url}")
            print(f"  confidence: {row.confidence}")
    elif target.sport == "basketball":
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
    else:
        raise ValueError(f"Unsupported SportPesa sport '{target.sport}' for parser output.")


if __name__ == "__main__":
    main()
