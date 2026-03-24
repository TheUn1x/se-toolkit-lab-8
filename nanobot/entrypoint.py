"""Resolve runtime env vars into MCP server configs, then start the gateway."""

import json
import os
import tempfile

CONFIG = "/app/nanobot/config.json"
WORKSPACE = "/app/nanobot/workspace"

# Env vars to forward into every MCP server subprocess.
_FORWARD_VARS = ["NANOBOT_LMS_BACKEND_URL"]


def main() -> None:
    with open(CONFIG) as f:
        config = json.load(f)

    # Network settings are controlled exclusively via env vars.
    webchat = config.setdefault("channels", {}).setdefault("webchat", {})
    webchat["host"] = os.environ.get("NANOBOT_WEBCHAT_CONTAINER_ADDRESS", "0.0.0.0")
    webchat["port"] = int(os.environ.get("NANOBOT_WEBCHAT_CONTAINER_PORT", "8765"))

    gateway = config.setdefault("gateway", {})
    gateway["host"] = os.environ.get("NANOBOT_GATEWAY_CONTAINER_ADDRESS", "0.0.0.0")
    gateway["port"] = int(os.environ.get("NANOBOT_GATEWAY_CONTAINER_PORT", "18790"))

    mcp_servers = config.get("tools", {}).get("mcp_servers", {})
    if mcp_servers:
        forward = {k: v for k in _FORWARD_VARS if (v := os.environ.get(k))}
        for srv in mcp_servers.values():
            env = srv.get("env", {})
            env.update(forward)
            srv["env"] = env

    with tempfile.NamedTemporaryFile(
        "w", suffix=".json", delete=False, dir="/tmp"
    ) as f:
        json.dump(config, f, indent=2)
        resolved = f.name

    os.execvp("nanobot", [
        "nanobot", "gateway",
        "--config", resolved,
        "--workspace", WORKSPACE,
    ])


if __name__ == "__main__":
    main()
