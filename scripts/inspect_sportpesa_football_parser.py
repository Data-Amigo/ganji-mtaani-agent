"""This is the inspect_sportpesa_football_parser.py file.

Author: Data-Amigo
Date: 2026-05-01
Description:
This script tests the SportPesa football parser against a saved HTML snapshot
and prints the first parsed rows so we can verify the stable fields before
connecting the parser to a live ingestion workflow.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ganji_mtaani_agent.parsers.sportpesa import parse_sportpesa_football


# =============================================================================
# Main Parser Inspection Function
# =============================================================================
def main() -> None:
    """Run the SportPesa football parser against a saved snapshot."""

    parser = argparse.ArgumentParser(description="Inspect the SportPesa football parser output.")
    parser.add_argument(
        "snapshot_path",
        nargs="?",
        default=r"data/raw/sportpesa/football_today/20260430_125807.html",
        help="Path to a saved SportPesa football HTML snapshot.",
    )
    parser.add_argument("--limit", type=int, default=5, help="Number of parsed rows to print.")
    args = parser.parse_args()

    snapshot_path = Path(args.snapshot_path)
    html = snapshot_path.read_text(encoding="utf-8", errors="replace")
    parsed_rows = parse_sportpesa_football(html)

    print(f"snapshot_path: {snapshot_path}")
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


if __name__ == "__main__":
    main()
