import json
from typing import Any

from ganji_mtaani_agent.models.polymarket import PolymarketMarket


# =============================================================================
# Polymarket Category Rules
# =============================================================================
# These tags represent the main high-level groupings we care about for the
# product. If a market inherits more than one of these from its parent event,
# we label it as Mixed rather than forcing an inaccurate single category.
PRIMARY_CATEGORY_TAGS = [
    "Sports",
    "Politics",
    "Crypto",
    "Finance",
    "Business",
    "Economy",
    "Technology",
    "World",
    "Culture",
]
GENERIC_TAGS = {"all"}


# =============================================================================
# Basic Parsing Helpers
# =============================================================================
def _to_float(value: Any) -> float | None:
    """Convert a raw Polymarket value to float when possible."""

    if value in (None, "", "null"):
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_json_list(raw_value: Any) -> list[Any]:
    """Normalize list-like values from the API into a Python list.

    The Gamma API may return arrays as native lists or as JSON-encoded strings.
    This helper keeps normalization tolerant and consistent.
    """

    if raw_value is None:
        return []

    if isinstance(raw_value, list):
        return raw_value

    if isinstance(raw_value, str):
        raw_value = raw_value.strip()

        if not raw_value:
            return []

        try:
            parsed = json.loads(raw_value)
        except json.JSONDecodeError:
            return [raw_value]

        return parsed if isinstance(parsed, list) else [parsed]

    return [raw_value]


def _parse_tags(raw_value: Any) -> list[str]:
    """Normalize tag-like values into a list of strings."""

    raw_tags = _parse_json_list(raw_value)
    normalized_tags: list[str] = []

    for item in raw_tags:
        if isinstance(item, dict):
            label = item.get("label") or item.get("slug") or item.get("name")
            if label:
                normalized_tags.append(str(label))
        elif item not in (None, ""):
            normalized_tags.append(str(item))

    return normalized_tags


# =============================================================================
# Event Enrichment Helpers
# =============================================================================
def build_event_map(raw_events: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Map event payloads by event id for market enrichment."""

    event_map: dict[str, dict[str, Any]] = {}

    for event in raw_events:
        event_id = event.get("id")
        if event_id not in (None, ""):
            event_map[str(event_id)] = event

    return event_map


def extract_event_id(raw_record: dict[str, Any]) -> str | None:
    """Extract the parent event id from a market record when possible."""

    direct_event_id = raw_record.get("eventId")
    if direct_event_id not in (None, ""):
        return str(direct_event_id)

    embedded_events = raw_record.get("events")
    if isinstance(embedded_events, list) and embedded_events:
        first_event = embedded_events[0]
        if isinstance(first_event, dict) and first_event.get("id") not in (None, ""):
            return str(first_event["id"])

    return None


def derive_category(tag_labels: list[str]) -> str | None:
    """Choose a stable top-level category from event tags."""

    matched_categories = [
        category
        for category in PRIMARY_CATEGORY_TAGS
        if any(tag.casefold() == category.casefold() for tag in tag_labels)
    ]

    if len(matched_categories) == 1:
        return matched_categories[0]

    if len(matched_categories) > 1:
        return "Mixed"

    for tag in tag_labels:
        if tag.casefold() not in GENERIC_TAGS:
            return tag

    return None


def derive_subcategory(tag_labels: list[str], category: str | None) -> str | None:
    """Choose a secondary grouping from the remaining tag labels."""

    if not tag_labels or category == "Mixed":
        return None

    for tag in tag_labels:
        if tag.casefold() in GENERIC_TAGS:
            continue
        if category is None or tag.casefold() != category.casefold():
            return tag

    return None


def matches_requested_category(market: PolymarketMarket, requested_category: str) -> bool:
    """Return True when a market matches a category by field or tags."""

    requested = requested_category.casefold()

    if market.category and market.category.casefold() == requested:
        return True

    return any(tag.casefold() == requested for tag in market.tags)


# =============================================================================
# Main Normalization Logic
# =============================================================================
def normalize_market_record(
    raw_record: dict[str, Any],
    event_map: dict[str, dict[str, Any]] | None = None,
) -> PolymarketMarket:
    """Convert one raw Gamma API market record into our stable V1 model."""

    event_map = event_map or {}
    event_id = extract_event_id(raw_record)
    event_record = event_map.get(event_id or "", {})

    raw_outcomes = _parse_json_list(raw_record.get("outcomes"))
    raw_prices = _parse_json_list(raw_record.get("outcomePrices"))
    event_tags = _parse_tags(event_record.get("tags"))

    outcomes = [str(item) for item in raw_outcomes if item not in (None, "")]
    outcome_prices = [
        price for price in (_to_float(item) for item in raw_prices) if price is not None
    ]

    market_category = (
        str(raw_record.get("category"))
        if raw_record.get("category") not in (None, "")
        else None
    )
    market_subcategory = (
        str(raw_record.get("subcategory"))
        if raw_record.get("subcategory") not in (None, "")
        else None
    )
    derived_category = derive_category(event_tags)
    derived_subcategory = derive_subcategory(event_tags, derived_category)

    return PolymarketMarket(
        source="polymarket",
        market_id=str(raw_record.get("id", "")),
        event_id=event_id,
        question=str(raw_record.get("question") or ""),
        slug=(str(raw_record.get("slug")) if raw_record.get("slug") not in (None, "") else None),
        category=market_category or derived_category,
        subcategory=market_subcategory or derived_subcategory,
        tags=event_tags or _parse_tags(raw_record.get("tags")),
        description=(
            str(raw_record.get("description"))
            if raw_record.get("description") not in (None, "")
            else None
        ),
        start_date=(
            str(raw_record.get("startDate"))
            if raw_record.get("startDate") not in (None, "")
            else None
        ),
        end_date=(
            str(raw_record.get("endDate"))
            if raw_record.get("endDate") not in (None, "")
            else None
        ),
        active=bool(raw_record.get("active", False)),
        closed=bool(raw_record.get("closed", False)),
        archived=bool(raw_record.get("archived", False)),
        outcomes=outcomes,
        outcome_prices=outcome_prices,
        liquidity=_to_float(raw_record.get("liquidity")) or _to_float(event_record.get("liquidity")),
        volume=_to_float(raw_record.get("volume")) or _to_float(event_record.get("volume")),
        open_interest=_to_float(raw_record.get("openInterest")) or _to_float(event_record.get("openInterest")),
        market_type=(
            str(raw_record.get("ammType") or raw_record.get("marketType"))
            if raw_record.get("ammType") not in (None, "") or raw_record.get("marketType") not in (None, "")
            else None
        ),
        raw_record=raw_record,
        confidence=1.0,
    )


def normalize_polymarket_markets(
    raw_markets: list[dict[str, Any]],
    raw_events: list[dict[str, Any]],
    category: str | None = None,
    result_limit: int | None = None,
) -> list[PolymarketMarket]:
    """Normalize and optionally filter Polymarket markets.

    This is the main parser entry point for the Polymarket ingestion flow.
    It enriches market records with parent event context, applies optional
    category/tag filtering, and returns structured PolymarketMarket objects.
    """

    event_map = build_event_map(raw_events)
    normalized_markets = [normalize_market_record(item, event_map=event_map) for item in raw_markets]

    if category:
        normalized_markets = [
            market for market in normalized_markets if matches_requested_category(market, category)
        ]

    if result_limit is not None:
        normalized_markets = normalized_markets[:result_limit]

    return normalized_markets
