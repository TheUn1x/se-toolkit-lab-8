#!/usr/bin/env python3
"""Test WebSocket connection to nanobot."""

import asyncio
import json
import os
import sys

import websockets

# Read access key from .env.docker.secret
access_key = ""
with open(".env.docker.secret") as f:
    for line in f:
        if line.startswith("NANOBOT_ACCESS_KEY="):
            access_key = line.strip().split("=", 1)[1]
            break

if not access_key:
    print("Error: NANOBOT_ACCESS_KEY not found in .env.docker.secret")
    sys.exit(1)

uri = f"ws://localhost:42002/ws/chat?access_key={access_key}"


async def test():
    try:
        async with websockets.connect(uri) as ws:
            await ws.send(json.dumps({"content": "What labs are available?"}))
            response = await ws.recv()
            print("Response:", response)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


asyncio.run(test())
