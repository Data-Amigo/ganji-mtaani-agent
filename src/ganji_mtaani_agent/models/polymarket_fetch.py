from dataclasses import dataclass
from typing import Any


# =============================================================================
# Polymarket Fetch Configuration Model
# =============================================================================
# This configuration object keeps the Polymarket ingestion entry point explicit.
# We separate how much raw data to scan from how many normalized records we want
# back, because category filtering often needs a larger search pool.
@dataclass(slots=True)
class PolymarketFetchConfig:
    """Configuration for fetching and filtering Polymarket market data.

    Attributes:
        result_limit: Number of normalized records we want after filtering.
        scan_limit: Number of raw markets/events to scan before filtering.
        active_only: Whether to limit the API query to active markets/events.
        category: Optional category or tag filter such as sports or politics.
    """

    result_limit: int = 20
    scan_limit: int = 100
    active_only: bool = True
    category: str | None = None


# =============================================================================
# Raw Polymarket Response Model
# =============================================================================
# This model keeps the raw API payloads together before parsing. It helps us
# preserve the separation between fetching JSON and normalizing it.
@dataclass(slots=True)
class PolymarketRawResponse:
    """Container for raw Polymarket market and event payloads."""

    markets: list[dict[str, Any]]
    events: list[dict[str, Any]]
