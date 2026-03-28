"""HTTP client for VictoriaLogs and VictoriaTraces APIs."""

import httpx
import json
from typing import Any

from mcp_obs.settings import ObservabilitySettings


class ObservabilityClient:
    """Client for querying VictoriaLogs and VictoriaTraces."""

    def __init__(self, settings: ObservabilitySettings) -> None:
        self.victorialogs_url = settings.victorialogs_url.rstrip("/")
        self.victoriatraces_url = settings.victoriatraces_url.rstrip("/")
        self._http = httpx.AsyncClient(timeout=30.0)

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._http.aclose()

    async def __aenter__(self) -> "ObservabilityClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()

    async def logs_search(
        self,
        query: str,
        limit: int = 10,
        time_range: str = "1h",
    ) -> list[dict[str, Any]]:
        """Search logs using VictoriaLogs LogsQL query."""
        url = f"{self.victorialogs_url}/select/logsql/query"
        params = {"query": query, "limit": limit}
        
        # Add time range to query if not already present
        if "_time:" not in query:
            params["query"] = f"_time:{time_range} {query}"

        response = await self._http.get(url, params=params)
        response.raise_for_status()
        
        # VictoriaLogs returns newline-delimited JSON (multiple objects)
        results = []
        content = response.text.strip()
        for line in content.split("\n"):
            if line.strip():
                try:
                    results.append(json.loads(line))
                except json.JSONDecodeError:
                    # Skip malformed lines
                    continue
        
        return results

    async def logs_error_count(
        self,
        service: str | None = None,
        time_range: str = "1h",
    ) -> list[dict[str, Any]]:
        """Count errors per service over a time window."""
        query = "severity:ERROR"
        if service:
            query = f'service.name:"{service}" severity:ERROR'
        
        # Query for errors in time range
        results = await self.logs_search(query=query, limit=100, time_range=time_range)
        
        # Count by service
        error_count: dict[str, int] = {}
        for entry in results:
            svc = entry.get("service.name", entry.get("service", "unknown"))
            error_count[svc] = error_count.get(svc, 0) + 1
        
        return [{"service": k, "error_count": v} for k, v in error_count.items()]

    async def traces_list(
        self,
        service: str,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """List recent traces for a service."""
        url = f"{self.victoriatraces_url}/select/jaeger/api/traces"
        params = {"service": service, "limit": limit}
        
        response = await self._http.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        if isinstance(data, dict) and "data" in data:
            return data["data"]
        return []

    async def traces_get(self, trace_id: str) -> dict[str, Any] | None:
        """Fetch a specific trace by ID."""
        url = f"{self.victoriatraces_url}/select/jaeger/api/traces/{trace_id}"
        
        response = await self._http.get(url)
        response.raise_for_status()
        
        data = response.json()
        if isinstance(data, dict) and "data" in data and len(data["data"]) > 0:
            return data["data"][0]
        return None
