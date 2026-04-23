# zeus/core/middleware.py — Query logging middleware (Sprint 9a / LAB-147)
# Records request_id, path, latency_ms, and status for every query through
# the chat and oracle endpoints. Attaches X-Request-Id header to responses.
import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware

from zeus.core.admin import record_query

logger = logging.getLogger("zeus.query")

_LOGGED_PREFIXES = ("/chat/message", "/context/query")


class QueryLoggingMiddleware(BaseHTTPMiddleware):
    """Log latency and metadata for chat/oracle query paths."""

    async def dispatch(self, request, call_next):
        if not any(request.url.path.startswith(p) for p in _LOGGED_PREFIXES):
            return await call_next(request)

        request_id = str(uuid.uuid4())[:8]
        start = time.monotonic()

        response = await call_next(request)

        latency_ms = round((time.monotonic() - start) * 1000, 1)
        entry = {
            "request_id": request_id,
            "path": request.url.path,
            "latency_ms": latency_ms,
            "status": response.status_code,
        }
        logger.info("query", extra=entry)
        record_query(request.app, entry)
        response.headers["X-Request-Id"] = request_id
        return response
