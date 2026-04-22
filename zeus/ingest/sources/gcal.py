# zeus/ingest/sources/gcal.py — Google Calendar ingest source (Sprint 10c)
# Fetches events from the primary Google Calendar and yields chunks.
# Auth: OAuth2 "installed application" flow.
#   First-time setup: python -m zeus.ingest.sources.gcal --auth
#   Token stored at GCAL_TOKEN_PATH (default: zeus/data/gcal_token.json)
import logging
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import AsyncIterator

from zeus.ingest.types import Chunk

logger = logging.getLogger("iris.gcal")

_SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
_DEFAULT_CREDENTIALS = "zeus/data/gcal_credentials.json"
_DEFAULT_TOKEN = "zeus/data/gcal_token.json"


def _load_credentials(credentials_path: str, token_path: str):
    """Load or refresh OAuth2 credentials. Returns google.oauth2.credentials.Credentials."""
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError as exc:
        raise ImportError(
            "Google Calendar support requires: pip install google-api-python-client google-auth-oauthlib"
        ) from exc

    creds = None
    token_file = Path(token_path)

    if token_file.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(token_file), _SCOPES)
        except (ValueError, KeyError) as exc:
            # Common mistake: copying gcal_credentials.json to gcal_token.json
            logger.warning(
                "gcal: token file %s is not a valid authorized-user token (%s). "
                "Remove it and run --auth again.",
                token_path,
                exc,
            )
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not Path(credentials_path).exists():
                raise FileNotFoundError(
                    f"Google OAuth credentials not found: {credentials_path}\n"
                    "Download from Google Cloud Console → APIs & Services → Credentials."
                )
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, _SCOPES)
            creds = flow.run_local_server(port=0)

        token_file.parent.mkdir(parents=True, exist_ok=True)
        token_file.write_text(creds.to_json())

    return creds


def _format_attendees(attendees: list[dict]) -> str:
    names = []
    for a in attendees or []:
        name = a.get("displayName") or a.get("email", "")
        if name:
            names.append(name)
    return ", ".join(names[:10])


def _event_to_text(event: dict) -> str:
    summary = event.get("summary", "(no title)")
    start_raw = event.get("start", {})
    start = start_raw.get("dateTime") or start_raw.get("date", "")
    date_label = start[:10]  # YYYY-MM-DD

    parts = [f"[{date_label}] calendar event: {summary}"]

    description = event.get("description", "").strip()
    if description:
        parts.append(f"— {description[:300]}")

    attendees_str = _format_attendees(event.get("attendees", []))
    if attendees_str:
        parts.append(f"(attendees: {attendees_str})")

    location = event.get("location", "").strip()
    if location:
        parts.append(f"(location: {location})")

    return " ".join(parts)


class GoogleCalendarSource:
    """
    Ingest events from Google Calendar primary calendar.

    Env vars:
      GCAL_CREDENTIALS_PATH  — OAuth client secrets JSON (from Google Cloud Console)
      GCAL_TOKEN_PATH        — stored token path (created on first auth)

    Config keys: credentials_path, token_path, days_back, days_forward
    """

    target: str = "memory"

    def __init__(
        self,
        credentials_path: str | None = None,
        token_path: str | None = None,
        days_back: int = 90,
        days_forward: int = 30,
        user_id: str = "chris",
    ) -> None:
        self.credentials_path = credentials_path or os.getenv("GCAL_CREDENTIALS_PATH", _DEFAULT_CREDENTIALS)
        self.token_path = token_path or os.getenv("GCAL_TOKEN_PATH", _DEFAULT_TOKEN)
        self.days_back = days_back
        self.days_forward = days_forward
        self.user_id = user_id

    async def chunks(self) -> AsyncIterator[Chunk]:
        try:
            from googleapiclient.discovery import build as gapi_build
        except ImportError as exc:
            logger.warning(
                "gcal: skipping — optional deps missing "
                "(pip install google-api-python-client google-auth-oauthlib): %s",
                exc,
            )
            return

        try:
            creds = _load_credentials(self.credentials_path, self.token_path)
        except FileNotFoundError as exc:
            logger.error("gcal: %s", exc)
            return
        except Exception as exc:
            logger.error("gcal: auth failed — %s", exc)
            return

        service = gapi_build("calendar", "v3", credentials=creds)

        now = datetime.now(timezone.utc)
        time_min = (now - timedelta(days=self.days_back)).isoformat()
        time_max = (now + timedelta(days=self.days_forward)).isoformat()

        seen_ids: set[str] = set()
        page_token = None
        total = 0

        while True:
            try:
                result = (
                    service.events()
                    .list(
                        calendarId="primary",
                        timeMin=time_min,
                        timeMax=time_max,
                        singleEvents=True,  # expand recurring events
                        orderBy="startTime",
                        maxResults=250,
                        pageToken=page_token,
                    )
                    .execute()
                )
            except Exception as exc:
                logger.error("gcal: API call failed — %s", exc)
                break

            for event in result.get("items", []):
                # Dedup recurring event instances by recurring_event_id + date
                event_id = event.get("recurringEventId") or event.get("id", "")
                start_date = (event.get("start", {}).get("dateTime") or event.get("start", {}).get("date", ""))[:10]
                dedup_key = f"{event_id}:{start_date}"

                if dedup_key in seen_ids:
                    continue
                seen_ids.add(dedup_key)

                # Skip private events
                if event.get("visibility") == "private":
                    continue

                text = _event_to_text(event)
                total += 1

                yield Chunk(
                    text=text,
                    source=f"gcal:{event.get('id', 'unknown')[:12]}",
                    metadata={
                        "event_id": event.get("id", ""),
                        "summary": event.get("summary", ""),
                        "start": start_date,
                        "calendar": "primary",
                        "type": "calendar_event",
                    },
                    user_id=self.user_id,
                )

            page_token = result.get("nextPageToken")
            if not page_token:
                break

        logger.info("gcal: yielded %d events (days_back=%d, days_forward=%d)", total, self.days_back, self.days_forward)


# ------------------------------------------------------------------
# Auth helper: python -m zeus.ingest.sources.gcal --auth
# ------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Zeus Google Calendar auth helper")
    parser.add_argument("--auth", action="store_true", help="Run OAuth2 flow to generate token")
    parser.add_argument("--credentials", default=_DEFAULT_CREDENTIALS)
    parser.add_argument("--token", default=_DEFAULT_TOKEN)
    args = parser.parse_args()

    if args.auth:
        creds = _load_credentials(args.credentials, args.token)
        print(f"Auth complete. Token saved to: {args.token}")
