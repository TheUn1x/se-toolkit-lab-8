#!/usr/bin/env python3
"""Test agent investigation with 'What went wrong?' question."""

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


async def test(question: str, timeout_sec: float = 60.0):
    """Send question and collect all responses."""
    try:
        async with websockets.connect(uri) as ws:
            await ws.send(json.dumps({"content": question}))
            
            # Collect responses
            responses = []
            end_time = asyncio.get_event_loop().time() + timeout_sec
            
            while asyncio.get_event_loop().time() < end_time:
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=10.0)
                    responses.append(msg)
                    # Check if this looks like a final response
                    if "Response to webchat" in msg or (len(responses) > 3 and "content" in msg):
                        # Give a bit more time for any follow-up
                        await asyncio.sleep(2.0)
                        break
                except asyncio.TimeoutError:
                    break
            
            return responses
    except Exception as e:
        return [f"Connection error: {e}"]


if __name__ == "__main__":
    question = "What went wrong?"
    print(f"Asking: {question}")
    print("=" * 60)
    responses = asyncio.run(test(question, timeout_sec=60.0))
    
    for i, resp in enumerate(responses):
        print(f"\n[Response {i+1}]:")
        # Parse JSON if possible
        try:
            data = json.loads(resp)
            if "content" in data:
                print(f"Type: {data.get('type', 'unknown')}")
                print(f"Content: {data.get('content', '')[:1000]}")
            else:
                print(resp[:500])
        except json.JSONDecodeError:
            print(resp[:500])
