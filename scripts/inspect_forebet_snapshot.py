"""This is the inspect_forebet_snapshot.py file.

Author: Data-Amigo
Date: 2026-04-29
Description:
This is a developer inspection script for saved Forebet HTML snapshots. It helps
us understand the structure of Forebet basketball and football pages before we
write the real parser.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from bs4 import BeautifulSoup

# =============================================================================
# Local Import Setup
# =============================================================================
# This lets the script run directly from the repo before the package is fully
# installed in the environment.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


# =============================================================================
# Snapshot Loader
# =============================================================================
# This helper reads the saved HTML snapshot from disk.
def load_snapshot(snapshot_path: Path) -> str:
    """Read a saved HTML snapshot file.

    Args:
        snapshot_path: Path to the saved HTML snapshot.

    Returns:
        The file contents as a string.
    """

    return snapshot_path.read_text(encoding="utf-8", errors="ignore")


# =============================================================================
# Basketball Inspection Helper
# =============================================================================
# Forebet basketball pages use a repeated div-based layout instead of a normal
# table. The main match container we discovered is:
#   div.schema.tbuo.tbbsk
#
# Inside it, the header row is:
#   div.hdrtb.prblh.tbbs-12
#
# The repeated match rows are:
#   div.rcnt.tr_0 and div.rcnt.tr_1
#
# This helper prints exactly those pieces so we can study the structure before
# writing a parser.
def inspect_basketball_snapshot(soup: BeautifulSoup) -> None:
    """Inspect the structure of a Forebet basketball snapshot.

    Args:
        soup: BeautifulSoup object built from the saved HTML.
    """

    container = soup.select_one("div.schema.tbuo.tbbsk")
    if container is None:
        print("Basketball container not found: div.schema.tbuo.tbbsk")
        return

    print("container_found: True")

    header = container.select_one("div.hdrtb.prblh.tbbs-12")
    if header is not None:
        print("header_text:")
        print(header.get_text(" | ", strip=True))
        print()

    headings = container.select("div.heading")
    if headings:
        print("date_sections:")
        for heading in headings[:5]:
            print(f"- {heading.get_text(' ', strip=True)}")
        print()

    rows = container.select("div.rcnt")
    print(f"match_rows_found: {len(rows)}")
    print()

    print("sample_rows:")
    for index, row in enumerate(rows[:8], start=1):
        row_text = row.get_text(" | ", strip=True)
        print(f"row_{index}: {row_text}")
        print("---")


# =============================================================================
# General Snapshot Summary
# =============================================================================
# This helper prints page-level information before sport-specific inspection.
def print_snapshot_summary(snapshot_path: Path, soup: BeautifulSoup, html: str) -> None:
    """Print high-level snapshot information.

    Args:
        snapshot_path: Path to the snapshot file.
        soup: BeautifulSoup object built from the saved HTML.
        html: Raw HTML string.
    """

    title = soup.title.get_text(strip=True) if soup.title else ""
    print(f"snapshot_path: {snapshot_path}")
    print(f"title: {title}")
    print(f"html_length: {len(html)}")
    print(f"tables_found: {len(soup.find_all('table'))}")
    print()


# =============================================================================
# Command-Line Entry Point
# =============================================================================
# This script takes a saved snapshot path and prints useful structure details.
def main() -> None:
    """Run snapshot inspection for a saved Forebet HTML file."""

    parser = argparse.ArgumentParser(description="Inspect a saved Forebet HTML snapshot.")
    parser.add_argument("snapshot_path", help="Path to the saved HTML snapshot file.")
    parser.add_argument(
        "--sport",
        choices=["basketball", "football"],
        default="basketball",
        help="Sport-specific inspection mode. Basketball is the current focus.",
    )
    args = parser.parse_args()

    snapshot_path = Path(args.snapshot_path)
    html = load_snapshot(snapshot_path)
    soup = BeautifulSoup(html, "html.parser")

    print_snapshot_summary(snapshot_path, soup, html)

    if args.sport == "basketball":
        inspect_basketball_snapshot(soup)
    else:
        print("Football inspection mode is not implemented yet.")


# =============================================================================
# Script Runner Guard
# =============================================================================
if __name__ == "__main__":
    main()
