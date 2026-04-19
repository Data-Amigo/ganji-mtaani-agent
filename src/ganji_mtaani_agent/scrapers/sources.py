"""This is the sources.py file.

Author: Data-Amigo
Date: 2026-04-16
Description:
This is the source registry. It tells the app which websites/data sources exist,
their target pages, default URLs, display names, descriptions, and default
browser settings.
"""

from dataclasses import dataclass, field


# =============================================================================
# Source Target Model
# =============================================================================
# SourceTarget defines one specific page or data target under a source.
#
# Example:
# - Forebet is the source.
# - Forebet football today is one target.
# - Forebet basketball today is another target.
#
# This prevents us from treating every page as a totally separate source while
# still allowing each sport/page to have its own URL and parser behavior later.
@dataclass(frozen=True, slots=True)
class SourceTarget:
    """Configuration details for one target page under a source.

    Attributes:
        name: Internal target key, such as "football_today".
        display_name: Human-readable target name shown in the UI.
        url: Exact URL to fetch for this target.
        sport: Sport or category represented by this target.
        description: Short explanation of what this target contains.
    """

    name: str
    display_name: str
    url: str
    sport: str
    description: str


# =============================================================================
# Source Configuration Model
# =============================================================================
# SourceConfig defines the shape of one supported website/source.
#
# Why this exists:
# - The app needs to know which sources are available.
# - The UI needs a display name and default target for each source.
# - The scraper needs a stable internal source name for logs and routing.
# - Each source can have different browser behavior during development.
# - Future sources can be added without changing the UI structure first.
@dataclass(frozen=True, slots=True)
class SourceConfig:
    """Configuration details for one supported scraping source.

    Attributes:
        name: Internal source key used by code, logs, and CLI arguments.
        display_name: Human-readable name shown in the Streamlit UI.
        default_target: Target key used when the caller does not choose one.
        targets: Dictionary of target pages available under this source.
        description: Short explanation of the source's role in the project.
        default_wait_until: Default Playwright load state for this source.
        default_settle_ms: Extra wait time after page load for JavaScript rendering.
        default_headless: Whether this source should run hidden by default.
    """

    name: str
    display_name: str
    default_target: str
    targets: dict[str, SourceTarget]
    description: str
    default_wait_until: str = "domcontentloaded"
    default_settle_ms: int = 3_000
    default_headless: bool = True

    @property
    def default_url(self) -> str:
        """Return the URL for the source's default target.

        This keeps backward compatibility with older code that expects a source
        to have one default URL, while still allowing multiple targets.
        """

        return self.targets[self.default_target].url


# =============================================================================
# Supported Source Registry
# =============================================================================
# SOURCES is the central list of websites the project currently understands.
#
# Important idea:
# - The dictionary key is the internal source name, for example "forebet".
# - The dictionary value is a SourceConfig object with source and target details.
#
# Forebet currently works better in headed mode during development because
# headless mode triggers a security verification page.
SOURCES: dict[str, SourceConfig] = {
    "forebet": SourceConfig(
        name="forebet",
        display_name="Forebet",
        default_target="basketball_today",
        description="Sports prediction source for football and basketball workflows.",
        default_wait_until="domcontentloaded",
        default_settle_ms=15_000,
        default_headless=False,
        targets={
            "football_today": SourceTarget(
                name="football_today",
                display_name="Football Predictions Today",
                url="https://www.forebet.com/en/football-tips-and-predictions-for-today",
                sport="football",
                description="Forebet football predictions for today's matches.",
            ),
            "basketball_today": SourceTarget(
                name="basketball_today",
                display_name="Basketball Predictions Today",
                url="https://www.forebet.com/en/basketball/predictions-today",
                sport="basketball",
                description="Forebet basketball predictions for today's games.",
            ),
        },
    ),
    "polymarket": SourceConfig(
        name="polymarket",
        display_name="Polymarket",
        default_target="markets",
        description="Strategic prediction-market source for broader market intelligence.",
        default_wait_until="domcontentloaded",
        default_settle_ms=5_000,
        default_headless=True,
        targets={
            "markets": SourceTarget(
                name="markets",
                display_name="All Markets",
                url="https://polymarket.com/markets",
                sport="market_intelligence",
                description="Polymarket markets index for broad prediction-market discovery.",
            ),
        },
    ),
}


# =============================================================================
# Source Lookup Helper
# =============================================================================
# This helper gives the rest of the app one safe way to get source details.
# Instead of accessing SOURCES directly everywhere, callers can use this function
# and receive a clear error if the source name is not supported.
def get_source_config(source_name: str) -> SourceConfig:
    """Return the configuration object for a supported source.

    Args:
        source_name: Internal source key, such as "forebet" or "polymarket".

    Returns:
        The SourceConfig object for the requested source.

    Raises:
        ValueError: If the source name is not registered in SOURCES.

    Example:
        source = get_source_config("forebet")
        print(source.default_url)
    """

    try:
        return SOURCES[source_name]
    except KeyError as exc:
        supported = ", ".join(sorted(SOURCES))
        raise ValueError(f"Unsupported source '{source_name}'. Supported sources: {supported}") from exc


# =============================================================================
# Target Lookup Helper
# =============================================================================
# This helper returns one specific target page for a source. The Streamlit UI and
# smoke script can use it to fetch basketball, football, or future target pages.
def get_source_target(source: SourceConfig, target_name: str | None = None) -> SourceTarget:
    """Return a target page config from a source.

    Args:
        source: SourceConfig object returned by get_source_config().
        target_name: Optional target key. If omitted, the source default is used.

    Returns:
        SourceTarget object for the requested target.

    Raises:
        ValueError: If the target does not exist under the selected source.
    """

    selected_target = target_name or source.default_target

    try:
        return source.targets[selected_target]
    except KeyError as exc:
        supported = ", ".join(sorted(source.targets))
        raise ValueError(
            f"Unsupported target '{selected_target}' for source '{source.name}'. "
            f"Supported targets: {supported}"
        ) from exc
