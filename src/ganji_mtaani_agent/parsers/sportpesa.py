"""This is the sportpesa.py parser file.

Author: Data-Amigo
Date: 2026-05-01
Description:
This parser module extracts the first stable football and basketball odds
fields from live SportPesa page HTML. It combines JSON-LD fixture identity data
with rendered DOM row text to produce structured SportPesa odds records.
"""

from __future__ import annotations

import json
import re
from typing import Any

from bs4 import BeautifulSoup

from ganji_mtaani_agent.models.sportpesa import SportPesaBasketballOdds, SportPesaFootballOdds


# =============================================================================
# Small Conversion Helpers
# =============================================================================
def _to_float(value: str) -> float | None:
    """Convert a token to float when possible."""

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _clean_text(value: str) -> str:
    """Normalize whitespace inside a text fragment."""

    return re.sub(r"\s+", " ", value).strip()


# =============================================================================
# JSON-LD Fixture Parsing
# =============================================================================
def _parse_json_ld_record(payload: dict[str, Any]) -> dict[str, str | None] | None:
    """Extract stable fixture identity fields from one SportPesa JSON-LD record."""

    name = str(payload.get("name") or "")
    if " - " not in name:
        return None

    home_team, away_team = [part.strip() for part in name.split(" - ", 1)]
    url = payload.get("url")
    game_id_match = re.search(r"/games/(\d+)/markets", str(url or ""))
    location = payload.get("location") or {}
    address = location.get("address") or {}

    return {
        "home_team": home_team,
        "away_team": away_team,
        "league": str(address.get("name") or "").strip() or None,
        "game_url": str(url).strip() if url else None,
        "game_url_id": game_id_match.group(1) if game_id_match else None,
    }


# =============================================================================
# Visible Row Parsing
# =============================================================================
def _parse_football_event_row_text(row_text: str) -> dict[str, Any] | None:
    """Parse the visible SportPesa football event row text into stable odds fields."""

    normalized = _clean_text(row_text)

    pattern = re.compile(
        r'^(?:Boosted Odds\s+)?'
        r'(?P<datetime>\d{2}/\d{2}/\d{2}\s+-\s+\d{2}:\d{2})\s+\|\s+'
        r'ID:\s*(?P<game_id>\d+)\s+'
        r'.*?3\s+Way\s+"\s+>\s+.*?\s+'
        r'(?P<home_odds>\d+\.\d{2})\s+Draw\s+(?P<draw_odds>\d+\.\d{2})\s+.*?\s+(?P<away_odds>\d+\.\d{2})\s+'
        r'Double\s+Chance\s+"\s+>\s+1\s+or\s+X\s+(?P<home_or_draw_odds>\d+\.\d{2})\s+'
        r'X\s+or\s+2\s+(?P<draw_or_away_odds>\d+\.\d{2})\s+1\s+or\s+2\s+(?P<home_or_away_odds>\d+\.\d{2})\s+'
        r'Over/Under\s+2\.5\s+"\s+>\s+OVER\s+2\.50\s+(?P<over_2_5_odds>\d+\.\d{2})\s+'
        r'UNDER\s+2\.50\s+(?P<under_2_5_odds>\d+\.\d{2})\s+'
        r'Both\s+Teams\s+To\s+Score\s+"\s+>\s+YES\s+\(GG\)\s+(?P<btts_yes_odds>\d+\.\d{2})\s+'
        r'NO\s+\(NG\)\s+(?P<btts_no_odds>\d+\.\d{2})',
        flags=re.IGNORECASE,
    )
    match = pattern.search(normalized)

    if not match:
        return None

    return {
        "event_datetime": match.group("datetime"),
        "game_id": match.group("game_id"),
        "home_odds": _to_float(match.group("home_odds")),
        "draw_odds": _to_float(match.group("draw_odds")),
        "away_odds": _to_float(match.group("away_odds")),
        "home_or_draw_odds": _to_float(match.group("home_or_draw_odds")),
        "draw_or_away_odds": _to_float(match.group("draw_or_away_odds")),
        "home_or_away_odds": _to_float(match.group("home_or_away_odds")),
        "over_2_5_odds": _to_float(match.group("over_2_5_odds")),
        "under_2_5_odds": _to_float(match.group("under_2_5_odds")),
        "btts_yes_odds": _to_float(match.group("btts_yes_odds")),
        "btts_no_odds": _to_float(match.group("btts_no_odds")),
        "raw_text": normalized,
    }


def _parse_basketball_event_row_text(row_text: str) -> dict[str, Any] | None:
    """Parse the visible SportPesa basketball event row text into stable odds fields.

    The rendered basketball row includes league text, fixture text, a market
    count token, the market name, both team names again, and then the final two
    decimal odds we care about. For V1 we intentionally avoid re-splitting team
    names from this noisy text because JSON-LD already gives us cleaner team
    identity data.
    """

    normalized = _clean_text(row_text)

    match = re.search(
        r'^(?P<prefix>.*?)'
        r'(?P<datetime>\d{2}/\d{2}/\d{2}\s+-\s+\d{2}:\d{2})\s+\|\s+'
        r'ID:\s*(?P<game_id>\d+)\s+',
        normalized,
        flags=re.IGNORECASE,
    )
    if not match:
        return None

    decimal_tokens = re.findall(r'\d+\.\d{2}', normalized)
    if len(decimal_tokens) < 2:
        return None

    prefix = _clean_text(match.group('prefix'))
    league = prefix if prefix else None
    home_odds_token, away_odds_token = decimal_tokens[-2:]

    return {
        'league_hint': league,
        'event_datetime': match.group('datetime'),
        'game_id': match.group('game_id'),
        'home_odds': _to_float(home_odds_token),
        'away_odds': _to_float(away_odds_token),
        'raw_text': normalized,
    }


# =============================================================================
# HTML Extraction Helpers
# =============================================================================
def _extract_json_ld_fixtures(soup: BeautifulSoup) -> list[dict[str, str | None]]:
    """Collect structured fixture identity records from JSON-LD scripts."""

    fixtures: list[dict[str, str | None]] = []

    for script in soup.select('script[type="application/ld+json"]'):
        raw_text = script.string or script.get_text()
        try:
            payload = json.loads(raw_text)
        except Exception:
            continue

        if isinstance(payload, dict) and payload.get("@type") == "SportsEvent":
            parsed_fixture = _parse_json_ld_record(payload)
            if parsed_fixture is not None:
                fixtures.append(parsed_fixture)

    return fixtures


def _extract_event_row_texts(soup: BeautifulSoup) -> list[str]:
    """Collect visible rendered event row texts from the SportPesa page."""

    rows: list[str] = []

    for element in soup.select(".event-row-container"):
        text = _clean_text(element.get_text(" ", strip=True))
        if text and re.search(r"\bID:\s*\d+\b", text):
            rows.append(text)

    return rows


# =============================================================================
# Main SportPesa Snapshot Parsers
# =============================================================================
def parse_sportpesa_football(html: str) -> list[SportPesaFootballOdds]:
    """Parse SportPesa football odds from saved or live page HTML.

    Important V1 assumption:
    SportPesa exposes fixture identity in JSON-LD and visible odds rows in a
    separate rendered DOM layer. The two layers currently align by page order,
    not by the same visible numeric id, so we join them positionally for V1.
    """

    soup = BeautifulSoup(html, "html.parser")
    fixtures = _extract_json_ld_fixtures(soup)
    event_rows = _extract_event_row_texts(soup)

    parsed_visible_rows = [parsed for row in event_rows if (parsed := _parse_football_event_row_text(row)) is not None]
    pair_count = min(len(fixtures), len(parsed_visible_rows))

    parsed_rows: list[SportPesaFootballOdds] = []

    for index in range(pair_count):
        fixture = fixtures[index]
        parsed_row = parsed_visible_rows[index]

        parsed_rows.append(
            SportPesaFootballOdds(
                source="sportpesa",
                sport="football",
                league=str(fixture.get("league") or "Unknown League"),
                event_datetime=str(parsed_row["event_datetime"]),
                game_id=str(parsed_row["game_id"]),
                home_team=str(fixture.get("home_team") or ""),
                away_team=str(fixture.get("away_team") or ""),
                home_odds=parsed_row["home_odds"],
                draw_odds=parsed_row["draw_odds"],
                away_odds=parsed_row["away_odds"],
                home_or_draw_odds=parsed_row["home_or_draw_odds"],
                draw_or_away_odds=parsed_row["draw_or_away_odds"],
                home_or_away_odds=parsed_row["home_or_away_odds"],
                over_2_5_odds=parsed_row["over_2_5_odds"],
                under_2_5_odds=parsed_row["under_2_5_odds"],
                btts_yes_odds=parsed_row["btts_yes_odds"],
                btts_no_odds=parsed_row["btts_no_odds"],
                game_url=str(fixture.get("game_url") or "") or None,
                raw_text=str(parsed_row["raw_text"]),
                confidence=0.9,
            )
        )

    return parsed_rows


def parse_sportpesa_basketball(html: str) -> list[SportPesaBasketballOdds]:
    """Parse SportPesa basketball odds from saved or live page HTML.

    V1 uses the same pairing strategy as football: JSON-LD gives us the clean
    fixture identity while the rendered row gives us the internal row id,
    visible datetime, and the 2-way odds including overtime.
    """

    soup = BeautifulSoup(html, "html.parser")
    fixtures = _extract_json_ld_fixtures(soup)
    event_rows = _extract_event_row_texts(soup)

    parsed_visible_rows = [parsed for row in event_rows if (parsed := _parse_basketball_event_row_text(row)) is not None]
    pair_count = min(len(fixtures), len(parsed_visible_rows))

    parsed_rows: list[SportPesaBasketballOdds] = []

    for index in range(pair_count):
        fixture = fixtures[index]
        parsed_row = parsed_visible_rows[index]
        league = str(fixture.get("league") or parsed_row.get("league_hint") or "Unknown League")

        parsed_rows.append(
            SportPesaBasketballOdds(
                source="sportpesa",
                sport="basketball",
                league=league,
                event_datetime=str(parsed_row["event_datetime"]),
                game_id=str(parsed_row["game_id"]),
                home_team=str(fixture.get("home_team") or ""),
                away_team=str(fixture.get("away_team") or ""),
                home_odds=parsed_row["home_odds"],
                away_odds=parsed_row["away_odds"],
                game_url=str(fixture.get("game_url") or "") or None,
                raw_text=str(parsed_row["raw_text"]),
                confidence=0.9,
            )
        )

    return parsed_rows
