#!/usr/bin/env python3
"""Get a specific trace by ID from VictoriaTraces."""

import requests
import json

# The error trace ID we found earlier
trace_id = "a2ab11f6862417ce696b0b9eab874890"
url = f"http://localhost:42011/select/jaeger/api/traces/{trace_id}"

response = requests.get(url)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    if 'data' in data and len(data['data']) > 0:
        trace = data['data'][0]
        print(f"\nTrace ID: {trace['traceID']}")
        print(f"Total spans: {len(trace.get('spans', []))}")
        print("\nSpan hierarchy:")
        for span in trace.get('spans', []):
            tags = {tag['key']: tag.get('value', '') for tag in span.get('tags', [])}
            has_error = 'error' in tags or tags.get('otel.status_code') == 'ERROR'
            error_marker = " ⚠️ ERROR" if has_error else ""
            print(f"  - {span.get('operationName', 'unknown')}: {span.get('spanID')}{error_marker}")
            if has_error and 'error' in tags:
                print(f"    Error: {tags['error'][:100]}...")
    else:
        print("Trace not found")
else:
    print(f"Response: {response.text[:500]}")
