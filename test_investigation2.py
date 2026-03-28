#!/usr/bin/env python3
"""Test agent investigation with specific question about LMS errors."""

import asyncio
import json

import websockets

# Read access key
access_key = ""
with open(".env.docker.secret") as f:
    for line in f:
        if line.startswith("NANOBOT_ACCESS_KEY="):
            access_key = line.strip().split("=", 1)[1]
            break

uri = f"ws://localhost:42002/ws/chat?access_key={access_key}"


async def test(question: str, timeout_sec: float = 90.0):
    """Send question and collect all responses."""
    try:
        async with websockets.connect(uri) as ws:
            await ws.send(json.dumps({"content": question}))
            
            responses = []
            end_time = asyncio.get_event_loop().time() + timeout_sec
            
            while asyncio.get_event_loop().time() < end_time:
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=15.0)
                    responses.append(msg)
                    # Check if this is a final response
                    if "Response to webchat" in str(msg):
                        await asyncio.sleep(3.0)
                        break
                except asyncio.TimeoutError:
                    break
            
            return responses
    except Exception as e:
        return [f"Connection error: {e}"]


if __name__ == "__main__":
    question = "Any LMS backend errors in the last 5 minutes? Check logs and traces and tell me what failed."
    print(f"Asking: {question}")
    print("=" * 60)
    responses = asyncio.run(test(question, timeout_sec=90.0))
    
    for i, resp in enumerate(responses):
        print(f"\n[Response {i+1}]:")
        try:
            data = json.loads(resp)
            if "content" in data:
                content = data.get('content', '')
                print(f"Content:\n{content[:1500]}")
            else:
                print(resp[:500])
        except json.JSONDecodeError:
            print(resp[:500])
