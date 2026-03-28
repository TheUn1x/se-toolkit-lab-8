#!/usr/bin/env python3
"""Entrypoint for nanobot gateway in Docker.

Resolves environment variables into config.json at runtime, then launches nanobot gateway.
"""

import json
import os
import sys
from pathlib import Path


def resolve_config() -> str:
    """Read config.json, inject env vars, write config.resolved.json."""
    config_path = Path(__file__).parent / "config.json"
    resolved_path = Path(__file__).parent / "config.resolved.json"

    with open(config_path) as f:
        config = json.load(f)

    # Inject LLM provider settings from env vars
    llm_api_key = os.environ.get("LLM_API_KEY")
    llm_api_base = os.environ.get("LLM_API_BASE_URL")
    llm_model = os.environ.get("LLM_API_MODEL")

    if llm_api_key:
        config["providers"]["custom"]["apiKey"] = llm_api_key
    if llm_api_base:
        config["providers"]["custom"]["apiBase"] = llm_api_base
    if llm_model:
        config["agents"]["defaults"]["model"] = llm_model

    # Inject gateway settings
    gateway_host = os.environ.get("NANOBOT_GATEWAY_CONTAINER_ADDRESS")
    gateway_port = os.environ.get("NANOBOT_GATEWAY_CONTAINER_PORT")
    if gateway_host:
        config.setdefault("gateway", {})["host"] = gateway_host
    if gateway_port:
        config.setdefault("gateway", {})["port"] = int(gateway_port)

    # Inject webchat channel settings if enabled
    webchat_host = os.environ.get("NANOBOT_WEBCHAT_CONTAINER_ADDRESS")
    webchat_port = os.environ.get("NANOBOT_WEBCHAT_CONTAINER_PORT")
    if webchat_host or webchat_port:
        config.setdefault("channels", {}).setdefault("webchat", {})
        if webchat_host:
            config["channels"]["webchat"]["host"] = webchat_host
        if webchat_port:
            config["channels"]["webchat"]["port"] = int(webchat_port)

    # Inject MCP server env vars for LMS
    lms_backend_url = os.environ.get("NANOBOT_LMS_BACKEND_URL")
    lms_api_key = os.environ.get("NANOBOT_LMS_API_KEY")
    if lms_backend_url or lms_api_key:
        mcp_config = config.setdefault("tools", {}).setdefault("mcpServers", {}).setdefault("lms", {})
        if lms_backend_url:
            mcp_config.setdefault("env", {})["NANOBOT_LMS_BACKEND_URL"] = lms_backend_url
        if lms_api_key:
            mcp_config.setdefault("env", {})["NANOBOT_LMS_API_KEY"] = lms_api_key

    # Inject MCP server settings for webchat UI delivery
    webchat_ui_relay_url = os.environ.get("NANOBOT_WEBCHAT_UI_RELAY_URL")
    webchat_ui_token = os.environ.get("NANOBOT_WEBCHAT_UI_TOKEN")
    nanobot_access_key = os.environ.get("NANOBOT_ACCESS_KEY")
    if webchat_ui_relay_url or webchat_ui_token or nanobot_access_key:
        webchat_mcp = config.setdefault("tools", {}).setdefault("mcpServers", {}).setdefault("webchat", {})
        webchat_mcp["command"] = "python"
        webchat_mcp["args"] = ["-m", "mcp_webchat"]
        webchat_mcp.setdefault("env", {})
        if webchat_ui_relay_url:
            webchat_mcp["env"]["NANOBOT_WEBCHAT_UI_RELAY_URL"] = webchat_ui_relay_url
        if webchat_ui_token:
            webchat_mcp["env"]["NANOBOT_WEBCHAT_UI_TOKEN"] = webchat_ui_token
        if nanobot_access_key:
            webchat_mcp["env"]["NANOBOT_ACCESS_KEY"] = nanobot_access_key

    # Write resolved config
    with open(resolved_path, "w") as f:
        json.dump(config, f, indent=2)

    return str(resolved_path)


def main() -> None:
    """Resolve config and launch nanobot gateway."""
    resolved_config = resolve_config()
    workspace = os.environ.get("NANOBOT_WORKSPACE", "./workspace")

    print(f"Using config: {resolved_config}", file=sys.stderr)

    # Launch nanobot gateway
    os.execvp("nanobot", ["nanobot", "gateway", "--config", resolved_config, "--workspace", workspace])


if __name__ == "__main__":
    main()
