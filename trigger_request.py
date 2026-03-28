#!/usr/bin/env python3
"""Trigger a request to the backend."""

import requests

# Read API key
with open(".env.docker.secret") as f:
    for line in f:
        if line.startswith("LMS_API_KEY="):
            api_key = line.strip().split("=", 1)[1]
            break

response = requests.get("http://localhost:42002/items/", headers={"Authorization": f"Bearer {api_key}"})
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:500]}")
