# tests/test_swarm_config.py — repo allowlist + self-edit path denylist
import os

from zeus.orchestration.swarm import config


def test_default_allowlist_is_zeus_only():
    # Default ships with just ~/zeus; ~ itself is not allowed.
    allow = config.repo_allowlist()
    assert allow == [os.path.realpath(os.path.expanduser("~/zeus"))]
    assert config.repo_allowed("~/zeus")
    assert not config.repo_allowed("~")
    assert not config.repo_allowed("/etc")


def test_allowlist_env_override(monkeypatch, tmp_path):
    monkeypatch.setenv("ZEUS_SWARM_REPO_ALLOWLIST", f"{tmp_path},/nonexistent/repo")
    assert config.repo_allowed(str(tmp_path))
    assert not config.repo_allowed("~/zeus")


def test_denylist_blocks_self_editing_and_secrets():
    # A worker must not be able to edit the machinery supervising it.
    assert config.path_denied("zeus/safety/policies/standard.yaml")
    assert config.path_denied("zeus/orchestration/swarm/coordinator.py")
    assert config.path_denied("zeus/orchestration/runtime.py")
    assert config.path_denied(".env")
    assert config.path_denied("services/foo/.env.prod")
    # Ordinary source is fine.
    assert not config.path_denied("zeus/core/query.py")
    assert not config.path_denied("zeus-os/src/lib/apps/Chat.svelte")


def test_denied_paths_filters():
    changed = ["zeus/core/query.py", "zeus/orchestration/bus.py", "README.md"]
    assert config.denied_paths(changed) == ["zeus/orchestration/bus.py"]
