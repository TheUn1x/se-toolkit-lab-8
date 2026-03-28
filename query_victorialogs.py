#!/usr/bin/env python3
"""Query VictoriaLogs HTTP API."""

import requests
import json

# Query for errors in the last hour
query = '_time:1h service.name:"Learning Management Service" severity:ERROR'
url = f"http://localhost:42010/select/logsql/query?query={query}&limit=10"

response = requests.get(url)
print(f"Status: {response.status_code}")
print(f"Response:\n{json.dumps(response.json(), indent=2)[:2000]}")
