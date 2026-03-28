"""MCP observability server settings."""

import os
from dataclasses import dataclass


@dataclass
class ObservabilitySettings:
    """Settings for observability MCP server."""
    victorialogs_url: str
    victoriatraces_url: str


def resolve_settings() -> ObservabilitySettings:
    """Resolve settings from environment variables."""
    victorialogs_url = os.environ.get(
        "NANOBOT_VICTORIALOGS_URL",
        "http://localhost:42010"
    )
    victoriatraces_url = os.environ.get(
        "NANOBOT_VICTORIATRACES_URL",
        "http://localhost:42011"
    )
    return ObservabilitySettings(
        victorialogs_url=victorialogs_url,
        victoriatraces_url=victoriatraces_url,
    )
