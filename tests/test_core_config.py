# tests/test_core_config.py
"""Resolution order for the zeus-core base URL.

The failure mode this guards is quiet: a wrong port surfaces as
connection-refused inside a tool, which reads as a broken feature rather than
a misconfigured address.
"""

from __future__ import annotations

import pytest

from zeus.core.config import DEFAULT_PUBLISHED_PORT, core_base_url


@pytest.fixture(autouse=True)
def _clear_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ZEUS_CORE_URL", raising=False)
    monkeypatch.delenv("ZEUS_CORE_PORT", raising=False)


def test_falls_back_to_the_compose_default_port() -> None:
    assert core_base_url() == f"http://127.0.0.1:{DEFAULT_PUBLISHED_PORT}"


def test_derives_from_published_port(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ZEUS_CORE_PORT", "8102")
    assert core_base_url() == "http://127.0.0.1:8102"


def test_explicit_url_wins_and_loses_trailing_slash(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ZEUS_CORE_PORT", "8102")
    monkeypatch.setenv("ZEUS_CORE_URL", "http://zeus-core:8000/")
    assert core_base_url() == "http://zeus-core:8000"


@pytest.mark.parametrize("blank", ["", "   "])
def test_blank_url_falls_through_to_port(
    monkeypatch: pytest.MonkeyPatch, blank: str
) -> None:
    # An env var set to empty string is a common compose/.env accident; it must
    # not resolve to "http://" with no host.
    monkeypatch.setenv("ZEUS_CORE_URL", blank)
    monkeypatch.setenv("ZEUS_CORE_PORT", "8102")
    assert core_base_url() == "http://127.0.0.1:8102"
