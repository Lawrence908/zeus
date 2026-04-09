"""zeus/ingest/sources/newsletter.py — Iris newsletter email source parser.

Fetches newsletter emails via IMAP, filtered by sender address.
Supports both chunked output (for Qdrant ingest) and raw body retrieval
(for summarization endpoints).

Environment variables:
  NEWSLETTER_IMAP_HOST     (default: imap.gmail.com)
  NEWSLETTER_IMAP_USER
  NEWSLETTER_IMAP_PASS
  NEWSLETTER_IMAP_PORT     (default: 993)
  NEWSLETTER_MAILBOX       (default: INBOX)
  NEWSLETTER_SOURCES       JSON dict: {"tldr": "dan@tldrnewsletter.com", ...}
"""

from __future__ import annotations

import imaplib
import json
import logging
import os
import ssl
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from email import message_from_bytes
from typing import AsyncIterator

from zeus.ingest.pipeline import Chunk, chunk_text
from zeus.ingest.sources.email import _extract_body, _safe_dt

logger = logging.getLogger("iris.newsletter")


@dataclass(frozen=True)
class NewsletterConfig:
    imap_host: str
    imap_user: str
    imap_pass: str
    imap_port: int = 993
    mailbox: str = "INBOX"
    sources: dict[str, str] = field(default_factory=dict)  # type → sender email
    limit: int = 50
    since_days: int = 7


@dataclass
class RawNewsletter:
    """A single fetched newsletter with full body (not chunked)."""

    newsletter_type: str
    subject: str
    sender: str
    date_iso: str
    message_id: str
    body: str


class NewsletterSource:
    def __init__(
        self,
        *,
        config: NewsletterConfig,
        chunk_size: int = 512,
        chunk_overlap: int = 64,
        user_id: str = "chris",
    ) -> None:
        self.config = config
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.user_id = user_id

    @staticmethod
    def from_env(*, limit: int = 50, since_days: int = 7) -> NewsletterConfig:
        host = os.getenv("NEWSLETTER_IMAP_HOST", "imap.gmail.com").strip()
        user = os.getenv("NEWSLETTER_IMAP_USER", "").strip()
        password = os.getenv("NEWSLETTER_IMAP_PASS", "")
        port = int(os.getenv("NEWSLETTER_IMAP_PORT", "993"))
        mailbox = os.getenv("NEWSLETTER_MAILBOX", "INBOX")
        sources_raw = os.getenv("NEWSLETTER_SOURCES", "{}").strip()
        try:
            sources = json.loads(sources_raw)
        except json.JSONDecodeError:
            raise ValueError(
                f"NEWSLETTER_SOURCES must be valid JSON, got: {sources_raw[:100]}"
            )
        if not isinstance(sources, dict):
            raise ValueError(
                "NEWSLETTER_SOURCES must be a JSON object, got: "
                f"{type(sources).__name__}"
            )
        if not user or not password:
            raise ValueError(
                "NEWSLETTER_IMAP_USER and NEWSLETTER_IMAP_PASS must be set"
            )
        # Validate each entry is a non-empty string
        validated: dict[str, str] = {}
        for key, val in sources.items():
            if not isinstance(val, str) or not val.strip():
                raise ValueError(
                    f"NEWSLETTER_SOURCES[{key!r}] must be a non-empty string, "
                    f"got: {val!r}"
                )
            validated[str(key)] = val.strip()
        if not validated:
            raise ValueError(
                "NEWSLETTER_SOURCES must contain at least one entry"
            )
        return NewsletterConfig(
            imap_host=host,
            imap_user=user,
            imap_pass=password,
            imap_port=port,
            mailbox=mailbox,
            sources=validated,
            limit=limit,
            since_days=since_days,
        )

    def _connect(self) -> imaplib.IMAP4_SSL:
        cfg = self.config
        ctx = ssl.create_default_context()
        imap = imaplib.IMAP4_SSL(cfg.imap_host, cfg.imap_port, ssl_context=ctx)
        imap.login(cfg.imap_user, cfg.imap_pass)
        imap.select(cfg.mailbox)
        return imap

    def _since_date_str(self) -> str:
        """IMAP date string for SINCE filter."""
        dt = datetime.now(timezone.utc) - timedelta(days=self.config.since_days)
        return dt.strftime("%d-%b-%Y")

    def _classify_sender(self, sender: str) -> str | None:
        """Return newsletter type if sender matches a configured source."""
        sender_lower = sender.lower()
        for ntype, email_addr in self.config.sources.items():
            if email_addr.lower() in sender_lower:
                return ntype
        return None

    def _fetch_from_imap(
        self,
        *,
        newsletter_type: str | None = None,
    ) -> list[RawNewsletter]:
        """Fetch newsletters from IMAP, optionally filtered by type."""
        cfg = self.config
        since_str = self._since_date_str()
        results: list[RawNewsletter] = []
        seen_ids: set[str] = set()

        # Determine which senders to fetch
        if newsletter_type and newsletter_type != "all":
            if newsletter_type not in cfg.sources:
                logger.warning("unknown newsletter type: %s", newsletter_type)
                return []
            senders = {newsletter_type: cfg.sources[newsletter_type]}
        else:
            senders = cfg.sources

        imap = self._connect()
        try:
            for ntype, sender_email in senders.items():
                status, data = imap.search(
                    None, "FROM", f'"{sender_email}"', "SINCE", since_str
                )
                if status != "OK" or not data or not data[0]:
                    logger.info("no emails found for %s (%s)", ntype, sender_email)
                    continue

                ids = data[0].split()
                ids = list(reversed(ids))[: max(cfg.limit, 1)]
                logger.info(
                    "found %d emails for %s (%s)", len(ids), ntype, sender_email
                )

                for msg_id in ids:
                    status, msg_data = imap.fetch(msg_id, "(RFC822)")
                    if status != "OK" or not msg_data:
                        continue
                    raw = msg_data[0][1]
                    if not isinstance(raw, (bytes, bytearray)):
                        continue

                    msg = message_from_bytes(raw)
                    message_id = str(msg.get("Message-ID") or "").strip()

                    # Dedup by Message-ID
                    dedup_key = message_id or msg_id.decode("utf-8", errors="replace")
                    if dedup_key in seen_ids:
                        continue
                    seen_ids.add(dedup_key)

                    subject = str(msg.get("Subject") or "").strip()
                    sender = str(msg.get("From") or "").strip()
                    date_iso = _safe_dt(str(msg.get("Date") or ""))

                    body, _ = _extract_body(msg)
                    if not body:
                        continue

                    results.append(
                        RawNewsletter(
                            newsletter_type=ntype,
                            subject=subject,
                            sender=sender,
                            date_iso=date_iso,
                            message_id=dedup_key,
                            body=body,
                        )
                    )
        finally:
            try:
                imap.logout()
            except Exception:
                try:
                    imap.shutdown()
                except Exception:
                    pass

        return results

    def fetch_newsletters_raw(
        self,
        *,
        newsletter_type: str = "all",
        num_recent: int = 1,
    ) -> list[RawNewsletter]:
        """Fetch raw newsletter bodies for summarization (not chunked).

        Results are sorted by date descending so slicing by num_recent
        always returns the most recent newsletters across all senders.
        """
        all_newsletters = self._fetch_from_imap(newsletter_type=newsletter_type)
        # Sort by date descending — empty dates sort last
        all_newsletters.sort(key=lambda nl: nl.date_iso or "", reverse=True)
        return all_newsletters[:num_recent]

    async def chunks(self) -> AsyncIterator[Chunk]:
        """Yield chunked newsletter content for Qdrant ingest."""
        newsletters = self._fetch_from_imap()
        for nl in newsletters:
            header = f"Subject: {nl.subject}\nFrom: {nl.sender}"
            if nl.date_iso:
                header += f"\nDate: {nl.date_iso}"

            doc = f"{header}\n\n{nl.body}".strip()

            for piece in chunk_text(doc, self.chunk_size, self.chunk_overlap):
                yield Chunk(
                    text=piece,
                    source=f"newsletter:{nl.newsletter_type}",
                    metadata={
                        "type": "newsletter",
                        "newsletter_type": nl.newsletter_type,
                        "subject": nl.subject,
                        "from": nl.sender,
                        "date": nl.date_iso,
                        "message_id": nl.message_id,
                    },
                    user_id=self.user_id,
                )
