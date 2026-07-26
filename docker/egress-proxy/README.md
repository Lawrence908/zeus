# Swarm sandbox egress lockdown

By default the sandboxed worker (`ZEUS_SWARM_WORKER=sandbox`) runs on the docker
`bridge` network with **unrestricted egress**. Since the worker runs LLM-authored
code, that is a data-exfiltration surface. The `proxy` egress policy closes it:
the worker joins an **internal** network with no route to the internet and sends
all traffic through this allowlist proxy, which only permits `*.anthropic.com`.

## One-time setup

```bash
# 1. Build the proxy image.
docker build -t zeus-swarm-egress-proxy:latest docker/egress-proxy

# 2. Create the internal (no-internet) network the worker will use.
docker network create --internal zeus-swarm-egress

# 3. Create a normal network for the proxy's own outbound access.
docker network create zeus-swarm-egress-out

# 4. Run the proxy attached to BOTH: internal (to receive worker traffic) and
#    the outbound network (to reach Anthropic).
docker run -d --name zeus-swarm-egress-proxy \
  --restart unless-stopped \
  --network zeus-swarm-egress \
  zeus-swarm-egress-proxy:latest
docker network connect zeus-swarm-egress-out zeus-swarm-egress-proxy
```

## Point the swarm at it

Set on `zeus-core`:

```bash
ZEUS_SWARM_SANDBOX_EGRESS=proxy
ZEUS_SWARM_SANDBOX_NETWORK=zeus-swarm-egress          # the --internal network
ZEUS_SWARM_EGRESS_PROXY=http://zeus-swarm-egress-proxy:8888
```

Now every worker container is launched on `zeus-swarm-egress` (no direct route
out) with `HTTPS_PROXY` pointing at the proxy, so it can reach Anthropic and
nothing else. `ANTHROPIC_API_KEY` must still be set for the sandboxed worker.

## Verifying

Inside a throwaway container on the internal network:

```bash
docker run --rm --network zeus-swarm-egress \
  -e HTTPS_PROXY=http://zeus-swarm-egress-proxy:8888 curlimages/curl:latest \
  -sS -o /dev/null -w '%{http_code}\n' https://api.anthropic.com/   # reaches Anthropic
docker run --rm --network zeus-swarm-egress \
  -e HTTPS_PROXY=http://zeus-swarm-egress-proxy:8888 curlimages/curl:latest \
  -sS https://example.com/                                          # denied by the proxy
```

## Allowing more hosts

Add extended-regex lines to `allowlist` (e.g. a package registry a run needs),
rebuild the image, and recreate the proxy container. Keep it minimal.

## Other modes

- `ZEUS_SWARM_SANDBOX_EGRESS=open` (default): the `bridge` network, unrestricted.
- `ZEUS_SWARM_SANDBOX_EGRESS=none`: `--network none`, no egress at all (the
  worker cannot reach Anthropic, so only useful for offline/local workers).
