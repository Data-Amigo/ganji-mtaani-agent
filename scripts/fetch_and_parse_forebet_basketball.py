"""This is the fetch_and_parse_forebet_basketball.py file.

Author: Data-Amigo
Date: 2026-04-29
Description:
This is a small developer workflow script that fetches the Forebet basketball
page, optionally saves debug artifacts, parses the snapshot, and prints a few
structured records. It connects the browser layer and the parser layer in one
place for easier testing.
"""

from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path

# =============================================================================
# Local Import Setup
# =============================================================================
# This lets the script run directly from the repo before the package is fully
# installed in the environment.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ganji_mtaani_agent.parsers.forebet import parse_forebet_basketball
from ganji_mtaani_agent.scrapers.browser import fetch_page
from ganji_mtaani_agent.scrapers.sources import get_source_config, get_source_target


# =============================================================================
# Artifact Path Helper
# =============================================================================
# We keep raw HTML and screenshots under data/raw/ so we can inspect what the
# browser actually saw during a parser test run.
def build_artifact_paths(source_name: str, target_name: str) -> tuple[Path, Path]:
    """Build snapshot and screenshot paths for one fetch run."""

    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    folder = Path("data") / "raw" / source_name / target_name
    return folder / f"{timestamp}.html", folder / f"{timestamp}.png"


# =============================================================================
# Command-Line Entry Point
# =============================================================================
def main() -> None:
    """Fetch Forebet basketball, parse it, and print a small preview."""

    parser = argparse.ArgumentParser(description="Fetch and parse Forebet basketball data.")
    parser.add_argument(
        "--target",
        choices=["basketball_today", "football_today"],
        default="basketball_today",
        help="Forebet target page. Basketball parsing is implemented today.",
    )
    parser.add_argument("--limit", type=int, default=5, help="How many parsed rows to print.")
    parser.add_argument("--save-snapshot", action="store_true", help="Save the raw HTML snapshot.")
    parser.add_argument("--screenshot", action="store_true", help="Save a screenshot of the page.")
    parser.add_argument("--headless", action="store_true", help="Force headless mode for comparison.")
    args = parser.parse_args()

    source = get_source_config("forebet")
    target = get_source_target(source, args.target)

    snapshot_path = None
    screenshot_path = None
    if args.save_snapshot or args.screenshot:
        built_snapshot_path, built_screenshot_path = build_artifact_paths(source.name, target.name)
        if args.save_snapshot:
            snapshot_path = built_snapshot_path
        if args.screenshot:
            screenshot_path = built_screenshot_path

    result = fetch_page(
        target.url,
        wait_until=source.default_wait_until,
        settle_ms=source.default_settle_ms,
        headless=args.headless if args.headless else source.default_headless,
        snapshot_path=snapshot_path,
        screenshot_path=screenshot_path,
    )

    print(f"source: {source.display_name}")
    print(f"target: {target.display_name}")
    print(f"sport: {target.sport}")
    print(f"status: {result.status}")
    print(f"title: {result.title}")
    print(f"html_length: {result.html_length}")
    print(f"snapshot_path: {result.snapshot_path}")
    print(f"screenshot_path: {result.screenshot_path}")

    if result.warnings:
        print("warnings:")
        for warning in result.warnings:
            print(f"- {warning}")

    if result.error:
        print(f"error: {result.error}")
        return

    if target.name != "basketball_today":
        print("Parser note: only basketball parsing is implemented right now.")
        return

    predictions = parse_forebet_basketball(result.html)
    print(f"parsed_rows: {len(predictions)}")
    print()

    for index, prediction in enumerate(predictions[: args.limit], start=1):
        print(f"row_{index}:")
        print(f"  league: {prediction.league}")
        print(f"  home_team: {prediction.home_team}")
        print(f"  away_team: {prediction.away_team}")
        print(f"  event_datetime: {prediction.event_datetime}")
        print(f"  prob_1: {prediction.prob_1}")
        print(f"  prob_2: {prediction.prob_2}")
        print(f"  pred_outcome: {prediction.pred_outcome}")
        print(f"  predicted_home_score: {prediction.predicted_home_score}")
        print(f"  predicted_away_score: {prediction.predicted_away_score}")
        print(f"  avg_points: {prediction.avg_points}")
        print(f"  coef_1: {prediction.coef_1}")
        print(f"  coef_2: {prediction.coef_2}")
        print(f"  coef_3: {prediction.coef_3}")
        print(f"  remaining_tokens: {prediction.remaining_tokens}")
        print(f"  confidence: {prediction.confidence}")
        print("---")


# =============================================================================
# Script Runner Guard
# =============================================================================
if __name__ == "__main__":
    main()
