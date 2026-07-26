# docker/egress-proxy/Dockerfile - allowlist egress proxy for the swarm sandbox.
#
# A tinyproxy that DENIES every host except the ones in `allowlist` (default:
# *.anthropic.com). The worker container joins an --internal network (no route to
# the internet) with HTTPS_PROXY pointing here, so this proxy is its only way out
# and it can only reach Anthropic. See README.md.
#
# Build:  docker build -t zeus-swarm-egress-proxy:latest docker/egress-proxy

FROM alpine:3.20

RUN apk add --no-cache tinyproxy

COPY tinyproxy.conf /etc/tinyproxy/tinyproxy.conf
COPY allowlist /etc/tinyproxy/allowlist

EXPOSE 8888

# Run in the foreground so docker manages the lifecycle.
CMD ["tinyproxy", "-d", "-c", "/etc/tinyproxy/tinyproxy.conf"]
