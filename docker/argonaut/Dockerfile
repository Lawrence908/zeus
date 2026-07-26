# docker/argonaut/Dockerfile - sandbox image for the swarm's code argonaut.
#
# Build:  docker build -t zeus-swarm-argonaut:latest docker/argonaut
# The container runs `claude -p` against a bind-mounted git worktree at /work,
# as the host user (via `docker run --user`), with ANTHROPIC_API_KEY passed in.
# It owns no git; the coordinator commits on the host.

FROM node:22-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        git ripgrep ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# The headless Claude Code CLI (provides `claude` on PATH).
RUN npm install -g @anthropic-ai/claude-code \
    && npm cache clean --force

# Worktree is bind-mounted here at runtime; HOME is a tmpfs (see build_docker_command).
WORKDIR /work

# No entrypoint: `docker run <image> claude -p ...` provides the full argv.
ENTRYPOINT []
CMD ["claude", "--version"]
