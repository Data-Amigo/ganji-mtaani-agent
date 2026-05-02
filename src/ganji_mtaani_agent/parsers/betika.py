"""This is the betika.py parser file.

Author: Data-Amigo
Date: 2026-05-02
Description:
This parser module extracts the first stable football odds fields from the
rendered Betika football page HTML. Betika is heavily app-rendered, so the V1
parser intentionally works from the rendered body text sequence instead of
relying on fragile CSS selectors.
"""

from __future__ import annotations

import re

from bs4 import BeautifulSoup

from ganji_mtaani_agent.models.betika import BetikaFootballOdds


# =============================================================================
# Small Conversion Helpers
# =============================================================================
def _to_float(value: str) -> float | None:
    """Convert a token to float when possible."""

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_int_from_plus(value: str) -> int | None:
    """Convert a token like '+85' into the integer 85 when possible."""

    match = re.fullmatch(r"\+(\d+)", value.strip())
    if not match:
        return None
    return int(match.group(1))


def _clean_line(value: str) -> str:
    """Normalize whitespace inside a text line."""

    return re.sub(r"\s+", " ", value).strip()


def _extract_text_lines(html: str) -> list[str]:
    """Extract non-empty rendered text lines from HTML."""

    soup = BeautifulSoup(html, "html.parser")
    raw_text = soup.get_text("\n", strip=True)
    return [_clean_line(line) for line in raw_text.splitlines() if _clean_line(line)]


def _looks_like_league_header(lines: list[str], index: int) -> bool:
    """Return True when the current position looks like a league header block."""

    return (
        index + 3 < len(lines)
        and lines[index + 1] == "•"
        and lines[index + 3].isdigit()
        and not lines[index].startswith("Starts")
    )


# =============================================================================
# Main Betika Football Parser
# =============================================================================
def parse_betika_football(html: str) -> list[BetikaFootballOdds]:
    """Parse Betika football odds from rendered page HTML.

    Expected V1 text pattern per league section:
    - League country
    - Bullet separator
    - League name
    - Match count
    - Repeated match blocks of:
      Starts...
      1 • X • 2
      Home team
      Away team
      Home odds
      Draw odds
      Away odds
      +extra markets
    """

    lines = _extract_text_lines(html)
    if not lines:
        return []

    try:
        start_index = lines.index("Both Teams To Score") + 1
    except ValueError:
        start_index = 0

    index = start_index
    current_league = "Unknown League"
    parsed_rows: list[BetikaFootballOdds] = []

    while index < len(lines):
        if _looks_like_league_header(lines, index):
            current_league = f"{lines[index]} {lines[index + 2]}"
            index += 4
            continue

        if index + 7 < len(lines) and lines[index].startswith("Starts"):
            market_header = lines[index + 1]
            if market_header != "1 • X • 2":
                index += 1
                continue

            home_team = lines[index + 2]
            away_team = lines[index + 3]
            home_odds = _to_float(lines[index + 4])
            draw_odds = _to_float(lines[index + 5])
            away_odds = _to_float(lines[index + 6])
            extra_market_count = _to_int_from_plus(lines[index + 7])

            if home_odds is None or draw_odds is None or away_odds is None:
                index += 1
                continue

            raw_tokens = lines[index : index + 8]
            parsed_rows.append(
                BetikaFootballOdds(
                    source="betika",
                    sport="football",
                    league=current_league,
                    event_datetime_text=lines[index],
                    home_team=home_team,
                    away_team=away_team,
                    home_odds=home_odds,
                    draw_odds=draw_odds,
                    away_odds=away_odds,
                    extra_market_count=extra_market_count,
                    raw_text=" | ".join(raw_tokens),
                    confidence=0.95,
                )
            )
            index += 8
            continue

        index += 1

    return parsed_rows
