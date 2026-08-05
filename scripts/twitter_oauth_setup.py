# scripts/twitter_oauth_setup.py - One-time OAuth2 token bootstrap for Pheme's Twitter poster.
#
# Runs the X (Twitter) OAuth2 authorization-code + PKCE flow in the terminal
# and writes the resulting user-context tokens to zeus/data/pheme/twitter_token.json,
# which is where zeus/integrations/twitter/poster.py reads (and rotates) them.
# After this succeeds you never touch tokens again; the poster refreshes and
# rotates automatically.
#
# Prereqs (see zeus/docs/pheme-twitter-setup.md):
#   TWITTER_OAUTH2_CLIENT_ID      in zeus/.env  (required)
#   TWITTER_OAUTH2_CLIENT_SECRET  in zeus/.env  (confidential app; blank for public app)
#   Redirect/callback URL registered on the X app: http://localhost:8971/callback
#
# Usage (from repo root):
#   .venv/bin/python scripts/twitter_oauth_setup.py
from __future__ import annotations

import base64
import hashlib
import json
import os
import secrets
import sys
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv(".env")

AUTH_URL = "https://twitter.com/i/oauth2/authorize"
TOKEN_URL = "https://api.twitter.com/2/oauth2/token"
REDIRECT_URI = os.getenv("TWITTER_OAUTH2_REDIRECT_URI", "http://localhost:8971/callback")
SCOPES = "tweet.read tweet.write users.read offline.access"
TOKEN_STATE = Path(os.getenv("PHEME_DATA_DIR", "zeus/data/pheme")) / "twitter_token.json"


def main() -> int:
    client_id = os.getenv("TWITTER_OAUTH2_CLIENT_ID", "").strip()
    client_secret = os.getenv("TWITTER_OAUTH2_CLIENT_SECRET", "").strip()
    if not client_id:
        print("TWITTER_OAUTH2_CLIENT_ID is not set in .env - see zeus/docs/pheme-twitter-setup.md")
        return 1

    verifier = secrets.token_urlsafe(64)
    challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest())
        .decode()
        .rstrip("=")
    )
    state = secrets.token_urlsafe(16)
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES,
        "state": state,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
    }
    print("\n1. Open this URL in a browser logged in as the account that should tweet:\n")
    print(f"   {AUTH_URL}?{urllib.parse.urlencode(params)}\n")
    print("2. Authorize the app. The browser lands on an unreachable localhost URL - that's fine.")
    print("3. Paste that full redirect URL (or just the code= value) here.\n")
    raw = input("Redirect URL or code: ").strip()

    if "code=" in raw:
        query = urllib.parse.urlparse(raw).query or raw.split("?", 1)[-1]
        parsed = urllib.parse.parse_qs(query)
        if parsed.get("state", [state])[0] != state:
            print("state mismatch - aborting (use the URL from THIS run)")
            return 1
        code = parsed.get("code", [""])[0]
    else:
        code = raw
    if not code:
        print("no authorization code found")
        return 1

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "code_verifier": verifier,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    if client_secret:
        basic = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        headers["Authorization"] = f"Basic {basic}"
    else:
        data["client_id"] = client_id  # public client

    resp = httpx.post(TOKEN_URL, data=data, headers=headers, timeout=30.0)
    if resp.status_code != 200:
        print(f"token exchange failed: {resp.status_code} {resp.text[:300]}")
        return 1
    body = resp.json()
    access, refresh = body.get("access_token", ""), body.get("refresh_token", "")
    if not access or not refresh:
        print(f"unexpected token response: {json.dumps(body)[:300]}")
        return 1

    TOKEN_STATE.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_STATE.write_text(
        json.dumps(
            {
                "access_token": access,
                "refresh_token": refresh,
                "rotated_at": datetime.now(timezone.utc).isoformat(),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"\nTokens written to {TOKEN_STATE} (scopes: {body.get('scope', SCOPES)})")

    me = httpx.get(
        "https://api.twitter.com/2/users/me",
        headers={"Authorization": f"Bearer {access}"},
        timeout=30.0,
    )
    if me.status_code == 200:
        user = (me.json() or {}).get("data", {})
        print(f"Authorized as @{user.get('username')} ({user.get('name')})")
    else:
        print(f"note: /users/me check returned {me.status_code} - tokens still saved")

    print("\nNext: set PHEME_TWITTER_ENABLED=1 in .env and recreate zeus-core.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
