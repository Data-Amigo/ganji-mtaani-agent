"""This is the browser.py file.

Author: Data-Amigo
Date: 2026-04-16
Description:
This is the reusable browser scraping layer. It launches Playwright/Chromium,
opens a URL, waits for the page to load, collects rendered HTML, handles
failures, and optionally saves raw page snapshots for debugging.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


# =============================================================================
# Browser Fetch Result Model
# =============================================================================
# BrowserFetchResult is the standard response object for the browser layer.
#
# Why this exists:
# - Returning only HTML is not enough for a production scraper.
# - The UI needs status, timing, warnings, and errors.
# - The Scraper Agent will later need structured evidence when a scrape fails.
# - Tests become easier because every browser run returns the same shape.
@dataclass(slots=True)
class BrowserFetchResult:
    """Structured result returned after trying to load a page.

    Attributes:
        url: The URL that Playwright attempted to open.
        status: Current outcome of the fetch, usually "success" or "failed".
        started_at: UTC timestamp when the browser fetch started.
        finished_at: UTC timestamp when the browser fetch finished.
        duration_ms: Total runtime in milliseconds.
        title: Browser page title after loading.
        html: Rendered HTML collected from the browser.
        html_length: Character length of the rendered HTML.
        snapshot_path: Optional file path where raw HTML was saved.
        warnings: Non-fatal issues discovered during the fetch.
        error: Fatal error message if the fetch failed.
    """

    url: str
    status: str
    started_at: datetime
    finished_at: datetime
    duration_ms: int
    title: str = ""
    html: str = ""
    html_length: int = 0
    snapshot_path: str | None = None
    warnings: list[str] = field(default_factory=list)
    error: str | None = None

    @property
    def ok(self) -> bool:
        """Return True when the fetch completed successfully.

        This makes caller code easier to read. Instead of writing
        `result.status == "success"` everywhere, callers can use `result.ok`.
        """

        return self.status == "success"


# =============================================================================
# Main Browser Fetch Function
# =============================================================================
# fetch_page is the reusable browser function for all source scrapers.
#
# Important design choice:
# This function does not parse betting data. It only fetches rendered page
# content. Source-specific parsing will live in parser modules later.
def fetch_page(
    url: str,
    *,
    timeout_ms: int = 60_000,
    wait_until: str = "domcontentloaded",
    settle_ms: int = 3_000,
    headless: bool = True,
    snapshot_path: str | Path | None = None,
) -> BrowserFetchResult:
    """Open a URL with Chromium and return a structured fetch result.

    Args:
        url: Page URL to open.
        timeout_ms: Maximum time to wait for the initial page load.
        wait_until: Playwright load state. For script-heavy pages, start with
            "domcontentloaded". "networkidle" can timeout if ads, trackers, or
            background requests keep running.
        settle_ms: Extra milliseconds to wait after the initial load state.
            This gives JavaScript-heavy pages time to render useful content.
        headless: Whether to run the browser without a visible window.
        snapshot_path: Optional path for saving the raw rendered HTML.

    Returns:
        BrowserFetchResult containing HTML, timing, status, and error details.

    Example:
        result = fetch_page("https://polymarket.com/markets")
        if result.ok:
            print(result.title, result.html_length)
    """

    # -------------------------------------------------------------------------
    # Timing Setup
    # -------------------------------------------------------------------------
    # We track both human-readable UTC timestamps and precise runtime duration.
    # This will be useful in the Streamlit status panel and scraper run history.
    started_at = datetime.now(UTC)
    start = perf_counter()
    warnings: list[str] = []

    try:
        # ---------------------------------------------------------------------
        # Browser Lifecycle
        # ---------------------------------------------------------------------
        # sync_playwright starts the Playwright controller.
        # chromium.launch starts a Chromium browser.
        # page.goto opens the target URL and waits for the selected load state.
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=headless)
            page = browser.new_page()
            page.goto(url, wait_until=wait_until, timeout=timeout_ms)

            # Some sites fire continuous network requests. Instead of waiting for
            # complete network silence, we wait briefly after DOM load so scripts
            # have time to render useful content.
            if settle_ms > 0:
                page.wait_for_timeout(settle_ms)

            # After the page settles, collect basic browser evidence.
            title = page.title()
            html = page.content()
            browser.close()

        # ---------------------------------------------------------------------
        # Result Assembly
        # ---------------------------------------------------------------------
        # If the caller requested a snapshot, save the rendered HTML for later
        # debugging or Scraper Agent review.
        saved_snapshot_path = _save_snapshot(snapshot_path, html)
        finished_at = datetime.now(UTC)
        duration_ms = int((perf_counter() - start) * 1000)

        # Empty HTML is not a fatal exception, but it is suspicious enough to
        # show as a warning in the UI.
        if not html.strip():
            warnings.append("Page returned empty HTML.")

        return BrowserFetchResult(
            url=url,
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=duration_ms,
            title=title,
            html=html,
            html_length=len(html),
            snapshot_path=saved_snapshot_path,
            warnings=warnings,
        )

    # -------------------------------------------------------------------------
    # Error Handling
    # -------------------------------------------------------------------------
    # We return failed BrowserFetchResult objects instead of raising errors.
    # This lets Streamlit show a clean error panel instead of crashing the app.
    except PlaywrightTimeoutError as exc:
        return _failed_result(url, started_at, start, f"Timed out loading page: {exc}")
    except Exception as exc:
        return _failed_result(url, started_at, start, str(exc))


# =============================================================================
# Snapshot Helper
# =============================================================================
# Snapshots are raw rendered HTML files saved for debugging. They are useful when
# selectors break or when we want to compare current page structure to an older
# successful scrape.
def _save_snapshot(snapshot_path: str | Path | None, html: str) -> str | None:
    """Save raw HTML to disk when a snapshot path is provided.

    Args:
        snapshot_path: File path where HTML should be written, or None.
        html: Rendered HTML collected from the browser.

    Returns:
        The saved file path as a string, or None if snapshots are disabled.
    """

    if snapshot_path is None:
        return None

    path = Path(snapshot_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
    return str(path)


# =============================================================================
# Failed Result Helper
# =============================================================================
# This helper keeps every failure response consistent. The UI can rely on the
# same fields whether a page loaded successfully or failed.
def _failed_result(url: str, started_at: datetime, start: float, error: str) -> BrowserFetchResult:
    """Create a BrowserFetchResult for a failed browser run.

    Args:
        url: URL that failed to load.
        started_at: UTC timestamp captured before the browser work began.
        start: perf_counter value captured before the browser work began.
        error: Human-readable error message.

    Returns:
        BrowserFetchResult with status="failed" and error details populated.
    """

    finished_at = datetime.now(UTC)
    duration_ms = int((perf_counter() - start) * 1000)

    return BrowserFetchResult(
        url=url,
        status="failed",
        started_at=started_at,
        finished_at=finished_at,
        duration_ms=duration_ms,
        error=error,
    )
