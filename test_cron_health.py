#!/usr/bin/env python3
"""Create scheduled health check and capture proactive reports."""

import asyncio
import json
import sys

import websockets

# Read access key
access_key = ""
with open(".env.docker.secret") as f:
    for line in f:
        if line.startswith("NANOBOT_ACCESS_KEY="):
            access_key = line.strip().split("=", 1)[1]
            break

uri = f"ws://localhost:42002/ws/chat?access_key={access_key}"


async def send_and_collect(ws, question: str, timeout_sec: float = 60.0):
    """Send a message and collect responses."""
    await ws.send(json.dumps({"content": question}))
    
    responses = []
    end_time = asyncio.get_event_loop().time() + timeout_sec
    
    while asyncio.get_event_loop().time() < end_time:
        try:
            msg = await asyncio.wait_for(ws.recv(), timeout=15.0)
            responses.append(msg)
            if "Response to webchat" in str(msg):
                await asyncio.sleep(2.0)
                break
        except asyncio.TimeoutError:
            break
    
    return responses


async def main():
    try:
        async with websockets.connect(uri) as ws:
            # Step 1: Create health check
            print("=" * 60)
            print("STEP 1: Creating scheduled health check...")
            print("=" * 60)
            question = "Create a health check for this chat that runs every 2 minutes using your cron tool. Each run should check for LMS backend errors in the last 2 minutes, inspect a trace if needed, and post a short summary here. If there are no recent errors, say the system looks healthy."
            responses = await send_and_collect(ws, question, timeout_sec=90.0)
            for resp in responses:
                try:
                    data = json.loads(resp)
                    if "content" in data:
                        print(f"\nAgent: {data['content'][:800]}")
                except:
                    pass
            
            # Step 2: List scheduled jobs
            print("\n" + "=" * 60)
            print("STEP 2: Listing scheduled jobs...")
            print("=" * 60)
            responses = await send_and_collect(ws, "List scheduled jobs.", timeout_sec=30.0)
            for resp in responses:
                try:
                    data = json.loads(resp)
                    if "content" in data:
                        print(f"\nAgent: {data['content'][:500]}")
                except:
                    pass
            
            # Keep connection open and wait for proactive messages
            print("\n" + "=" * 60)
            print("STEP 3: Waiting for proactive health report (up to 3 min)...")
            print("=" * 60)
            
            # Trigger another failure to ensure fresh data
            import subprocess
            subprocess.run(["uv", "run", "python", "trigger_request.py"], capture_output=True)
            
            end_time = asyncio.get_event_loop().time() + 180.0  # Wait up to 3 minutes
            while asyncio.get_event_loop().time() < end_time:
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=30.0)
                    data = json.loads(msg)
                    if "content" in data:
                        content = data.get('content', '')
                        if any(word in content.lower() for word in ['health', 'error', 'healthy', 'check']):
                            print(f"\n[Proactive Report]:\n{content[:1000]}")
                            break
                except asyncio.TimeoutError:
                    print("Still waiting...")
                except json.JSONDecodeError:
                    pass
                except Exception as e:
                    print(f"Error: {e}")
                    break
            
            # Step 4: Remove the job
            print("\n" + "=" * 60)
            print("STEP 4: Removing scheduled job...")
            print("=" * 60)
            responses = await send_and_collect(ws, "Remove the health check job you just created.", timeout_sec=30.0)
            for resp in responses:
                try:
                    data = json.loads(resp)
                    if "content" in data:
                        print(f"\nAgent: {data['content'][:500]}")
                except:
                    pass
                    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
