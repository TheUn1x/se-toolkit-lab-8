#!/usr/bin/env python3
"""Query VictoriaTraces HTTP API (Jaeger-compatible)."""

import requests
import json

# Get recent traces for the backend service
url = "http://localhost:42011/select/jaeger/api/traces?service=Learning%20Management%20Service&limit=5"

response = requests.get(url)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    if 'data' in data and len(data['data']) > 0:
        print(f"\nFound {len(data['data'])} traces:")
        for trace in data['data'][:3]:
            print(f"\nTrace ID: {trace['traceID']}")
            print(f"Spans: {len(trace.get('spans', []))}")
            for span in trace.get('spans', [])[:3]:
                print(f"  - Span: {span.get('operationName', 'unknown')} ({span.get('spanID')})")
    else:
        print("No traces found")
else:
    print(f"Response: {response.text[:500]}")
