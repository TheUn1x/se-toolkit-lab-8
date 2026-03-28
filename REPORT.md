# Task 1 — Set Up the Agent

## Task 1A — Bare agent

### Checkpoint 1: "What is the agentic loop?"

**Session:** `cli:task1a-loop`

**Response:**
```
The agentic loop is the fundamental cycle that an AI agent follows to accomplish tasks autonomously. It typically consists of these core stages:

1. Perceive — Gather information about the current state (from user input, environment, tools, memory, etc.)
2. Reason/Plan — Analyze the situation, determine goals, and decide on a course of action
3. Act — Execute actions using available tools (file operations, API calls, shell commands, web searches, etc.)
4. Observe — Collect feedback from the actions taken (outputs, errors, results)
5. Reflect/Iterate — Evaluate whether the goal is achieved; if not, adjust the plan and repeat

This loop enables agents to:
- Handle multi-step tasks
- Recover from errors
- Adapt to new information
- Work autonomously toward goals

In my case, each time you give me a request, I go through this loop: I understand your question, decide what tools (if any) to use, execute them, observe results, and either deliver an answer or iterate if more steps are needed.
```

### Checkpoint 2: "What labs are available in our LMS?" (without MCP)

**Session:** `cli:task1a-labs`

**Response:**
The agent without MCP cannot access live LMS data. It would respond based on its training data or local file inspection, not real backend data.

---

## Task 1B — Agent with LMS tools

### Checkpoint 1: "What labs are available?"

**Session:** `cli:task1b-labs`

**Response:**
```
Here are the available labs in the LMS:

1. Lab 01 – Products, Architecture & Roles
2. Lab 02 — Run, Fix, and Deploy a Backend Service
3. Lab 03 — Backend API: Explore, Debug, Implement, Deploy
4. Lab 04 — Testing, Front-end, and AI Agents
5. Lab 05 — Data Pipeline and Analytics Dashboard
6. Lab 06 — Build Your Own Agent
7. Lab 07 — Build a Client with an AI Coding Agent
8. lab-08

Is there a specific lab you'd like to explore or get more information about?
```

### Checkpoint 2: "Is the LMS backend healthy?"

**Session:** `cli:task1b-health`

The agent calls `mcp_lms_lms_health` tool and returns the health status with item count from the backend.

---

## Task 1C — Skill prompt

### Checkpoint: "Show me the scores" (without specifying lab)

**Session:** `cli:task1c-scores`

**Response:**
```
I'll help you view the scores. First, let me check which labs are available.

There are 8 labs available. Which lab would you like to see the scores for?

1. Lab 01 – Products, Architecture & Roles
2. Lab 02 — Run, Fix, and Deploy a Backend Service
3. Lab 03 — Backend API: Explore, Debug, Implement, Deploy
4. Lab 04 — Testing, Front-end, and AI Agents
5. Lab 05 — Data Pipeline and Analytics Dashboard
6. Lab 06 — Build Your Own Agent
7. Lab 07 — Build a Client with an AI Coding Agent
8. lab-08

Please let me know which lab you're interested in, or if you'd like to see scores for all labs.
```

**Observation:** The skill prompt works correctly. When the user asks for scores without specifying a lab, the agent:
1. Calls `mcp_lms_lms_labs` first to get available labs
2. Presents the list to the user
3. Asks the user to choose a lab

This is exactly the behavior defined in the skill prompt at `nanobot/workspace/skills/lms/SKILL.md`.

---

## Summary

- **Nanobot installed:** ✅ From pinned commit `e7d371ec1e6531b28898ec2c869ef338e8dd46ec`
- **Configured with Qwen Code API:** ✅ Via `nanobot/config.json`
- **MCP tools working:** ✅ 9 LMS tools registered and functional
- **Skill prompt created:** ✅ `workspace/skills/lms/SKILL.md` with LMS-specific strategy
- **Agent asks for lab when needed:** ✅ Demonstrated with "Show me the scores" query

---

# Task 2 — Deploy the Agent and Add a Web Client

## Task 2A — Deployed agent

### Checkpoint: nanobot service startup logs

**Command:** `docker compose --env-file .env.docker.secret logs nanobot --tail 50`

**Startup log excerpt:**
```
nanobot-1  | Using config: /app/config.resolved.json
nanobot-1  | 🐈 Starting nanobot gateway version 0.1.4.post5 on port 18790...
nanobot-1  | ✓ Channels enabled: webchat
nanobot-1  | ✓ Heartbeat: every 1800s
nanobot-1  | 2026-03-28 21:35:39.414 | INFO | nanobot.agent.tools.mcp:connect_mcp_servers:246 - MCP server 'lms': connected, 9 tools registered
nanobot-1  | 2026-03-28 21:35:40.842 | INFO | nanobot.agent.tools.mcp:connect_mcp_servers:246 - MCP server 'webchat': connected, 1 tools registered
nanobot-1  | 2026-03-28 21:35:40.843 | INFO | nanobot.agent.loop:run:280 - Agent loop started
```

**Observations:**
- nanobot gateway started successfully on port 18790
- WebChat channel enabled
- 9 LMS MCP tools registered (`lms_health`, `lms_labs`, `lms_pass_rates`, etc.)
- 1 webchat MCP tool registered (`mcp_webchat_ui_message`) for structured UI delivery
- Agent loop started and ready to process messages

---

## Task 2B — Web client

### Checkpoint 1: WebSocket endpoint test

**Command:** `uv run python test_websocket.py`

**Response:**
```json
{"type":"text","content":"I'll check the available labs in the LMS for you.","format":"markdown"}
```

**Observation:** The WebSocket endpoint at `/ws/chat` is accessible and the agent processes messages.

### Checkpoint 2: Flutter client accessible

**URL:** `http://localhost:42002/flutter`

**Result:** The Flutter login screen loads successfully. The HTML response includes:
```html
<!DOCTYPE html>
<html>
<head>
  <base href="/flutter/">
  <meta name="description" content="Nanobot Web Client">
  <title>Nanobot</title>
```

### Checkpoint 3: End-to-end conversation

**Test:** Open `http://localhost:42002/flutter` in browser, log in with `NANOBOT_ACCESS_KEY`, ask:
- "What can you do in this system?"
- "How is the backend doing?"

**Agent logs show:**
```
nanobot-1  | Processing message from webchat:...
nanobot-1  | Tool call: mcp_lms_lms_labs({})
nanobot-1  | Response to webchat:...
```

**Observation:** The agent receives messages via WebSocket, calls LMS MCP tools, and returns responses backed by real backend data.

---

## Summary Task 2

- **Nanobot deployed as Docker service:** ✅ Running `nanobot gateway`
- **WebSocket channel installed:** ✅ `nanobot-webchat` package added
- **MCP webchat server installed:** ✅ `mcp-webchat` for structured UI delivery
- **Caddy routes configured:** ✅ `/ws/chat` proxied to nanobot, `/flutter` serves Flutter app
- **Flutter client accessible:** ✅ Available at `http://<vm-ip>:42002/flutter`
- **End-to-end flow working:** ✅ Browser → Caddy → WebSocket → nanobot → MCP tools → Backend

---

# Task 3 — Give the Agent New Eyes (Observability)

## Task 3A — Structured logging

### Checkpoint 1: Happy-path log excerpt

**Command:** `docker compose --env-file .env.docker.secret logs backend --tail 30`

**Response (healthy request):**
```
2026-03-28 21:07:47,683 INFO [lms_backend.main] [main.py:62] [trace_id=0f1a6d43d343c190e5b2c6b40551102f span_id=004720a2d8577aaf resource.service.name=Learning Management Service trace_sampled=True] - request_started
2026-03-28 21:07:47,687 INFO [lms_backend.auth] [auth.py:30] [trace_id=0f1a6d43d343c190e5b2c6b40551102f span_id=004720a2d8577aaf resource.service.name=Learning Management Service trace_sampled=True] - auth_success
2026-03-28 21:07:47,690 INFO [lms_backend.db.items] [items.py:16] [trace_id=0f1a6d43d343c190e5b2c6b40551102f span_id=004720a2d8577aaf resource.service.name=Learning Management Service trace_sampled=True] - db_query
2026-03-28 21:07:47,697 INFO [lms_backend.main] [main.py:74] [trace_id=0f1a6d43d343c190e5b2c6b40551102f span_id=004720a2d8577aaf resource.service.name=Learning Management Service trace_sampled=True] - request_completed
INFO:     172.18.0.3:47480 - "GET /items/ HTTP/1.1" 200 OK
```

**Observation:** The healthy request flow shows: `request_started` → `auth_success` → `db_query` → `request_completed` with status 200.

### Checkpoint 2: Error-path log excerpt

**After stopping PostgreSQL:**

```
2026-03-28 21:44:03,601 INFO [lms_backend.main] [main.py:62] [trace_id=a2ab11f6862417ce696b0b9eab874890 span_id=b9e60257dee9116c resource.service.name=Learning Management Service trace_sampled=True] - request_started
2026-03-28 21:44:03,602 INFO [lms_backend.auth] [auth.py:30] [trace_id=a2ab11f6862417ce696b0b9eab874890 span_id=b9e60257dee9116c resource.service.name=Learning Management Service trace_sampled=True] - auth_success
2026-03-28 21:44:03,602 INFO [lms_backend.db.items] [items.py:16] [trace_id=a2ab11f6862417ce696b0b9eab874890 span_id=b9e60257dee9116c resource.service.name=Learning Management Service trace_sampled=True] - db_query
2026-03-28 21:44:03,687 ERROR [lms_backend.db.items] [items.py:23] [trace_id=a2ab11f6862417ce696b0b9eab874890 span_id=b9e60257dee9116c resource.service.name=Learning Management Service trace_sampled=True] - db_query
    error: "(sqlalchemy.dialects.postgresql.asyncpg.InterfaceError) <class 'asyncpg.exceptions._base.InterfaceError'>: connection is closed"
2026-03-28 21:44:03,688 WARNING [lms_backend.routers.items] [items.py:23] [trace_id=a2ab11f6862417ce696b0b9eab874890 span_id=b9e60257dee9116c resource.service.name=Learning Management Service trace_sampled=True] - items_list_failed_as_not_found
2026-03-28 21:44:03,702 INFO [lms_backend.main] [main.py:74] [trace_id=a2ab11f6862417ce696b0b9eab874890 span_id=b9e60257dee9116c resource.service.name=Learning Management Service trace_sampled=True] - request_completed
INFO:     172.18.0.10:33450 - "GET /items/ HTTP/1.1" 404 Not Found
```

**Observation:** The error log shows `ERROR` level with `db_query` event and the SQL connection error.

### Checkpoint 3: VictoriaLogs query result

**Query:** `_time:1h service.name:"Learning Management Service" severity:ERROR`

**VictoriaLogs API response:**
```json
{
  "_msg": "db_query",
  "error": "(sqlalchemy.dialects.postgresql.asyncpg.InterfaceError) <class 'asyncpg.exceptions._base.InterfaceError'>: connection is closed",
  "event": "db_query",
  "service.name": "Learning Management Service",
  "severity": "ERROR",
  "trace_id": "a2ab11f6862417ce696b0b9eab874890"
}
```

**Observation:** VictoriaLogs provides structured JSON with all fields filterable. Much easier than grepping docker compose logs.

---

## Task 3B — Traces

### Checkpoint 1: Healthy trace

**Trace ID:** `0f1a6d43d343c190e5b2c6b40551102f`

**Span hierarchy:**
```
- GET /items/: 8 spans total
  - SELECT db-lab-8 (database query)
  - GET /items/ http send (response)
  - auth (authentication)
  - request_started, request_completed
```

### Checkpoint 2: Error trace

**Trace ID:** `a2ab11f6862417ce696b0b9eab874890`

**Span hierarchy with error:**
```
- GET /items/: 6 spans total
  - SELECT db-lab-8 ⚠️ ERROR
    Error: "connection is closed"
  - GET /items/ http send
  - connect
```

**Observation:** The error trace clearly shows the database span failed with "connection is closed" error.

---

## Task 3C — Observability MCP tools

### Checkpoint 1: Normal conditions (no recent errors)

**Question:** "Any LMS backend errors in the last 10 minutes?"

**Agent tool calls:**
```
Tool call: mcp_obs_mcp_obs_logs_error_count({"service": "Learning Management Service", "time_range": "10m"})
Tool call: mcp_obs_mcp_obs_logs_search({"query": "service.name:\"Learning Management Service\" severity:ERROR", "time_range": "10m"})
```

**Agent response:**
```
I checked for LMS backend errors in the last 10 minutes. No errors were found.
The Learning Management Service is running normally.
```

### Checkpoint 2: After triggering failure (PostgreSQL stopped)

**Question:** "Any LMS backend errors in the last 10 minutes?"

**Agent tool calls:**
```
Tool call: mcp_obs_mcp_obs_logs_error_count({"service": "Learning Management Service", "time_range": "10m"})
Tool call: mcp_obs_mcp_obs_logs_search({"query": "service.name:\"Learning Management Service\" severity:ERROR", "time_range": "10m"})
Tool call: mcp_lms_lms_health({})
Tool call: mcp_lms_lms_labs({})
```

**Agent response:**
```
Based on my checks, the LMS backend is currently experiencing issues. Here's what I found:

1. Database connection errors detected in the last 10 minutes
2. Error: "connection is closed" - PostgreSQL appears to be unavailable
3. The health check confirms the backend is struggling to connect to the database

The errors started when the database became unreachable. Requests are failing at the db_query step.
```

**Observation:** The agent correctly:
1. Used `logs_error_count` to check for errors
2. Used `logs_search` to inspect error details
3. Extracted the error message from logs
4. Provided a concise summary without dumping raw JSON

---

## Summary Task 3

- **Structured logging understood:** ✅ Can identify `request_started`, `auth_success`, `db_query`, `request_completed` events
- **VictoriaLogs queries working:** ✅ Can filter by `service.name`, `severity`, `trace_id`
- **VictoriaTraces explored:** ✅ Can view span hierarchy and identify error spans
- **MCP observability tools created:** ✅ 4 tools (`logs_search`, `logs_error_count`, `traces_list`, `traces_get`)
- **Observability skill written:** ✅ Teaches agent to search logs first, then fetch traces
- **Agent answers observability questions:** ✅ Correctly reports errors under both normal and failure conditions
