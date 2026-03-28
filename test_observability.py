#!/usr/bin/env python3
"""Test agent with observability question."""

import asyncio
import json
import os

import websockets

# Read access key
access_key = ""
with open(".env.docker.secret") as f:
    for line in f:
        if line.startswith("NANOBOT_ACCESS_KEY="):
            access_key = line.strip().split("=", 1)[1]
            break

uri = f"ws://localhost:42002/ws/chat?access_key={access_key}"


async def test(question: str):
    try:
        async with websockets.connect(uri) as ws:
            await ws.send(json.dumps({"content": question}))
            # Wait for response (may take multiple messages)
            responses = []
            for _ in range(10):  # Wait for up to 10 messages
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=30.0)
                    responses.append(msg)
                    if "Response to webchat" in msg or "content" in msg:
                        break
                except asyncio.TimeoutError:
                    break
            return responses
    except Exception as e:
        return [f"Error: {e}"]


if __name__ == "__main__":
    question = "Any LMS backend errors in the last 10 minutes?"
    print(f"Asking: {question}")
    responses = asyncio.run(test(question))
    for resp in responses:
        print(f"Response: {resp[:500]}")
