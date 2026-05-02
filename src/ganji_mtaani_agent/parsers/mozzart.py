"""This is the mozzart.py parser file.

Author: Data-Amigo
Date: 2026-05-02
Description:
This parser module extracts the first stable football and basketball odds
fields from the rendered Mozzart live page HTML. The page is heavily mobile-
oriented, so the V1 parser intentionally works from the rendered body text
sequence rather than fragile selectors.
"""

from __future__ import annotations

import re

from bs4 import BeautifulSoup

from ganji_mtaani_agent.models.mozzart import MozzartBasketballOdds, MozzartFootballOdds


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
    """Convert a token like '+224' into the integer 224 when possible."""

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


def _looks_like_league_label(value: str) -> bool:
    """Return True when a line looks like a Mozzart league label."""

    return bool(re.fullmatch(r"[A-Za-z&.'\- ]+(?:\.\.\.)?\s+\d+(?:\s+[A-Za-z]+)?", value))


def _parse_live_rows(
    html: str,
    sport_section_pattern: str,
    sport: str,
) -> list[dict[str, object]]:
    """Parse repeated live Mozzart rows for a given sport section."""

    lines = _extract_text_lines(html)
    if not lines:
        return []

    try:
        start_index = next(i for i, line in enumerate(lines) if re.fullmatch(sport_section_pattern, line)) + 1
    except StopIteration:
        return []

    index = start_index
    parsed_rows: list[dict[str, object]] = []

    while index < len(lines):
        line = lines[index]

        if line.startswith("Go To Mobile Plus") or line.startswith("Mobile Plus") or line.startswith("T SPORTS"):
            break

        if not _looks_like_league_label(line):
            index += 1
            continue

        if index + 10 >= len(lines):
            break

        league = lines[index]
        status_tokens = lines[index + 1 : index + 4]
        home_team = lines[index + 4]
        away_team = lines[index + 5]
        score_tokens = lines[index + 6 : index + 10]
        extra_market_count = _to_int_from_plus(lines[index + 10])

        if len(status_tokens) < 3 or len(score_tokens) < 4:
            index += 1
            continue

        match_status = " ".join(status_tokens)
        score_text = " ".join(score_tokens)

        next_line = lines[index + 11] if index + 11 < len(lines) else ""
        if next_line == "There are currently no odds for this event.":
            index += 12
            continue

        if index + 16 >= len(lines):
            break

        if lines[index + 11] != "1" or lines[index + 13] != "X" or lines[index + 15] != "2":
            index += 1
            continue

        home_odds = _to_float(lines[index + 12])
        draw_odds = _to_float(lines[index + 14])
        away_odds = _to_float(lines[index + 16])

        if home_odds is None or draw_odds is None or away_odds is None:
            index += 1
            continue

        raw_tokens = lines[index : index + 17]
        parsed_rows.append(
            {
                "source": "mozzart",
                "sport": sport,
                "league": league,
                "match_status": match_status,
                "home_team": home_team,
                "away_team": away_team,
                "score_text": score_text,
                "extra_market_count": extra_market_count,
                "home_odds": home_odds,
                "draw_odds": draw_odds,
                "away_odds": away_odds,
                "raw_text": " | ".join(raw_tokens),
                "confidence": 0.9,
            }
        )
        index += 17

    return parsed_rows


# =============================================================================
# Main Mozzart Parsers
# =============================================================================
def parse_mozzart_football(html: str) -> list[MozzartFootballOdds]:
    """Parse Mozzart live football odds from rendered page HTML."""

    parsed_dicts = _parse_live_rows(
        html=html,
        sport_section_pattern=r"Football - \d+",
        sport="football",
    )
    return [MozzartFootballOdds(**row) for row in parsed_dicts]


def parse_mozzart_basketball(html: str) -> list[MozzartBasketballOdds]:
    """Parse Mozzart live basketball odds from rendered page HTML."""

    parsed_dicts = _parse_live_rows(
        html=html,
        sport_section_pattern=r"Basketball - \d+",
        sport="basketball",
    )
    return [MozzartBasketballOdds(**row) for row in parsed_dicts]
