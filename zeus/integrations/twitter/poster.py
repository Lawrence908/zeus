# zeus/integrations/twitter/poster.py - OAuth2 user-context tweet posting for Pheme.
#
# Ports the proven posting path from the api-clients PF Twitter integration
# (~/services/api-clients/resources/PF/Integrations/twitter/): POST /2/tweets
# with a user-context OAuth2 bearer token, refresh via /2/oauth2/token with
# basic client auth. The PF module itself depends on that app's DB/session
# stack, so the two HTTP calls are mirrored here rather than imported; token
# rotation persists to zeus/data/pheme/twitter_token.json instead of a DB.
#
# Safety contract (public, irreversible surface):
#   - twitter_enabled() gate: PHEME_TWITTER_ENABLED=1 required for any post
#   - every tweet text passes AegisPolicyEngine("pheme").evaluate_payload
#     inside post_news_thread - there is no ungated path to /2/tweets
#
# Env:
#   PHEME_TWITTER_ENABLED           master gate (default 0)
#   TWITTER_OAUTH2_CLIENT_ID        OAuth2 app client id (needed for refresh)
#   TWITTER_OAUTH2_CLIENT_SECRET    confidential-client secret (optional)
#   TWITTER_OAUTH2_ACCESS_TOKEN     initial user-context access token
#   TWITTER_OAUTH2_REFRESH_TOKEN    initial refresh token (offline.access scope)
from __future__ import annotations

import json
import logging
import os
from base64 import b64encode
from datetime import datetime, timezone
from pathlib import Path

import httpx

logger = logging.getLogger("zeus.twitter")

_API_BASE = os.getenv("TWITTER_API_BASE_URL", "https://api.twitter.com").rstrip("/")
_TOKEN_URL = f"{_API_BASE}/2/oauth2/token"
_TWEETS_URL = f"{_API_BASE}/2/tweets"


class TwitterPostError(RuntimeError):
    pass


def twitter_enabled() -> bool:
    return os.getenv("PHEME_TWITTER_ENABLED", "0").strip() in ("1", "true", "yes", "on")


def _token_state_path() -> Path:
    return Path(os.getenv("PHEME_DATA_DIR", "zeus/data/pheme")) / "twitter_token.json"


def _load_tokens() -> dict:
    """Rotated tokens from the state file win over the env-seeded ones."""
    state: dict = {}
    p = _token_state_path()
    if p.is_file():
        try:
            state = json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            logger.warning("corrupt twitter token state at %s, falling back to env", p)
    return {
        "access_token": state.get("access_token") or os.getenv("TWITTER_OAUTH2_ACCESS_TOKEN", ""),
        "refresh_token": state.get("refresh_token") or os.getenv("TWITTER_OAUTH2_REFRESH_TOKEN", ""),
    }


def _save_tokens(access_token: str, refresh_token: str) -> None:
    p = _token_state_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(
        json.dumps(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "rotated_at": datetime.now(timezone.utc).isoformat(),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    tmp.replace(p)


async def _refresh(client: httpx.AsyncClient, refresh_token: str) -> dict:
    client_id = os.getenv("TWITTER_OAUTH2_CLIENT_ID", "").strip()
    client_secret = os.getenv("TWITTER_OAUTH2_CLIENT_SECRET", "").strip()
    if not refresh_token or not client_id:
        raise TwitterPostError(
            "access token expired and no refresh credentials configured "
            "(TWITTER_OAUTH2_REFRESH_TOKEN + TWITTER_OAUTH2_CLIENT_ID)"
        )
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {"grant_type": "refresh_token", "refresh_token": refresh_token}
    if client_secret:
        headers["Authorization"] = "Basic " + b64encode(
            f"{client_id}:{client_secret}".encode()
        ).decode()
    else:
        data["client_id"] = client_id  # public client
    r = await client.post(_TOKEN_URL, headers=headers, data=data)
    if r.status_code != 200:
        raise TwitterPostError(f"token refresh failed: {r.status_code} {r.text[:200]}")
    body = r.json() or {}
    access = str(body.get("access_token", ""))
    new_refresh = str(body.get("refresh_token", "") or refresh_token)
    if not access:
        raise TwitterPostError("token refresh returned no access_token")
    _save_tokens(access, new_refresh)
    logger.info("twitter access token refreshed")
    return {"access_token": access, "refresh_token": new_refresh}


async def _post_one(
    client: httpx.AsyncClient, tokens: dict, text: str, reply_to: str | None
) -> tuple[str, dict]:
    """POST one tweet; on 401 refresh once and retry. Returns (tweet_id, tokens)."""
    payload: dict = {"text": text}
    if reply_to:
        payload["reply"] = {"in_reply_to_tweet_id": reply_to}
    for attempt in range(2):
        r = await client.post(
            _TWEETS_URL,
            json=payload,
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        if r.status_code == 401 and attempt == 0:
            tokens = await _refresh(client, tokens.get("refresh_token", ""))
            continue
        if r.status_code >= 400:
            raise TwitterPostError(f"tweet failed: {r.status_code} {r.text[:300]}")
        data = (r.json() or {}).get("data") or {}
        tweet_id = str(data.get("id", ""))
        if not tweet_id:
            raise TwitterPostError("twitter returned no tweet id")
        return tweet_id, tokens
    raise TwitterPostError("tweet failed after token refresh")


async def post_news_thread(lead: str, thread: list[str] | None = None) -> list[str]:
    """Post a lead tweet plus optional reply thread. Returns posted tweet ids.

    This is the single choke point to /2/tweets: env gate + Aegis pre-hook on
    every tweet text run here, so MCP, chat-path, Telegram-approve, and
    autopost callers are all gated identically.
    """
    if not twitter_enabled():
        raise TwitterPostError("twitter posting disabled (PHEME_TWITTER_ENABLED=0)")

    texts = [t.strip()[:280] for t in [lead, *(thread or [])] if t and t.strip()]
    if not texts:
        raise TwitterPostError("nothing to post")

    from zeus.safety.policy_engine import AegisPolicyEngine

    engine = AegisPolicyEngine(policy="pheme")
    for i, text in enumerate(texts):
        outcome = engine.evaluate_payload({"text": text})
        if outcome.status != "ok":
            raise TwitterPostError(
                f"aegis rejected tweet {i + 1}/{len(texts)}: {outcome.message}"
            )

    tokens = _load_tokens()
    if not tokens["access_token"] and not tokens["refresh_token"]:
        raise TwitterPostError("no twitter credentials configured (TWITTER_OAUTH2_*)")

    ids: list[str] = []
    async with httpx.AsyncClient(timeout=30.0) as client:
        if not tokens["access_token"] and tokens["refresh_token"]:
            tokens = await _refresh(client, tokens["refresh_token"])
        reply_to: str | None = None
        for text in texts:
            tweet_id, tokens = await _post_one(client, tokens, text, reply_to)
            ids.append(tweet_id)
            reply_to = tweet_id
    logger.info("posted %d tweet(s): %s", len(ids), ids)
    return ids
