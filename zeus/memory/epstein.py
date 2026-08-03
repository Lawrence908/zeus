# zeus/memory/epstein.py — Live HTTP proxy to the external Epstein research API.
#
# Follows the Reference-layer pattern (zeus/memory/reference.py): a thin async
# client that queries a purpose-built external service AT REQUEST TIME and
# stores nothing locally. The ~1.3M-document DOJ/court corpus, all retrieval,
# the entity graph, and the deep-research LLM live in the SEPARATE `epstein`
# service. Zeus never ingests any of it.
#
# The service exposes /api/research/* (see GET /api/research/capabilities for
# the authoritative, evolving manifest). This client is deliberately a thin
# transport: it does not interpret doc types or filter fields — callers read
# those from the live capabilities manifest so the two services can evolve
# independently.
#
# Safety: this corpus involves victims and unproven allegations. Read-only by
# construction — there is NO write path to the epstein service here. Callers
# must echo the manifest's `safety_rules` into any agent/system prompt and
# render allegations as allegations. See CLAUDE.md "Safety and ethics".
from __future__ import annotations

import asyncio
import logging
import os
from dataclasses import dataclass
from typing import Any

import httpx

logger = logging.getLogger("zeus.memory.epstein")


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


# Ordered probe list used when ZEUS_EPSTEIN_BASE_URL is not set. First to return
# 200 on /api/research/capabilities wins. The docker-network name resolves only
# when zeus-core shares the homelab-web network with epstein-backend; the LAN IP
# and the public TLS host are fallbacks.
_DEFAULT_CANDIDATES = (
    "http://epstein-backend:8000",
    "http://192.168.50.128:8170",
    "https://epstein.chrislawrence.ca",
)

# Timeouts (seconds). Fast reads get a tight cap; the synchronous `ask` and
# job creation get more room. Job polling uses the fast cap per poll.
_FAST_TIMEOUT = 15.0
_JOB_START_TIMEOUT = 20.0
_ASK_TIMEOUT = float(os.getenv("ZEUS_EPSTEIN_ASK_TIMEOUT", "300") or 300)


class EpsteinError(RuntimeError):
    """Raised on transport/HTTP failure so tools can format a graceful message.

    `status` is the HTTP status code when the failure was an error response
    (e.g. 503 when the entity graph is down), else None.
    """

    def __init__(self, message: str, *, status: int | None = None) -> None:
        super().__init__(message)
        self.status = status


@dataclass
class EpsteinHit:
    """One retrieved excerpt from the corpus.

    Mirrors the /api/research/search result shape. `document_id` +
    `source_label` are the citation handle every rendered claim must carry.
    """

    text: str
    document_id: str
    source_label: str
    doc_type: str
    chunk_index: str
    score: float

    @classmethod
    def from_api(cls, d: dict[str, Any]) -> "EpsteinHit":
        return cls(
            text=str(d.get("text", "")),
            document_id=str(d.get("document_id", "")),
            source_label=str(d.get("source_label", "")),
            doc_type=str(d.get("doc_type", "")),
            chunk_index=str(d.get("chunk_index", "")),
            score=float(d.get("score", 0.0) or 0.0),
        )

    def citation(self) -> str:
        """Compact inline citation handle: doc id + source label."""
        label = self.source_label or self.doc_type or "corpus"
        return f"{self.document_id} ({label})"


class EpsteinClient:
    """Async client for the epstein research API (seven read-only endpoints).

    Base-URL resolution is lazy: the first call that needs the network probes
    the candidate list (or uses ZEUS_EPSTEIN_BASE_URL verbatim) and caches the
    winner. An optional bearer token is sent as `Authorization: Bearer <key>`
    so the currently-open, network-isolated API can be locked down later
    without a client change.
    """

    def __init__(
        self,
        base_url: str = "",
        *,
        api_key: str = "",
        write_api_key: str = "",
        candidates: tuple[str, ...] = _DEFAULT_CANDIDATES,
    ) -> None:
        self._configured_base = base_url.rstrip("/") if base_url else ""
        self._api_key = api_key.strip()
        # Separate, stricter credential for the findings write routes. The write
        # path is closed by default server-side; without this key writes 403.
        self._write_api_key = write_api_key.strip()
        self._candidates = candidates
        self._resolved_base: str | None = self._configured_base or None
        self._resolve_lock = asyncio.Lock()

    # -- infrastructure --------------------------------------------------

    def _headers(self) -> dict[str, str] | None:
        if self._api_key:
            return {"Authorization": f"Bearer {self._api_key}"}
        return None

    def _write_headers(self) -> dict[str, str] | None:
        if self._write_api_key:
            return {"Authorization": f"Bearer {self._write_api_key}"}
        return None

    @property
    def write_enabled(self) -> bool:
        return bool(self._write_api_key)

    async def _base(self) -> str:
        """Return the working base URL, probing candidates once if needed."""
        if self._resolved_base:
            return self._resolved_base
        async with self._resolve_lock:
            if self._resolved_base:
                return self._resolved_base
            for cand in self._candidates:
                url = cand.rstrip("/")
                try:
                    async with httpx.AsyncClient(
                        timeout=_FAST_TIMEOUT, headers=self._headers()
                    ) as client:
                        resp = await client.get(f"{url}/api/research/capabilities")
                    if resp.status_code == 200:
                        self._resolved_base = url
                        logger.info("epstein API resolved to %s", url)
                        return url
                    logger.debug("epstein probe %s -> HTTP %s", url, resp.status_code)
                except Exception as exc:  # noqa: BLE001 - probe is best-effort
                    logger.debug("epstein probe %s failed: %s", url, exc)
            raise EpsteinError(
                "epstein API unreachable on all candidate base URLs: "
                + ", ".join(self._candidates)
            )

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        timeout: float = _FAST_TIMEOUT,
        write: bool = False,
    ) -> Any:
        base = await self._base()
        url = f"{base}{path}"
        headers = self._write_headers() if write else self._headers()
        try:
            async with httpx.AsyncClient(
                timeout=timeout, headers=headers, follow_redirects=True
            ) as client:
                resp = await client.request(method, url, json=json, params=params)
        except httpx.HTTPError as exc:
            raise EpsteinError(f"{method} {path} failed: {exc}") from exc
        if resp.status_code >= 400:
            body = (resp.text or "")[:300]
            raise EpsteinError(
                f"{method} {path} -> HTTP {resp.status_code}: {body}",
                status=resp.status_code,
            )
        try:
            return resp.json()
        except ValueError as exc:
            raise EpsteinError(f"{method} {path}: non-JSON response") from exc

    @property
    def resolved_base(self) -> str | None:
        return self._resolved_base

    # -- endpoints -------------------------------------------------------

    async def capabilities(self) -> dict[str, Any]:
        """GET /api/research/capabilities — the authoritative live manifest.

        Doc types, filter fields, endpoints, graph availability, auth mode,
        and the `safety_rules` string. Call this first; do not hardcode any of
        it. Also usable as a reachability probe.
        """
        return await self._request("GET", "/api/research/capabilities")

    async def search(
        self,
        query: str,
        *,
        doc_type: str | None = None,
        date_mentioned: str | None = None,
        document_ids: list[str] | None = None,
        n_results: int = 10,
        expand_graph: bool = False,
    ) -> dict[str, Any]:
        """POST /api/research/search — fast dense retrieval (+optional graph).

        Returns {"results": [...], "entities"?: {...}}. Results are the raw
        API dicts; use EpsteinHit.from_api to normalise if desired.
        """
        payload: dict[str, Any] = {
            "query": query,
            "n_results": max(1, min(50, int(n_results))),
            "expand_graph": bool(expand_graph),
        }
        if doc_type:
            payload["doc_type"] = doc_type
        if date_mentioned:
            payload["date_mentioned"] = date_mentioned
        if document_ids:
            payload["document_ids"] = document_ids
        return await self._request("POST", "/api/research/search", json=payload)

    async def document(self, document_id: str) -> dict[str, Any]:
        """GET /api/research/document/{id} — reconstructed full text + metadata."""
        return await self._request(
            "GET", f"/api/research/document/{document_id}"
        )

    async def entity(
        self, name: str, *, depth: int = 1, related_to: str | None = None
    ) -> dict[str, Any]:
        """GET /api/research/entity/{name} — graph dossier.

        Raises EpsteinError(status=503) when the graph backend is down; callers
        must degrade gracefully (mention is not involvement — an entity being
        in the graph is a co-occurrence signal, never an accusation).
        """
        params: dict[str, Any] = {"depth": max(1, min(3, int(depth)))}
        if related_to:
            params["related_to"] = related_to
        return await self._request(
            "GET", f"/api/research/entity/{name}", params=params
        )

    async def ask(
        self,
        question: str,
        *,
        doc_type: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        entity: str | None = None,
        document_ids: list[str] | None = None,
        include_timeline: bool = True,
    ) -> dict[str, Any]:
        """POST /api/research/ask — synchronous grounded answer. SLOW (minutes).

        Prefer async jobs (start_job/get_job) for deep synthesis. This may time
        out under GPU contention; the caller should treat prose as best-effort
        and still surface any citations.
        """
        payload: dict[str, Any] = {
            "question": question,
            "include_timeline": bool(include_timeline),
        }
        if doc_type:
            payload["doc_type"] = doc_type
        if date_from:
            payload["date_from"] = date_from
        if date_to:
            payload["date_to"] = date_to
        if entity:
            payload["entity"] = entity
        if document_ids:
            payload["document_ids"] = document_ids
        return await self._request(
            "POST", "/api/research/ask", json=payload, timeout=_ASK_TIMEOUT
        )

    async def start_job(
        self,
        question: str,
        *,
        doc_type: str | None = None,
        date_mentioned: str | None = None,
        depth: int = 3,
    ) -> dict[str, Any]:
        """POST /api/research/jobs — start an async deep-research job.

        Returns {"job_id", "status"}. The job decomposes -> retrieves ->
        synthesizes a cited report. Retrieval + citations land even when the
        synthesis step times out (known GPU-contention caveat).
        """
        payload: dict[str, Any] = {
            "question": question,
            "depth": max(1, min(5, int(depth))),
        }
        if doc_type:
            payload["doc_type"] = doc_type
        if date_mentioned:
            payload["date_mentioned"] = date_mentioned
        return await self._request(
            "POST", "/api/research/jobs", json=payload, timeout=_JOB_START_TIMEOUT
        )

    async def get_job(self, job_id: str) -> dict[str, Any]:
        """GET /api/research/jobs/{id} — poll status/steps/report/citations."""
        return await self._request("GET", f"/api/research/jobs/{job_id}")

    async def list_jobs(self) -> dict[str, Any]:
        """GET /api/research/jobs — recent jobs."""
        return await self._request("GET", "/api/research/jobs")

    async def submit_finding(
        self,
        *,
        kind: str,
        subject: str,
        body_md: str,
        citations: list[dict[str, Any]],
        confidence: str | None = None,
        gaps: list[str] | None = None,
        provenance: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """POST /api/research/findings — store a cited case-context proposal.

        WRITE route: requires the write bearer (ZEUS_EPSTEIN_WRITE_API_KEY); the
        server refuses (403) without a write key provisioned. Citations are
        required. The finding lands as `proposed`; it never mutates the corpus and
        is not reflected into context/claims files until a human accepts it."""
        payload: dict[str, Any] = {
            "kind": kind,
            "subject": subject,
            "body_md": body_md,
            "citations": citations,
            "gaps": gaps or [],
        }
        if confidence:
            payload["confidence"] = confidence
        if provenance:
            payload["provenance"] = provenance
        return await self._request(
            "POST", "/api/research/findings", json=payload, write=True
        )

    async def list_findings(
        self, *, limit: int = 50, status: str | None = None
    ) -> dict[str, Any]:
        """GET /api/research/findings — recent findings (read access)."""
        params: dict[str, Any] = {"limit": max(1, min(200, int(limit)))}
        if status:
            params["status"] = status
        return await self._request("GET", "/api/research/findings", params=params)

    async def set_finding_status(self, finding_id: str, status: str) -> dict[str, Any]:
        """POST /api/research/findings/{id}/accept — set review status. WRITE route."""
        return await self._request(
            "POST",
            f"/api/research/findings/{finding_id}/accept",
            json={"status": status},
            write=True,
        )


_client_singleton: EpsteinClient | None = None
_initialised = False


def get_epstein_client() -> EpsteinClient | None:
    """Return the process-wide client, gated by ZEUS_EPSTEIN_ENABLED (default off).

    - ZEUS_EPSTEIN_ENABLED (default "0")
    - ZEUS_EPSTEIN_BASE_URL (optional; skips probing when set)
    - ZEUS_EPSTEIN_API_KEY (optional read bearer token)
    - ZEUS_EPSTEIN_WRITE_API_KEY (optional; required for findings write-back)
    """
    global _client_singleton, _initialised
    if _initialised:
        return _client_singleton
    if _env_bool("ZEUS_EPSTEIN_ENABLED", False):
        base = os.getenv("ZEUS_EPSTEIN_BASE_URL", "").strip()
        api_key = os.getenv("ZEUS_EPSTEIN_API_KEY", "").strip()
        write_api_key = os.getenv("ZEUS_EPSTEIN_WRITE_API_KEY", "").strip()
        _client_singleton = EpsteinClient(base, api_key=api_key, write_api_key=write_api_key)
        logger.info(
            "epstein research client enabled (base=%s, auth=%s, write=%s)",
            base or "probe",
            "bearer" if api_key else "open",
            "on" if write_api_key else "off",
        )
    _initialised = True
    return _client_singleton


def reset_epstein_client() -> None:
    """Test hook — drop the singleton so env changes are re-read."""
    global _client_singleton, _initialised
    _client_singleton = None
    _initialised = False
