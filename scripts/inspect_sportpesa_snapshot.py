"""This is the inspect_sportpesa_snapshot.py file.

Author: Data-Amigo
Date: 2026-04-30
Description:
This script fetches the SportPesa football page with a lightweight HTTP request,
then prints a structure-oriented inspection summary so we can identify stable
fixture fields before building the SportPesa scraper and parser.
"""

from __future__ import annotations

# =============================================================================
# Imports
# =============================================================================
import argparse
import re
from datetime import UTC, datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen


# =============================================================================
# Text Cleaning Helpers
# =============================================================================
def _clean_text(value: str) -> str:
    """Normalize whitespace inside a text fragment."""

    return re.sub(r"\s+", " ", value).strip()


# =============================================================================
# Lightweight HTML Fetch Helper
# =============================================================================
def fetch_html(url: str, timeout_seconds: int = 60) -> tuple[str, str]:
    """Fetch HTML from a public page using the standard library.

    Returns:
        A tuple of (html, page_title).
    """

    request = Request(
        url,
        headers={
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        },
        method="GET",
    )

    with urlopen(request, timeout=timeout_seconds) as response:
        html = response.read().decode("utf-8", errors="replace")

    title_match = re.search(r"<title[^>]*>(.*?)</title>", html, flags=re.IGNORECASE | re.DOTALL)
    title = _clean_text(title_match.group(1)) if title_match else ""

    return html, title


# =============================================================================
# Lightweight HTML Inspection Parser
# =============================================================================
class SportPesaInspectionParser(HTMLParser):
    """Collect headings, table headers, text lines, and class hints from HTML."""

    def __init__(self) -> None:
        super().__init__()
        self._stack: list[dict[str, object]] = []
        self.headings: list[str] = []
        self.table_headers: list[str] = []
        self.text_lines: list[str] = []
        self.class_hints: list[str] = []
        self._seen_headings: set[str] = set()
        self._seen_headers: set[str] = set()
        self._seen_text_lines: set[str] = set()
        self._seen_class_hints: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        classes = attrs_dict.get("class", "") or ""
        class_list = [item for item in classes.split() if item]
        self._stack.append({"tag": tag, "classes": class_list, "buffer": []})

    def handle_data(self, data: str) -> None:
        if not self._stack:
            return

        if data.strip():
            current = self._stack[-1]
            buffer = current["buffer"]
            if isinstance(buffer, list):
                buffer.append(data)

    def handle_endtag(self, tag: str) -> None:
        if not self._stack:
            return

        current = self._stack.pop()
        current_tag = current.get("tag")
        if current_tag != tag:
            return

        raw_text = " ".join(current.get("buffer", []))
        text = _clean_text(raw_text)
        classes = current.get("classes", [])
        class_hint = ".".join(classes) if isinstance(classes, list) else ""

        if tag in {"h1", "h2", "h3", "h4"} and text and text not in self._seen_headings:
            self._seen_headings.add(text)
            self.headings.append(text)

        if tag == "th" and text and text not in self._seen_headers:
            self._seen_headers.add(text)
            self.table_headers.append(text)

        if text and len(text) >= 12 and text not in self._seen_text_lines:
            self._seen_text_lines.add(text)
            self.text_lines.append(text)

        if class_hint and text and len(text) >= 20 and class_hint not in self._seen_class_hints:
            lowered = text.casefold()
            if any(token in lowered for token in ["odds", "football", "jackpot", "vs", "premier", "draw"]):
                self._seen_class_hints.add(class_hint)
                self.class_hints.append(class_hint)


# =============================================================================
# Inspection Helpers
# =============================================================================
def _extract_candidate_fixture_lines(text_lines: list[str], limit: int = 15) -> list[str]:
    """Filter raw text lines down to likely fixture/odds lines."""

    candidates: list[str] = []

    for text in text_lines:
        lowered = text.casefold()
        looks_like_fixture = (
            any(token in lowered for token in [" vs ", " v ", " x "])
            or bool(re.search(r"\b\d{1,2}:\d{2}\b", text))
            or bool(re.search(r"\b\d+\.\d{2}\b", text))
        )

        if looks_like_fixture:
            candidates.append(text)

        if len(candidates) >= limit:
            break

    return candidates


# =============================================================================
# Main Inspection Function
# =============================================================================
def main() -> None:
    """Fetch SportPesa and print a page-structure inspection summary."""

    parser = argparse.ArgumentParser(description="Inspect the SportPesa football page structure.")
    parser.add_argument(
        "--url",
        default="https://www.sportpesa.co.ke/sports/football",
        help="Optional URL override for the SportPesa football page.",
    )
    parser.add_argument("--save-snapshot", action="store_true")
    parser.add_argument("--timeout-seconds", type=int, default=60, help="Maximum HTTP timeout in seconds.")
    args = parser.parse_args()

    html, title = fetch_html(args.url, timeout_seconds=args.timeout_seconds)

    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    snapshot_path = None

    if args.save_snapshot:
        artifact_folder = Path("data") / "raw" / "sportpesa" / "football_today"
        artifact_folder.mkdir(parents=True, exist_ok=True)
        snapshot_path = artifact_folder / f"{timestamp}.html"
        snapshot_path.write_text(html, encoding="utf-8")

    print("source: SportPesa")
    print("target: Football Odds Today")
    print(f"url: {args.url}")
    print("status: success")
    print(f"title: {title}")
    print(f"html_length: {len(html)}")
    print(f"snapshot_path: {snapshot_path}")

    inspection_parser = SportPesaInspectionParser()
    inspection_parser.feed(html)

    headings = inspection_parser.headings[:20]
    table_headers = inspection_parser.table_headers[:20]
    fixture_lines = _extract_candidate_fixture_lines(inspection_parser.text_lines, limit=15)
    class_hints = inspection_parser.class_hints[:25]

    print(f"headings_found: {len(headings)}")
    for index, heading in enumerate(headings, start=1):
        print(f"heading_{index}: {heading}")

    print(f"table_headers_found: {len(table_headers)}")
    for index, header in enumerate(table_headers, start=1):
        print(f"table_header_{index}: {header}")

    print(f"candidate_fixture_lines_found: {len(fixture_lines)}")
    for index, line in enumerate(fixture_lines, start=1):
        print(f"fixture_line_{index}: {line}")

    print(f"class_hints_found: {len(class_hints)}")
    for index, class_hint in enumerate(class_hints, start=1):
        print(f"class_hint_{index}: {class_hint}")


if __name__ == "__main__":
    main()
