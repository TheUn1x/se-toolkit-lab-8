"""Stdio MCP server exposing observability tools."""

from __future__ import annotations

import asyncio
import json
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
from pydantic import BaseModel

from mcp_obs.client import ObservabilityClient
from mcp_obs.settings import resolve_settings
from mcp_obs.tools import (
    LogsSearchParams,
    LogsErrorCountParams,
    TracesListParams,
    TracesGetParams,
)


def _text(data: Any) -> list[TextContent]:
    """Convert data to text content."""
    if isinstance(data, BaseModel):
        payload = data.model_dump()
    elif isinstance(data, list):
        payload = [
            item.model_dump() if isinstance(item, BaseModel) else item
            for item in data
        ]
    else:
        payload = data
    return [TextContent(type="text", text=json.dumps(payload, ensure_ascii=False, default=str))]


def create_server(client: ObservabilityClient) -> Server:
    """Create the MCP server with observability tools."""
    server = Server("observability")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="mcp_obs_logs_search",
                description="Search logs using LogsQL query. Use fields like service.name, severity, event, trace_id. Example: 'service.name:\"Learning Management Service\" severity:ERROR'",
                inputSchema=LogsSearchParams.model_json_schema(),
            ),
            Tool(
                name="mcp_obs_logs_error_count",
                description="Count errors per service over a time window. Returns list of {service, error_count}.",
                inputSchema=LogsErrorCountParams.model_json_schema(),
            ),
            Tool(
                name="mcp_obs_traces_list",
                description="List recent traces for a service. Returns trace summaries with span counts.",
                inputSchema=TracesListParams.model_json_schema(),
            ),
            Tool(
                name="mcp_obs_traces_get",
                description="Fetch a specific trace by ID. Returns full trace with all spans and tags.",
                inputSchema=TracesGetParams.model_json_schema(),
            ),
        ]

    @server.call_tool()
    async def call_tool(
        name: str,
        arguments: dict[str, Any] | None,
    ) -> list[TextContent]:
        """Handle tool calls."""
        args = arguments or {}
        
        try:
            if name == "mcp_obs_logs_search":
                params = LogsSearchParams.model_validate(args)
                result = await client.logs_search(
                    query=params.query,
                    limit=params.limit,
                    time_range=params.time_range,
                )
                return _text(result)
            
            elif name == "mcp_obs_logs_error_count":
                params = LogsErrorCountParams.model_validate(args)
                result = await client.logs_error_count(
                    service=params.service,
                    time_range=params.time_range,
                )
                return _text(result)
            
            elif name == "mcp_obs_traces_list":
                params = TracesListParams.model_validate(args)
                result = await client.traces_list(
                    service=params.service,
                    limit=params.limit,
                )
                # Simplify trace data for response
                simplified = [
                    {
                        "trace_id": t.get("traceID"),
                        "span_count": len(t.get("spans", [])),
                    }
                    for t in result
                ]
                return _text(simplified)
            
            elif name == "mcp_obs_traces_get":
                params = TracesGetParams.model_validate(args)
                result = await client.traces_get(params.trace_id)
                if result is None:
                    return _text({"error": f"Trace {params.trace_id} not found"})
                
                # Simplify trace with span hierarchy
                spans = []
                for span in result.get("spans", []):
                    tags = {tag["key"]: tag.get("value", "") for tag in span.get("tags", [])}
                    has_error = "error" in tags or tags.get("otel.status_code") == "ERROR"
                    span_info = {
                        "operation": span.get("operationName"),
                        "span_id": span.get("spanID"),
                        "has_error": has_error,
                    }
                    if has_error and "error" in tags:
                        span_info["error"] = str(tags["error"])[:200]
                    spans.append(span_info)
                
                return _text({
                    "trace_id": result.get("traceID"),
                    "span_count": len(spans),
                    "spans": spans,
                })
            
            else:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]
        
        except Exception as exc:
            return [TextContent(type="text", text=f"Error: {type(exc).__name__}: {exc}")]

    _ = list_tools, call_tool
    return server


async def main() -> None:
    """Main entry point."""
    settings = resolve_settings()
    async with ObservabilityClient(settings) as client:
        server = create_server(client)
        async with stdio_server() as (read_stream, write_stream):
            init_options = server.create_initialization_options()
            await server.run(read_stream, write_stream, init_options)


if __name__ == "__main__":
    asyncio.run(main())
