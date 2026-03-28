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
