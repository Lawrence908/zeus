# tests/test_newsletter.py — Newsletter digest system tests
import asyncio
import json
import os
from email.message import EmailMessage
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from zeus.ingest.sources.newsletter import (
    NewsletterConfig,
    NewsletterSource,
    RawNewsletter,
)


# ---------------------------------------------------------------------------
# NewsletterConfig.from_env — validation
# ---------------------------------------------------------------------------

_BASE_ENV = {
    "NEWSLETTER_IMAP_USER": "test@example.com",
    "NEWSLETTER_IMAP_PASS": "secret",
    "NEWSLETTER_SOURCES": '{"tldr": "dan@tldrnewsletter.com"}',
}


def _env(**overrides: str) -> dict[str, str]:
    merged = {**_BASE_ENV, **overrides}
    return merged


class TestNewsletterConfigFromEnv:
    def test_happy_path(self):
        with patch.dict(os.environ, _env(), clear=False):
            cfg = NewsletterSource.from_env()
        assert cfg.imap_host == "imap.gmail.com"
        assert cfg.imap_user == "test@example.com"
        assert cfg.imap_port == 993
        assert cfg.mailbox == "INBOX"
        assert cfg.sources == {"tldr": "dan@tldrnewsletter.com"}

    def test_custom_host_and_port(self):
        with patch.dict(os.environ, _env(
            NEWSLETTER_IMAP_HOST="mail.custom.io",
            NEWSLETTER_IMAP_PORT="465",
            NEWSLETTER_MAILBOX="Newsletters",
        ), clear=False):
            cfg = NewsletterSource.from_env()
        assert cfg.imap_host == "mail.custom.io"
        assert cfg.imap_port == 465
        assert cfg.mailbox == "Newsletters"

    def test_missing_user_raises(self):
        env = _env()
        del env["NEWSLETTER_IMAP_USER"]
        with patch.dict(os.environ, env, clear=False):
            os.environ.pop("NEWSLETTER_IMAP_USER", None)
            with pytest.raises(ValueError, match="NEWSLETTER_IMAP_USER"):
                NewsletterSource.from_env()

    def test_missing_pass_raises(self):
        env = _env()
        del env["NEWSLETTER_IMAP_PASS"]
        with patch.dict(os.environ, env, clear=False):
            os.environ.pop("NEWSLETTER_IMAP_PASS", None)
            with pytest.raises(ValueError, match="NEWSLETTER_IMAP_PASS"):
                NewsletterSource.from_env()

    def test_invalid_json_raises(self):
        with patch.dict(os.environ, _env(NEWSLETTER_SOURCES="not json"), clear=False):
            with pytest.raises(ValueError, match="valid JSON"):
                NewsletterSource.from_env()

    def test_sources_not_dict_raises(self):
        with patch.dict(os.environ, _env(NEWSLETTER_SOURCES='["a","b"]'), clear=False):
            with pytest.raises(ValueError, match="JSON object"):
                NewsletterSource.from_env()

    def test_empty_sources_raises(self):
        with patch.dict(os.environ, _env(NEWSLETTER_SOURCES="{}"), clear=False):
            with pytest.raises(ValueError, match="at least one entry"):
                NewsletterSource.from_env()

    def test_source_value_empty_string_raises(self):
        with patch.dict(os.environ, _env(
            NEWSLETTER_SOURCES='{"bad": "  "}'
        ), clear=False):
            with pytest.raises(ValueError, match="non-empty string"):
                NewsletterSource.from_env()

    def test_multiple_sources(self):
        sources = '{"tldr": "dan@tldrnewsletter.com", "morning": "hello@morning.com"}'
        with patch.dict(os.environ, _env(NEWSLETTER_SOURCES=sources), clear=False):
            cfg = NewsletterSource.from_env()
        assert len(cfg.sources) == 2
        assert cfg.sources["morning"] == "hello@morning.com"

    def test_since_days_and_limit_passthrough(self):
        with patch.dict(os.environ, _env(), clear=False):
            cfg = NewsletterSource.from_env(limit=5, since_days=3)
        assert cfg.limit == 5
        assert cfg.since_days == 3


# ---------------------------------------------------------------------------
# NewsletterSource._classify_sender
# ---------------------------------------------------------------------------

class TestClassifySender:
    def _source(self) -> NewsletterSource:
        cfg = NewsletterConfig(
            imap_host="host",
            imap_user="u",
            imap_pass="p",
            sources={"tldr": "dan@tldrnewsletter.com", "morning": "hello@morning.com"},
        )
        return NewsletterSource(config=cfg)

    def test_exact_match(self):
        src = self._source()
        assert src._classify_sender("dan@tldrnewsletter.com") == "tldr"

    def test_display_name_match(self):
        src = self._source()
        assert src._classify_sender("TLDR <dan@tldrnewsletter.com>") == "tldr"

    def test_case_insensitive(self):
        src = self._source()
        assert src._classify_sender("DAN@TLDRNEWSLETTER.COM") == "tldr"

    def test_no_match(self):
        src = self._source()
        assert src._classify_sender("unknown@random.com") is None


# ---------------------------------------------------------------------------
# NewsletterSource.fetch_newsletters_raw — with mocked IMAP
# ---------------------------------------------------------------------------

def _make_email(
    subject: str = "Test Subject",
    sender: str = "dan@tldrnewsletter.com",
    body: str = "Hello newsletter content",
    date: str = "Mon, 07 Apr 2026 10:00:00 +0000",
    message_id: str = "<test-001@example.com>",
) -> bytes:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["Date"] = date
    msg["Message-ID"] = message_id
    msg.set_content(body)
    return msg.as_bytes()


class TestFetchNewslettersRaw:
    def _source(self) -> NewsletterSource:
        cfg = NewsletterConfig(
            imap_host="imap.test.com",
            imap_user="user@test.com",
            imap_pass="pass",
            sources={"tldr": "dan@tldrnewsletter.com"},
            limit=5,
            since_days=7,
        )
        return NewsletterSource(config=cfg)

    def test_fetches_and_returns_raw_newsletters(self):
        mock_imap = MagicMock()
        mock_imap.search.return_value = ("OK", [b"1 2"])
        mock_imap.fetch.side_effect = [
            ("OK", [(b"1", _make_email(subject="Issue 1", message_id="<1@x>"))]),
            ("OK", [(b"2", _make_email(subject="Issue 2", message_id="<2@x>"))]),
        ]

        src = self._source()
        with patch.object(src, "_connect", return_value=mock_imap):
            results = src.fetch_newsletters_raw(newsletter_type="tldr", num_recent=5)

        assert len(results) == 2
        assert results[0].newsletter_type == "tldr"
        assert results[0].subject in ("Issue 1", "Issue 2")
        mock_imap.logout.assert_called_once()

    def test_deduplicates_by_message_id(self):
        same_email = _make_email(message_id="<dup@x>")
        mock_imap = MagicMock()
        mock_imap.search.return_value = ("OK", [b"1 2"])
        mock_imap.fetch.side_effect = [
            ("OK", [(b"1", same_email)]),
            ("OK", [(b"2", same_email)]),
        ]

        src = self._source()
        with patch.object(src, "_connect", return_value=mock_imap):
            results = src.fetch_newsletters_raw(newsletter_type="tldr", num_recent=10)

        assert len(results) == 1

    def test_unknown_type_returns_empty(self):
        src = self._source()
        with patch.object(src, "_connect") as mock_conn:
            results = src.fetch_newsletters_raw(newsletter_type="nonexistent")
        assert results == []
        mock_conn.assert_not_called()

    def test_num_recent_limits_results(self):
        mock_imap = MagicMock()
        mock_imap.search.return_value = ("OK", [b"1 2 3"])
        mock_imap.fetch.side_effect = [
            ("OK", [(b"3", _make_email(subject="Issue 3", message_id="<3@x>", date="Wed, 09 Apr 2026 10:00:00 +0000"))]),
            ("OK", [(b"2", _make_email(subject="Issue 2", message_id="<2@x>", date="Tue, 08 Apr 2026 10:00:00 +0000"))]),
            ("OK", [(b"1", _make_email(subject="Issue 1", message_id="<1@x>", date="Mon, 07 Apr 2026 10:00:00 +0000"))]),
        ]

        src = self._source()
        with patch.object(src, "_connect", return_value=mock_imap):
            results = src.fetch_newsletters_raw(newsletter_type="tldr", num_recent=1)

        assert len(results) == 1

    def test_empty_search_returns_empty(self):
        mock_imap = MagicMock()
        mock_imap.search.return_value = ("OK", [b""])

        src = self._source()
        with patch.object(src, "_connect", return_value=mock_imap):
            results = src.fetch_newsletters_raw(newsletter_type="tldr")

        assert results == []


# ---------------------------------------------------------------------------
# NewsletterSource.chunks — async iterator
# ---------------------------------------------------------------------------

class TestChunks:
    def test_yields_chunks_from_emails(self):
        mock_imap = MagicMock()
        mock_imap.search.return_value = ("OK", [b"1"])
        mock_imap.fetch.return_value = (
            "OK",
            [(b"1", _make_email(body="A " * 300))],  # long enough to chunk
        )

        cfg = NewsletterConfig(
            imap_host="h", imap_user="u", imap_pass="p",
            sources={"tldr": "dan@tldrnewsletter.com"},
        )
        src = NewsletterSource(config=cfg, chunk_size=128, chunk_overlap=16)

        async def _run() -> list:
            chunks = []
            with patch.object(src, "_connect", return_value=mock_imap):
                async for c in src.chunks():
                    chunks.append(c)
            return chunks

        chunks = asyncio.run(_run())
        assert len(chunks) >= 2
        assert chunks[0].source == "newsletter:tldr"
        assert chunks[0].metadata["type"] == "newsletter"
        assert chunks[0].metadata["newsletter_type"] == "tldr"


# ---------------------------------------------------------------------------
# Manifest helpers (core/newsletter.py)
# ---------------------------------------------------------------------------

from zeus.core.newsletter import (
    _append_digest,
    _load_manifest,
    _save_manifest,
    _SAFE_FILENAME_RE,
)


class TestManifestHelpers:
    def test_load_missing_file_returns_empty(self, tmp_path: Path):
        with patch("zeus.core.newsletter._MANIFEST_PATH", tmp_path / "nope.json"):
            manifest = _load_manifest()
        assert manifest == {"digests": []}

    def test_load_corrupt_file_returns_empty(self, tmp_path: Path):
        bad = tmp_path / "bad.json"
        bad.write_text("not json!")
        with patch("zeus.core.newsletter._MANIFEST_PATH", bad):
            manifest = _load_manifest()
        assert manifest == {"digests": []}

    def test_roundtrip_save_and_load(self, tmp_path: Path):
        mp = tmp_path / "manifest.json"
        md = tmp_path
        with patch("zeus.core.newsletter._MANIFEST_PATH", mp), \
             patch("zeus.core.newsletter._MANIFEST_DIR", md):
            _save_manifest({"digests": [{"id": "1"}]})
            manifest = _load_manifest()
        assert len(manifest["digests"]) == 1
        assert manifest["digests"][0]["id"] == "1"

    def test_append_digest_inserts_at_front(self):
        manifest = {"digests": [{"id": "old"}]}
        _append_digest(manifest, {"id": "new"})
        assert manifest["digests"][0]["id"] == "new"
        assert manifest["digests"][1]["id"] == "old"

    def test_append_digest_caps_at_50(self):
        manifest = {"digests": [{"id": str(i)} for i in range(50)]}
        _append_digest(manifest, {"id": "newest"})
        assert len(manifest["digests"]) == 50
        assert manifest["digests"][0]["id"] == "newest"


# ---------------------------------------------------------------------------
# Filename validation regex
# ---------------------------------------------------------------------------

class TestFilenameValidation:
    @pytest.mark.parametrize("name", [
        "newsletter_20260409_abc12345.wav",
        "test-file_123.wav",
        "a.wav",
    ])
    def test_valid_filenames(self, name: str):
        assert _SAFE_FILENAME_RE.match(name)

    @pytest.mark.parametrize("name", [
        "../etc/passwd",
        "file.mp3",
        "newsletter 20260409.wav",
        "../../secret.wav",
        "",
        "file.wav.exe",
    ])
    def test_invalid_filenames(self, name: str):
        assert not _SAFE_FILENAME_RE.match(name)


# ---------------------------------------------------------------------------
# API endpoints — using FastAPI test client
# ---------------------------------------------------------------------------

class TestNewsletterAPI:
    @pytest.fixture
    def client(self):
        from fastapi.testclient import TestClient
        from zeus.core.newsletter import router
        from fastapi import FastAPI

        app = FastAPI()
        app.include_router(router)
        return TestClient(app)

    def test_list_digests_empty(self, client, tmp_path: Path):
        mp = tmp_path / "manifest.json"
        with patch("zeus.core.newsletter._MANIFEST_PATH", mp):
            resp = client.get("/api/newsletter/digests")
        assert resp.status_code == 200
        assert resp.json()["digests"] == []

    def test_list_digests_returns_entries(self, client, tmp_path: Path):
        mp = tmp_path / "manifest.json"
        entry = {
            "id": "abc", "newsletter_type": "tldr", "date": "2026-04-09",
            "summary": "Test", "bullets": ["one"], "advice": "Do stuff",
            "audio_file": None, "audio_url": None,
            "generated_at": "2026-04-09T00:00:00+00:00",
        }
        mp.write_text(json.dumps({"digests": [entry]}))
        with patch("zeus.core.newsletter._MANIFEST_PATH", mp):
            resp = client.get("/api/newsletter/digests")
        assert resp.status_code == 200
        assert len(resp.json()["digests"]) == 1
        assert resp.json()["digests"][0]["summary"] == "Test"

    def test_audio_rejects_path_traversal(self, client):
        # FastAPI/Starlette normalizes ../../ in path, so test with encoded dots
        resp = client.get("/api/newsletter/audio/..%2F..%2Fetc%2Fpasswd")
        assert resp.status_code in (400, 404)  # rejected either by regex or routing

    def test_audio_404_for_missing_file(self, client, tmp_path: Path):
        with patch("zeus.core.newsletter._AUDIO_DIR", tmp_path):
            resp = client.get("/api/newsletter/audio/nonexistent_file.wav")
        assert resp.status_code == 404

    def test_audio_serves_existing_file(self, client, tmp_path: Path):
        wav = tmp_path / "test_audio.wav"
        wav.write_bytes(b"RIFF fake wav data")
        with patch("zeus.core.newsletter._AUDIO_DIR", tmp_path):
            resp = client.get("/api/newsletter/audio/test_audio.wav")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "audio/wav"

    def test_sources_returns_config(self, client):
        with patch.dict(os.environ, _env(), clear=False):
            resp = client.get("/api/newsletter/sources")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["sources"]) == 1
        assert data["sources"][0]["type"] == "tldr"

    def test_sources_returns_empty_on_missing_config(self, client):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("NEWSLETTER_IMAP_USER", None)
            os.environ.pop("NEWSLETTER_IMAP_PASS", None)
            resp = client.get("/api/newsletter/sources")
        assert resp.status_code == 200
        assert resp.json()["sources"] == []

    def test_digest_post_no_config_returns_503(self, client):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("NEWSLETTER_IMAP_USER", None)
            os.environ.pop("NEWSLETTER_IMAP_PASS", None)
            os.environ.pop("NEWSLETTER_SOURCES", None)
            resp = client.post(
                "/api/newsletter/digest",
                json={"newsletter_type": "all", "num_recent": 1},
            )
        assert resp.status_code == 503

    def test_digest_post_no_emails_returns_404(self, client):
        mock_source = MagicMock()
        mock_source.fetch_newsletters_raw.return_value = []

        with patch.dict(os.environ, _env(), clear=False), \
             patch(
                 "zeus.ingest.sources.newsletter.NewsletterSource",
                 return_value=mock_source,
             ) as mock_cls:
            # The endpoint does `from zeus.ingest.sources.newsletter import NewsletterSource`
            # at call time, so we also need to patch asyncio.to_thread to call our mock
            mock_cls.from_env.return_value = MagicMock()
            with patch("zeus.core.newsletter.asyncio.to_thread", return_value=[]):
                resp = client.post(
                    "/api/newsletter/digest",
                    json={"newsletter_type": "tldr", "num_recent": 1},
                )
        assert resp.status_code == 404

    def test_newsletters_page_serves_html(self, client):
        resp = client.get("/newsletters")
        # Will succeed if newsletters.html exists, 503 if not
        assert resp.status_code in (200, 503)
