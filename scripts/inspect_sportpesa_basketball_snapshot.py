"""This is the inspect_sportpesa_basketball_snapshot.py file.

Author: Data-Amigo
Date: 2026-05-01
Description:
This script fetches the live SportPesa basketball page with the shared browser
layer, saves an optional snapshot/screenshot, and prints the first rendered row
samples so we can define the stable basketball parser fields from real output.
"""

from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ganji_mtaani_agent.scrapers.browser import fetch_page
from ganji_mtaani_agent.scrapers.sources import get_source_config, get_source_target
from playwright.sync_api import sync_playwright


# =============================================================================
# Text Helpers
# =============================================================================
def _clean_text(value: str) -> str:
    """Normalize whitespace inside a text fragment."""

    import re

    return re.sub(r"\s+", " ", value).strip()


# =============================================================================
# Main Inspection Function
# =============================================================================
def main() -> None:
    """Fetch and inspect the live SportPesa basketball page."""

    parser = argparse.ArgumentParser(description="Inspect the live SportPesa basketball page.")
    parser.add_argument("--save-snapshot", action="store_true")
    parser.add_argument("--screenshot", action="store_true")
    parser.add_argument("--settle-ms", type=int, default=None, help="Override extra wait after page load.")
    parser.add_argument("--timeout-ms", type=int, default=60000, help="Maximum page load timeout.")
    args = parser.parse_args()

    source = get_source_config("sportpesa")
    target = get_source_target(source, "basketball_today")

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
        headless=False,
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
    print(f"snapshot_path: {result.snapshot_path}")
    print(f"screenshot_path: {result.screenshot_path}")

    if result.warnings:
        print("warnings:")
        for warning in result.warnings:
            print(f"- {warning}")

    if result.error:
        print(f"error: {result.error}")
        return

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(target.url, wait_until=source.default_wait_until, timeout=args.timeout_ms)
        page.wait_for_timeout(settle_ms)

        candidate_selectors = [
            ".event-row-container",
            ".event-row",
            ".event-bets",
        ]

        print("selector_text_samples:")
        for selector in candidate_selectors:
            locator = page.locator(selector)
            count = min(locator.count(), 6)
            print("---")
            print(f"selector: {selector}")
            print(f"texts_found: {count}")
            for index in range(count):
                try:
                    text = _clean_text(locator.nth(index).inner_text())
                except Exception:
                    text = ""
                if text:
                    print(f"  text_{index + 1}: {text}")

        browser.close()


if __name__ == "__main__":
    main()