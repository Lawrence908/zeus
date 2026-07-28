# tests/test_aletheia.py — Aletheia documentation-drift investigator.
#
# Covers the pieces that carry risk: exclusion enforcement (a miss leaks the
# personal-data layer), reference classification, independent verification, the
# stable finding identity that the weekly digest depends on, fail-open sweep,
# and the digest's new/carried/resolved partition.
import asyncio
import os

from zeus.orchestration.aletheia import config, verifier
from zeus.orchestration.aletheia.digest import generate_digest, prev_iso_week
from zeus.orchestration.aletheia.extract import extract_references
from zeus.orchestration.aletheia.models import (
    Finding,
    FindingStatus,
    Reference,
    ReferenceKind,
    RunMode,
    iso_week,
)
from zeus.orchestration.aletheia.store import AletheiaStore
from zeus.orchestration.aletheia.sweep import discover_docs, run_sweep
from zeus.orchestration.aletheia.worker import parse_findings


# --- config: exclusion enforcement ------------------------------------------


def test_exclusion_globs_cover_personal_data_layer():
    for p in [".env", ".env.local", "zeus/.env", "zeus/data/context_pack.md",
              "zeus/data/sessions.db", "a/b.sqlite3", ".ssh/id_rsa", "home/.ssh/k"]:
        assert config.path_excluded(p), p
    # Ordinary source and docs are readable.
    for p in ["zeus/memory/store.py", "zeus/safety/policies/swarm.yaml",
              "README.md", "CLAUDE.md"]:
        assert not config.path_excluded(p), p


def test_disallowed_tool_specs_enforce_exclusions():
    specs = config.disallowed_tool_specs()
    # The enforcement is what makes the exclusion real, not decorative.
    assert any(s.startswith("Read(") and ".env" in s for s in specs)
    assert any("zeus/data/**" in s for s in specs)
    # Every exclusion glob is enforced across Read/Grep/Glob.
    assert len(specs) == len(config.exclusion_globs()) * 3


def test_observe_roots_rejects_unsafe(monkeypatch):
    monkeypatch.setenv("ZEUS_ALETHEIA_OBSERVE_ROOTS", "/\n~")
    assert config.observe_roots() == []  # never the whole fs or home


def test_is_doc_matches_root_and_nested():
    assert config.is_doc("README.md")           # root-level (fnmatch /-quirk guard)
    assert config.is_doc("zeus/docs/architecture.md")
    assert not config.is_doc("zeus/core/query.py")


# --- extractor ---------------------------------------------------------------


def test_extract_classifies_reference_kinds():
    text = (
        "Path `zeus/memory/store.py`, dir `zeus/safety/policies/`, "
        "env `ZEUS_KNOWLEDGE_HYBRID`, route `POST /swarm/runs`, "
        "symbol `MemoryStore.get_profile_facts`, cmd `python -m zeus.bench`."
    )
    got = {(r.reference.kind, r.reference.target) for r in extract_references(text)}
    assert (ReferenceKind.PATH, "zeus/memory/store.py") in got
    assert (ReferenceKind.PATH, "zeus/safety/policies/") in got
    assert (ReferenceKind.ENV_VAR, "ZEUS_KNOWLEDGE_HYBRID") in got
    assert (ReferenceKind.ENDPOINT, "POST /swarm/runs") in got
    assert (ReferenceKind.SYMBOL, "MemoryStore.get_profile_facts") in got
    assert (ReferenceKind.COMMAND, "python -m zeus.bench") in got


def test_extract_skips_fenced_blocks_and_prose():
    text = "Real `env_VAR` no.\n```\nfake `zeus/inside/fence.py`\n```\nplain word `hello world`\n"
    targets = {r.reference.target for r in extract_references(text)}
    assert "zeus/inside/fence.py" not in targets   # inside a fence
    assert "hello world" not in targets            # unclassifiable prose


# --- verifier (against a synthetic tree) -------------------------------------


def _tree(tmp_path):
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "real.py").write_text(
        "def existing_fn():\n    pass\n\nMY_REAL_VAR = 1\n"
    )
    (tmp_path / "pkg" / "moved.py").write_text("class Widget:\n    pass\n")
    (tmp_path / "doc.md").write_text("stub\n")
    return tmp_path


def test_verifier_resolves_paths_symbols_env(monkeypatch, tmp_path):
    _tree(tmp_path)
    monkeypatch.setenv("ZEUS_ALETHEIA_OBSERVE_ROOTS", str(tmp_path))

    assert verifier.resolve(Reference(kind=ReferenceKind.PATH, target="pkg/real.py")).status == FindingStatus.OK
    assert verifier.resolve(Reference(kind=ReferenceKind.PATH, target="pkg/gone.py")).status == FindingStatus.MISSING
    # moved: documented at old path, class lives elsewhere
    moved = verifier.resolve(Reference(kind=ReferenceKind.SYMBOL, target="pkg/old.py::Widget"))
    assert moved.status == FindingStatus.MOVED
    assert "moved.py" in moved.evidence
    assert verifier.resolve(Reference(kind=ReferenceKind.ENV_VAR, target="MY_REAL_VAR")).status == FindingStatus.OK
    assert verifier.resolve(Reference(kind=ReferenceKind.ENV_VAR, target="NOPE_VAR_X")).status == FindingStatus.MISSING


def test_verifier_never_reads_excluded(monkeypatch, tmp_path):
    monkeypatch.setenv("ZEUS_ALETHEIA_OBSERVE_ROOTS", str(tmp_path))
    (tmp_path / ".env").write_text("SECRET_TOKEN=abc123\n")
    # An env var that exists ONLY in .env must resolve missing, not ok - the
    # scanner must skip the excluded file.
    res = verifier.resolve(Reference(kind=ReferenceKind.ENV_VAR, target="SECRET_TOKEN"))
    assert res.status == FindingStatus.MISSING


def test_verify_finding_drops_on_disagreement(monkeypatch, tmp_path):
    _tree(tmp_path)
    monkeypatch.setenv("ZEUS_ALETHEIA_OBSERVE_ROOTS", str(tmp_path))
    # Worker claims a real path is missing; verifier resolves it -> dropped.
    f = Finding(
        doc_path="doc.md", reference=Reference(kind=ReferenceKind.PATH, target="pkg/real.py"),
        status=FindingStatus.MISSING,
    )
    out = verifier.verify_finding(f)
    assert out.verified is False
    assert out.reportable is False


# --- store: identity, dedup, weekly partition -------------------------------


def _finding(doc, target, status=FindingStatus.MISSING):
    return Finding(
        doc_path=doc, reference=Reference(kind=ReferenceKind.PATH, target=target),
        status=status, verified=True,
    )


def test_store_identity_is_stable():
    a = _finding("d.md", "x/y.py")
    b = _finding("d.md", "x/y.py")
    assert a.identity() == b.identity()
    assert _finding("d.md", "x/z.py").identity() != a.identity()


def test_store_persist_dedup_and_weeks(tmp_path):
    store = AletheiaStore(str(tmp_path / "a.db"))

    async def scenario():
        from zeus.orchestration.aletheia.models import AletheiaRun
        run = AletheiaRun(id="r1", mode=RunMode.FULL, iso_week="2026-W10")
        await store.create_run(run)
        f = _finding("d.md", "gone.py")
        await store.add_finding("r1", "2026-W10", f)
        await store.add_finding("r1", "2026-W10", f)  # same identity -> replace
        wk = await store.findings_for_week("2026-W10")
        assert len(wk) == 1
        ids = await store.identities_for_week("2026-W10")
        assert ids == {f.identity()}
        assert await store.identities_for_week("2026-W09") == set()

    asyncio.run(scenario())


# --- sweep: mechanical, fail-open -------------------------------------------


def test_sweep_reports_real_drift(monkeypatch, tmp_path):
    _tree(tmp_path)
    (tmp_path / "doc.md").write_text(
        "Good: `pkg/real.py` env `MY_REAL_VAR`.\n"
        "Drift: `pkg/gone.py` env `MY_FAKE_VAR`.\n"
    )
    monkeypatch.setenv("ZEUS_ALETHEIA_OBSERVE_ROOTS", str(tmp_path))
    monkeypatch.setenv("ZEUS_ALETHEIA_WORKER_ENABLED", "0")

    async def scenario():
        store = AletheiaStore(str(tmp_path / "a.db"))
        rep = await run_sweep(store, mode=RunMode.FULL)
        assert rep.run.status.value == "completed"
        assert rep.run.docs_total >= 1
        targets = {f.reference.target for f in rep.reportable}
        assert "pkg/gone.py" in targets
        assert "MY_FAKE_VAR" in targets
        assert "pkg/real.py" not in targets   # resolves OK, not reported

    asyncio.run(scenario())


def test_discover_incremental_scopes_to_changed(monkeypatch, tmp_path):
    _tree(tmp_path)
    (tmp_path / "a.md").write_text("mentions `real.py` somewhere\n")
    (tmp_path / "b.md").write_text("unrelated content\n")
    monkeypatch.setenv("ZEUS_ALETHEIA_OBSERVE_ROOTS", str(tmp_path))
    docs = discover_docs(RunMode.INCREMENTAL, ["pkg/real.py"])
    rels = {rel for _ap, rel, _root in docs}
    assert "a.md" in rels          # references the changed file
    assert "b.md" not in rels      # unrelated


# --- digest: new / carried / resolved ---------------------------------------


def test_prev_iso_week():
    assert prev_iso_week("2026-W10") == "2026-W09"


def test_digest_partitions_new_carried_resolved(monkeypatch, tmp_path):
    monkeypatch.setenv("ZEUS_ALETHEIA_DIGEST_DIR", str(tmp_path / "digests"))
    store = AletheiaStore(str(tmp_path / "a.db"))
    prev, cur = "2026-W20", "2026-W21"

    async def scenario():
        from zeus.orchestration.aletheia.models import AletheiaRun
        for wk in (prev, cur):
            await store.create_run(AletheiaRun(id=f"run-{wk}", mode=RunMode.FULL, iso_week=wk))
        # last week: carried + fixed ; this week: carried + new
        await store.add_finding("run-2026-W20", prev, _finding("d.md", "carried.py"))
        await store.add_finding("run-2026-W20", prev, _finding("d.md", "fixed.py"))
        await store.add_finding("run-2026-W21", cur, _finding("d.md", "carried.py"))
        await store.add_finding("run-2026-W21", cur, _finding("d.md", "new.py"))

        res = await generate_digest(store, week=cur, ingest=False)
        assert res.total == 2
        assert res.new == 1        # new.py
        assert res.carried == 1    # carried.py
        assert res.resolved == 1   # fixed.py gone this week
        assert os.path.exists(res.path)
        assert "Resolved since last week" in res.markdown

    asyncio.run(scenario())


# --- worker output parsing ---------------------------------------------------


def test_parse_findings_valid_and_malformed():
    good = (
        'noise before ['
        '{"doc_line": 5, "claim": "c", "reference": {"kind": "path", "target": "x/y.py"}, '
        '"status": "missing", "evidence": "e", "confidence": 0.8},'
        '{"reference": {"kind": "path", "target": "z.py"}, "status": "ok"},'  # ok -> skipped
        '{"garbage": true}'
        '] after'
    )
    out = parse_findings(good, "doc.md")
    assert len(out) == 1
    assert out[0].reference.target == "x/y.py"
    assert out[0].verified is False   # must pass the verifier before reporting
    assert parse_findings("no json here", "doc.md") == []
