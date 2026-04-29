"""This is the inspect_forebet_football_parser.py file.

Author: Data-Amigo
Date: 2026-04-29
Description:
This is a small developer script that runs the first Forebet football parser
against a saved HTML snapshot and prints a few parsed records for inspection.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# =============================================================================
# Local Import Setup
# =============================================================================
# This lets the script run directly from the repo before the package is fully
# installed in the environment.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ganji_mtaani_agent.parsers.forebet import parse_forebet_football


# =============================================================================
# Snapshot Loader
# =============================================================================
def load_snapshot(snapshot_path: Path) -> str:
    """Read a saved HTML snapshot file from disk."""

    return snapshot_path.read_text(encoding="utf-8", errors="ignore")


# =============================================================================
# Command-Line Entry Point
# =============================================================================
def main() -> None:
    """Run the first football parser against a saved Forebet snapshot."""

    parser = argparse.ArgumentParser(description="Inspect parsed Forebet football rows.")
    parser.add_argument("snapshot_path", help="Path to the saved football HTML snapshot file.")
    parser.add_argument("--limit", type=int, default=5, help="How many parsed rows to print.")
    args = parser.parse_args()

    snapshot_path = Path(args.snapshot_path)
    html = load_snapshot(snapshot_path)
    predictions = parse_forebet_football(html)

    print(f"snapshot_path: {snapshot_path}")
    print(f"parsed_rows: {len(predictions)}")
    print()

    for index, prediction in enumerate(predictions[: args.limit], start=1):
        print(f"row_{index}:")
        print(f"  league: {prediction.league}")
        print(f"  home_team: {prediction.home_team}")
        print(f"  away_team: {prediction.away_team}")
        print(f"  event_datetime: {prediction.event_datetime}")
        print(f"  prob_1: {prediction.prob_1}")
        print(f"  prob_x: {prediction.prob_x}")
        print(f"  prob_2: {prediction.prob_2}")
        print(f"  pred_outcome: {prediction.pred_outcome}")
        print(f"  predicted_home_score: {prediction.predicted_home_score}")
        print(f"  predicted_away_score: {prediction.predicted_away_score}")
        print(f"  correct_score_text: {prediction.correct_score_text}")
        print(f"  avg_goals: {prediction.avg_goals}")
        print(f"  weather: {prediction.weather}")
        print(f"  coef_1: {prediction.coef_1}")
        print(f"  coef_x: {prediction.coef_x}")
        print(f"  coef_2: {prediction.coef_2}")
        print(f"  coef_extra: {prediction.coef_extra}")
        print(f"  remaining_tokens: {prediction.remaining_tokens}")
        print(f"  confidence: {prediction.confidence}")
        print("---")


# =============================================================================
# Script Runner Guard
# =============================================================================
if __name__ == "__main__":
    main()
