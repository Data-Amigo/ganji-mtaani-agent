from dataclasses import dataclass, field
from typing import Any


# =============================================================================
# Polymarket Market Model
# =============================================================================
# This model stores the stable Polymarket V1 fields we want from the Gamma API.
# It focuses on identity, category, timing, status, outcomes, and market-size
# metrics. The raw_record field keeps the original JSON payload for debugging
# and later enrichment when we expand the parser.
@dataclass(slots=True)
class PolymarketMarket:
    """Structured Polymarket market record normalized from the Gamma API.

    Attributes:
        source: Source name. For this model it will be "polymarket".
        market_id: Unique Polymarket market identifier.
        event_id: Parent event identifier when available.
        question: Main market question shown to users.
        slug: URL-friendly market slug.
        category: High-level category such as sports or politics.
        subcategory: More specific grouping under the main category.
        tags: Flexible tag labels for later filtering and analysis.
        description: Market description text when available.
        start_date: Market start date string from the API.
        end_date: Market end date string from the API.
        active: Whether the market is currently active.
        closed: Whether the market is closed.
        archived: Whether the market is archived.
        outcomes: Outcome labels in API order, for example ["Yes", "No"].
        outcome_prices: Prices/probabilities aligned with outcomes.
        liquidity: Reported market liquidity.
        volume: Reported total market volume.
        open_interest: Reported open interest when available.
        market_type: Market type or AMM/order-book style indicator.
        raw_record: Original JSON payload for debugging and future expansion.
        confidence: Ingestion confidence score for the record.
    """

    source: str
    market_id: str
    event_id: str | None
    question: str
    slug: str | None
    category: str | None
    subcategory: str | None
    tags: list[str] = field(default_factory=list)
    description: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    active: bool = False
    closed: bool = False
    archived: bool = False
    outcomes: list[str] = field(default_factory=list)
    outcome_prices: list[float] = field(default_factory=list)
    liquidity: float | None = None
    volume: float | None = None
    open_interest: float | None = None
    market_type: str | None = None
    raw_record: dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0

    def outcome_map(self) -> dict[str, float | None]:
        """Return outcomes mapped to their matching prices.

        The Gamma API gives outcomes and outcome prices as parallel arrays.
        This helper makes downstream code easier to read when we want a simple
        outcome-to-price mapping.
        """

        mapped: dict[str, float | None] = {}

        for index, outcome in enumerate(self.outcomes):
            price = self.outcome_prices[index] if index < len(self.outcome_prices) else None
            mapped[outcome] = price

        return mapped
