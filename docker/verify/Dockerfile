# docker/verify/Dockerfile - sandbox image for the swarm's verifier (P5).
#
# Build:  docker build -t zeus-swarm-verify:latest docker/verify
#
# SandboxedCommandVerifier runs a node's LLM-authored `check` inside this image,
# against a bind-mounted git worktree at /work, as the host user, with NO network
# by default (see build_verify_docker_command). The point is isolation: the check
# never touches the host beyond the worktree.
#
# This is a LEAN image: it covers `ruff check`, `python -c '...'`, and pytest for
# self-contained tests. For a check that imports your application (and therefore
# needs its dependencies), point ZEUS_SWARM_VERIFY_IMAGE at an image that already
# carries the repo's runtime env (e.g. your project's own zeus-core image) - the
# verifier only shells `<image> bash -c "<check>"`, so any image with the
# toolchain works.

FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        git ripgrep ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Common check tooling. Pinned loosely; extend per-stack as needed.
RUN pip install --no-cache-dir ruff pytest

# Worktree is bind-mounted here at runtime; HOME is a tmpfs (see the command builder).
WORKDIR /work

# No entrypoint: `docker run <image> bash -c "<check>"` provides the full argv.
ENTRYPOINT []
CMD ["python", "--version"]
