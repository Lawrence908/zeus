"""zeus/ingest/sources/email.py — Iris IMAP email source parser.

Environment variables:
  ZEUS_EMAIL_HOST
  ZEUS_EMAIL_USER
  ZEUS_EMAIL_PASSWORD
  ZEUS_EMAIL_PORT (optional, default 993)
  ZEUS_EMAIL_MAILBOX (optional, default INBOX)
  ZEUS_EMAIL_SCOPE (optional, default starred)
"""

from __future__ import annotations

import imaplib
import os
import re
import ssl
from dataclasses import dataclass
from datetime import datetime
from email import message_from_bytes
from email.message import Message
from email.utils import parsedate_to_datetime
from typing import AsyncIterator

from zeus.ingest.pipeline import Chunk, chunk_text


def _strip_html(html: str) -> str:
    html = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", html)
    html = re.sub(r"(?s)<.*?>", " ", html)
    html = re.sub(r"&nbsp;", " ", html)
    html = re.sub(r"\s+", " ", html)
    return html.strip()


def _decode_text(part: Message) -> str:
    payload = part.get_payload(decode=True)
    if payload is None:
        text = part.get_payload()  # type: ignore[assignment]
        return str(text or "").strip()
    charset = part.get_content_charset() or "utf-8"
    try:
        return payload.decode(charset, errors="replace").strip()
    except LookupError:
        return payload.decode("utf-8", errors="replace").strip()


def _extract_body(msg: Message) -> tuple[str, str]:
    """
    Return (text, content_kind) where content_kind is 'plain' or 'html'.
    Prefer text/plain; fall back to text/html.
    """
    if not msg.is_multipart():
        ctype = (msg.get_content_type() or "").lower()
        if ctype == "text/html":
            return _strip_html(_decode_text(msg)), "html"
        return _decode_text(msg), "plain"

    plain: list[str] = []
    html: list[str] = []
    for part in msg.walk():
        if part.is_multipart():
            continue
        disp = (part.get("Content-Disposition") or "").lower()
        if "attachment" in disp:
            continue
        ctype = (part.get_content_type() or "").lower()
        if ctype == "text/plain":
            t = _decode_text(part)
            if t:
                plain.append(t)
        elif ctype == "text/html":
            t = _decode_text(part)
            if t:
                html.append(t)

    if plain:
        return "\n\n".join(plain).strip(), "plain"
    if html:
        return _strip_html("\n\n".join(html)), "html"
    return "", "plain"


def _safe_dt(value: str | None) -> str:
    if not value:
        return ""
    try:
        dt = parsedate_to_datetime(value)
        if isinstance(dt, datetime):
            return dt.isoformat()
    except Exception:
        return ""
    return ""


@dataclass(frozen=True)
class EmailConfig:
    host: str
    user: str
    password: str
    port: int = 993
    mailbox: str = "INBOX"
    scope: str = "starred"  # starred | sent | all
    limit: int = 200


class EmailSource:
    target: str = "knowledge"

    def __init__(
        self,
        *,
        config: EmailConfig,
        chunk_size: int = 512,
        chunk_overlap: int = 64,
        user_id: str = "user",
    ) -> None:
        self.config = config
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.user_id = user_id

    @staticmethod
    def from_env(*, limit: int = 200) -> EmailConfig:
        host = os.getenv("ZEUS_EMAIL_HOST", "").strip()
        user = os.getenv("ZEUS_EMAIL_USER", "").strip()
        password = os.getenv("ZEUS_EMAIL_PASSWORD", "")
        port = int(os.getenv("ZEUS_EMAIL_PORT", "993"))
        mailbox = os.getenv("ZEUS_EMAIL_MAILBOX", "INBOX")
        scope = os.getenv("ZEUS_EMAIL_SCOPE", "starred").strip().lower()
        if not host or not user or not password:
            raise ValueError("ZEUS_EMAIL_HOST/USER/PASSWORD must be set for email ingest")
        return EmailConfig(
            host=host,
            user=user,
            password=password,
            port=port,
            mailbox=mailbox,
            scope=scope,
            limit=int(limit),
        )

    def _imap_query(self) -> str:
        scope = (self.config.scope or "starred").lower()
        if scope == "all":
            return "ALL"
        if scope == "sent":
            # Sent mailbox varies by provider; users can set ZEUS_EMAIL_MAILBOX to Sent.
            return "ALL"
        # default: flagged/starred
        return "FLAGGED"

    async def chunks(self) -> AsyncIterator[Chunk]:
        cfg = self.config
        ctx = ssl.create_default_context()
        imap = imaplib.IMAP4_SSL(cfg.host, cfg.port, ssl_context=ctx)
        try:
            imap.login(cfg.user, cfg.password)
            imap.select(cfg.mailbox)

            query = self._imap_query()
            status, data = imap.search(None, query)
            if status != "OK" or not data or not data[0]:
                return

            ids = data[0].split()
            # newest-first, bounded
            ids = list(reversed(ids))[: max(int(cfg.limit), 1)]

            for msg_id in ids:
                status, msg_data = imap.fetch(msg_id, "(RFC822)")
                if status != "OK" or not msg_data:
                    continue
                raw = msg_data[0][1]
                if not isinstance(raw, (bytes, bytearray)):
                    continue

                msg = message_from_bytes(raw)
                subject = str(msg.get("Subject") or "").strip()
                sender = str(msg.get("From") or "").strip()
                date_hdr = str(msg.get("Date") or "").strip()
                date_iso = _safe_dt(date_hdr)
                message_id = str(msg.get("Message-ID") or "").strip()
                in_reply_to = str(msg.get("In-Reply-To") or "").strip()

                body, body_kind = _extract_body(msg)
                if not body:
                    continue

                header = "\n".join(
                    x
                    for x in [
                        f"Subject: {subject}" if subject else "",
                        f"From: {sender}" if sender else "",
                        f"Date: {date_iso}" if date_iso else "",
                        f"Message-ID: {message_id}" if message_id else "",
                        f"In-Reply-To: {in_reply_to}" if in_reply_to else "",
                    ]
                    if x
                )

                doc = f"{header}\n\n{body}".strip()
                identifier = message_id or msg_id.decode("utf-8", errors="replace")

                for piece in chunk_text(doc, self.chunk_size, self.chunk_overlap):
                    yield Chunk(
                        text=piece,
                        source=f"email:{identifier}",
                        metadata={
                            "type": "email",
                            "subject": subject,
                            "from": sender,
                            "date": date_iso,
                            "body_kind": body_kind,
                            "mailbox": cfg.mailbox,
                            "scope": cfg.scope,
                        },
                        user_id=self.user_id,
                    )
        finally:
            try:
                imap.logout()
            except Exception:
                try:
                    imap.shutdown()
                except Exception:
                    pass

