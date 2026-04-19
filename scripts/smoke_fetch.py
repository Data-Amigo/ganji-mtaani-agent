"""This is the smoke_fetch.py file.

Author: Data-Amigo
Date: 2026-04-16
Description:
This is a small manual test script for the Playwright browser foundation. It
confirms that the browser layer can open a source URL, collect page metadata,
and optionally save a raw HTML snapshot before we build the full Streamlit UI.
"""

from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path

# =============================================================================
# Local Import Setup
# =============================================================================
# This lets the script run before the package is installed with pip.
# Later, once the environment is fully installed, this can be removed if desired.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ganji_mtaani_agent.scrapers.browser import fetch_page
from ganji_mtaani_agent.scrapers.sources import get_source_config


# =============================================================================
# Command-Line Entry Point
# =============================================================================
# This script can be run from PowerShell like:
#
# python scripts\smoke_fetch.py --source forebet --save-snapshot
#
# It is useful before Streamlit exists because it tests the browser foundation
# directly from the terminal.
def main() -> None:
    """Run a small browser-fetch test from the terminal.

    The function performs four steps:
    1. Read command-line options.
    2. Resolve the selected source and URL.
    3. Call the reusable Playwright fetch_page function.
    4. Print a simple summary for debugging.
    """

    # -------------------------------------------------------------------------
    # CLI Argument Setup
    # -------------------------------------------------------------------------
    # argparse defines what options the script accepts from the terminal.
    # --source chooses the registered source.
    # --url lets us override the default source URL for testing.
    # --save-snapshot saves the raw rendered HTML under data/raw/.
    # --wait-until lets us test different Playwright load strategies.
    # --settle-ms lets JavaScript render after the initial page load.
    parser = argparse.ArgumentParser(description="Smoke test the Playwright browser fetcher.")
    parser.add_argument("--source", choices=["forebet", "polymarket"], default="forebet")
    parser.add_argument("--url", help="Optional URL override for the selected source.")
    parser.add_argument("--save-snapshot", action="store_true")
    parser.add_argument(
        "--wait-until",
        choices=["commit", "domcontentloaded", "load", "networkidle"],
        default="domcontentloaded",
        help="Playwright page load state. Use domcontentloaded first for script-heavy sites.",
    )
    parser.add_argument(
        "--settle-ms",
        type=int,
        default=3000,
        help="Extra milliseconds to wait after the page reaches the selected load state.",
    )
    parser.add_argument(
        "--timeout-ms",
        type=int,
        default=60000,
        help="Maximum milliseconds to wait for the selected page load state.",
    )
    args = parser.parse_args()

    # -------------------------------------------------------------------------
    # Source and URL Resolution
    # -------------------------------------------------------------------------
    # The selected source gives us a default URL. If --url is provided, we use
    # that instead. This is how we test different pages from the same source
    # without editing Python code.
    source = get_source_config(args.source)
    url = args.url or source.default_url
    snapshot_path = None

    # -------------------------------------------------------------------------
    # Optional Snapshot Path
    # -------------------------------------------------------------------------
    # A timestamped filename prevents one smoke test from overwriting another.
    # data/raw/ is ignored by git because snapshots can become large.
    if args.save_snapshot:
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        snapshot_path = Path("data") / "raw" / args.source / f"{timestamp}.html"

    # -------------------------------------------------------------------------
    # Browser Fetch
    # -------------------------------------------------------------------------
    # fetch_page is the same reusable function that Forebet, Polymarket, and the
    # future Streamlit UI will call.
    result = fetch_page(
        url,
        timeout_ms=args.timeout_ms,
        wait_until=args.wait_until,
        settle_ms=args.settle_ms,
        snapshot_path=snapshot_path,
    )

    # -------------------------------------------------------------------------
    # Terminal Output
    # -------------------------------------------------------------------------
    # Keep output simple so we can quickly see if the browser layer worked.
    print(f"source: {source.display_name}")
    print(f"url: {result.url}")
    print(f"status: {result.status}")
    print(f"title: {result.title}")
    print(f"html_length: {result.html_length}")
    print(f"duration_ms: {result.duration_ms}")
    print(f"snapshot_path: {result.snapshot_path}")

    # -------------------------------------------------------------------------
    # Warning and Error Output
    # -------------------------------------------------------------------------
    # Warnings are non-fatal issues. Errors mean the fetch failed.
    if result.warnings:
        print("warnings:")
        for warning in result.warnings:
            print(f"- {warning}")

    if result.error:
        print(f"error: {result.error}")


# =============================================================================
# Script Runner Guard
# =============================================================================
# This ensures main() only runs when this file is executed directly, not when the
# file is imported by tests or another Python module.
if __name__ == "__main__":
    main()
