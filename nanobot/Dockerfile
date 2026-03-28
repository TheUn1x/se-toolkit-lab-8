# Adapted from backend/Dockerfile and qwen-code-api/Dockerfile
# Also see https://docs.astral.sh/uv/guides/integration/docker/

# ---
# Stage 1: build the application in the `/app` directory.
# ---

ARG REGISTRY_PREFIX_DOCKER_HUB
FROM ${REGISTRY_PREFIX_DOCKER_HUB}astral/uv:python3.14-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Omit development dependencies
ENV UV_NO_DEV=1

# Disable Python downloads - use the system interpreter across both images.
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Copy workspace root files for dependency resolution (from additional_contexts)
COPY --from=workspace pyproject.toml uv.lock ./

# Copy mcp for mcp-lms and mcp-obs workspace dependencies
COPY --from=workspace mcp ./mcp

# Copy nanobot-websocket-channel for webchat packages
COPY --from=workspace nanobot-websocket-channel ./nanobot-websocket-channel

# Copy nanobot project files
COPY pyproject.toml ./pyproject.toml
COPY entrypoint.py ./entrypoint.py

# Sync nanobot dependencies (includes mcp-lms from workspace)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --package nanobot

# Copy the rest of nanobot source
COPY . ./

# ---
# Stage 2: use a final image without uv
# ---

ARG REGISTRY_PREFIX_DOCKER_HUB
FROM ${REGISTRY_PREFIX_DOCKER_HUB}python:3.14.2-slim-bookworm

# Set environment variables for Python and application
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Make sure we use UTF-8 encoding
ENV LANG=C.UTF-8

# Accept UID/GID as build args for non-root user
ARG APP_UID=999
ARG APP_GID=999

# Create non-root user with specified UID/GID
RUN groupadd --system --gid ${APP_GID} nonroot \
    && useradd --system --gid ${APP_GID} --uid ${APP_UID} --create-home nonroot

# Copy the application from the builder
COPY --from=builder --chown=nonroot:nonroot /app /app

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Use the non-root user
USER nonroot

WORKDIR /app

# Run the entrypoint script which resolves config and launches nanobot gateway
CMD ["python", "/app/entrypoint.py"]
