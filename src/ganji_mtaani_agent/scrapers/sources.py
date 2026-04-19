"""This is the sources.py file.

Author: Data-Amigo
Date: 2026-04-16
Description:
This is the source registry. It tells the app which websites/data sources exist,
their default URLs, display names, and descriptions.
"""

from dataclasses import dataclass


# =============================================================================
# Source Configuration Model
# =============================================================================
# SourceConfig defines the shape of one supported website/source.
#
# Why this exists:
# - The app needs to know which sources are available.
# - The UI needs a display name and default URL for each source.
# - The scraper needs a stable internal source name for logs and routing.
# - Future sources can be added without changing the UI structure first.
@dataclass(frozen=True, slots=True)
class SourceConfig:
    """Configuration details for one supported scraping source.

    Attributes:
        name: Internal source key used by code, logs, and CLI arguments.
        display_name: Human-readable name shown in the Streamlit UI.
        default_url: First URL to use when this source is selected.
        description: Short explanation of the source's role in the project.
    """

    name: str
    display_name: str
    default_url: str
    description: str


# =============================================================================
# Supported Source Registry
# =============================================================================
# SOURCES is the central list of websites the project currently understands.
#
# Important idea:
# - The dictionary key is the internal source name, for example "forebet".
# - The dictionary value is a SourceConfig object with the source details.
#
# When we build the Streamlit source selector, it can read from this dictionary
# to know which sources exist and what default URL to prefill.
SOURCES: dict[str, SourceConfig] = {
    "forebet": SourceConfig(
        name="forebet",
        display_name="Forebet",
        default_url="https://www.forebet.com/en/football-tips-and-predictions-for-today",
        description="Football prediction source for the first betting workflow.",
    ),
    "polymarket": SourceConfig(
        name="polymarket",
        display_name="Polymarket",
        default_url="https://polymarket.com/markets",
        description="Strategic prediction-market source for broader market intelligence.",
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
