"""MCP tool definitions for observability."""

from dataclasses import dataclass
from typing import Any, Callable, Awaitable

from mcp.types import Tool
from pydantic import BaseModel


@dataclass
class ToolSpec:
    """Tool specification."""
    name: str
    description: str
    model: type[BaseModel]
    handler: Callable[..., Awaitable[Any]]

    def as_tool(self) -> Tool:
        """Convert to MCP Tool."""
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema=self.model.model_json_schema(),
        )


# --- Log Tools ---


class LogsSearchParams(BaseModel):
    """Parameters for logs_search tool."""
    query: str
    limit: int = 10
    time_range: str = "1h"


class LogsErrorCountParams(BaseModel):
    """Parameters for logs_error_count tool."""
    service: str | None = None
    time_range: str = "1h"


# --- Trace Tools ---


class TracesListParams(BaseModel):
    """Parameters for traces_list tool."""
    service: str
    limit: int = 5


class TracesGetParams(BaseModel):
    """Parameters for traces_get tool."""
    trace_id: str


# Tool specs will be created in server.py with actual handlers
