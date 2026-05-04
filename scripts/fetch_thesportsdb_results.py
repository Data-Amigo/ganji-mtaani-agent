"""This is the fetch_thesportsdb_results.py file.

Author: Data-Amigo
Date: 2026-05-04
Description:
This script is a thin inspection runner for the reusable TheSportsDB ingestion
module. It fetches actual result data first, then optionally enriches the first
result with stats, lineup, and player profile data when requested.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from ganji_mtaani_agent.models.thesportsdb import (
    TheSportsDBEventLineupPlayer,
    TheSportsDBEventResult,
    TheSportsDBEventStat,
    TheSportsDBPlayerProfile,
)
from ganji_mtaani_agent.parsers.thesportsdb import (
    normalize_event_lineup,
    normalize_event_results,
    normalize_event_stats,
    normalize_player_profile,
)
from ganji_mtaani_agent.scrapers.thesportsdb import (
    fetch_event_lineup,
    fetch_event_results,
    fetch_event_stats,
    fetch_events_day,
    fetch_lookup_event,
    fetch_lookup_player,
    fetch_player_former_teams,
    fetch_player_honours,
)


# =============================================================================
# CLI Defaults
# =============================================================================
DEFAULT_LIMIT = 5
DEFAULT_SPORT = "Soccer"


# =============================================================================
# CLI Helpers
# =============================================================================
def build_argument_parser() -> argparse.ArgumentParser:
    """Build the command-line interface for the TheSportsDB inspection script."""

    parser = argparse.ArgumentParser(
        description="Fetch and inspect TheSportsDB results and optional enrichments."
    )
    parser.add_argument(
        "--date",
        type=str,
        default=datetime.now().strftime("%Y-%m-%d"),
        help="Event date in YYYY-MM-DD format.",
    )
    parser.add_argument(
        "--sport",
        type=str,
        default=DEFAULT_SPORT,
        help="Sport filter such as Soccer or Basketball.",
    )
    parser.add_argument(
        "--league-id",
        type=str,
        default=None,
        help="Optional TheSportsDB league id filter.",
    )
    parser.add_argument(
        "--event-id",
        type=str,
        default=None,
        help="Optional event id to inspect one specific event and its enrichments.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_LIMIT,
        help="Number of normalized result rows to print.",
    )
    parser.add_argument(
        "--include-stats",
        action="store_true",
        help="Fetch and print event stats for the first result or selected event.",
    )
    parser.add_argument(
        "--include-lineup",
        action="store_true",
        help="Fetch and print lineup players for the first result or selected event.",
    )
    parser.add_argument(
        "--include-players",
        action="store_true",
        help="Fetch and print one player profile from the lineup when available.",
    )
    return parser


# =============================================================================
# Output Helpers
# =============================================================================
def print_result_preview(results: list[TheSportsDBEventResult]) -> None:
    """Print a readable preview of normalized event results."""

    print(f"normalized_results: {len(results)}")

    for index, row in enumerate(results, start=1):
        print("---")
        print(f"result_{index}:")
        print(f"  event_id: {row.event_id}")
        print(f"  sport: {row.sport}")
        print(f"  league: {row.league}")
        print(f"  season: {row.season}")
        print(f"  event_name: {row.event_name}")
        print(f"  event_date: {row.event_date}")
        print(f"  event_time: {row.event_time}")
        print(f"  home_team: {row.home_team}")
        print(f"  away_team: {row.away_team}")
        print(f"  home_score: {row.home_score}")
        print(f"  away_score: {row.away_score}")
        print(f"  status: {row.status}")
        print(f"  progress: {row.progress}")
        print(f"  venue: {row.venue}")
        print(f"  winner: {row.winner}")
        print(f"  confidence: {row.confidence}")


def print_stat_preview(stats: list[TheSportsDBEventStat]) -> None:
    """Print a readable preview of normalized event stats."""

    print(f"normalized_stats: {len(stats)}")
    for index, row in enumerate(stats[:10], start=1):
        print("---")
        print(f"stat_{index}:")
        print(f"  stat_name: {row.stat_name}")
        print(f"  home_value: {row.home_value}")
        print(f"  away_value: {row.away_value}")
        print(f"  confidence: {row.confidence}")


def print_lineup_preview(lineup: list[TheSportsDBEventLineupPlayer]) -> None:
    """Print a readable preview of normalized lineup players."""

    print(f"normalized_lineup_players: {len(lineup)}")
    for index, row in enumerate(lineup[:10], start=1):
        print("---")
        print(f"lineup_player_{index}:")
        print(f"  team_name: {row.team_name}")
        print(f"  player_id: {row.player_id}")
        print(f"  player_name: {row.player_name}")
        print(f"  position: {row.position}")
        print(f"  shirt_number: {row.shirt_number}")
        print(f"  role: {row.role}")
        print(f"  status: {row.status}")
        print(f"  confidence: {row.confidence}")


def print_player_profile(profile: TheSportsDBPlayerProfile | None) -> None:
    """Print a readable preview of one normalized player profile."""

    if profile is None:
        print("player_profile: None")
        return

    print("player_profile:")
    print(f"  player_id: {profile.player_id}")
    print(f"  player_name: {profile.player_name}")
    print(f"  team_name: {profile.team_name}")
    print(f"  nationality: {profile.nationality}")
    print(f"  date_of_birth: {profile.date_of_birth}")
    print(f"  position: {profile.position}")
    print(f"  former_teams: {profile.former_teams[:10]}")
    print(f"  honours: {profile.honours[:10]}")
    print(f"  confidence: {profile.confidence}")


# =============================================================================
# Main Entry Point
# =============================================================================
def main() -> None:
    """Fetch live TheSportsDB records and print a normalized preview."""

    parser = build_argument_parser()
    args = parser.parse_args()

    if args.event_id:
        raw_event = fetch_lookup_event(args.event_id)
        results = normalize_event_results(raw_event)
        if not results:
            raw_event_results = fetch_event_results(args.event_id)
            results = normalize_event_results(raw_event_results)
    else:
        raw_day = fetch_events_day(args.date, sport=args.sport, league_id=args.league_id)
        results = normalize_event_results(raw_day)

    limited_results = results[: args.limit]
    print_result_preview(limited_results)

    if not limited_results:
        return

    selected_event = limited_results[0]

    if args.include_stats:
        raw_stats = fetch_event_stats(selected_event.event_id)
        stats = normalize_event_stats(raw_stats, event_id=selected_event.event_id, sport=selected_event.sport)
        print_stat_preview(stats)

    lineup: list[TheSportsDBEventLineupPlayer] = []
    if args.include_lineup or args.include_players:
        raw_lineup = fetch_event_lineup(selected_event.event_id)
        lineup = normalize_event_lineup(raw_lineup, event_id=selected_event.event_id, sport=selected_event.sport)
        print_lineup_preview(lineup)

    if args.include_players and lineup:
        first_player_with_id = next((row for row in lineup if row.player_id), None)
        if first_player_with_id is not None:
            raw_player = fetch_lookup_player(first_player_with_id.player_id)
            raw_former_teams = fetch_player_former_teams(first_player_with_id.player_id)
            raw_honours = fetch_player_honours(first_player_with_id.player_id)
            profile = normalize_player_profile(raw_player, raw_former_teams, raw_honours)
            print_player_profile(profile)


if __name__ == "__main__":
    main()
