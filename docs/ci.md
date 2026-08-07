# CI / CD

Zeus runs a GitHub Actions pipeline on every push and on PRs into `main`.
Definition: [`.github/workflows/ci.yml`](../.github/workflows/ci.yml).

## Jobs

| Job | What it does | Fails the build when |
|-----|--------------|----------------------|
| **backend** | `ruff check .` then `pytest -q` (with coverage) on Python 3.11 | Lint violation of an enforced rule, or any test fails |
| **frontend** | `npm ci` + `npm run build` for `zeus/frontend` (React SPA) and `zeus-os` (SvelteKit, also `npm run check`) | A frontend fails to type-check or build |
| **docker** | Builds `zeus/core/Dockerfile` (context = repo root), no push | The runtime image fails to build |

Jobs are independent (no `needs:`) and run in parallel. The `docker` job installs
the full runtime (`libzim-dev`, torch/FlagEmbedding, etc.), so it doubles as the
end-to-end check that heavy/optional deps still install.

## The test suite is mock-based

All 235 tests use `httpx.MockTransport` and `monkeypatch`: **no live Qdrant,
Ollama, or Postgres is required.** That is why CI needs no service containers and
runs anywhere. Keep it that way: a new test that needs a real service should mock
it or be gated behind a `pytest.mark.skipif` probe (see the qdrant-gated skip in
`tests/retrieval_eval.py` for the pattern).

## Run the gate locally

Reproduce the `backend` job exactly before pushing:

```bash
scripts/test.sh              # ruff check . + pytest -q
scripts/test.sh -k epstein   # extra args forward to pytest
```

Frontends:

```bash
cd zeus/frontend && npm ci && npm run build
cd zeus-os       && npm ci && npm run check && npm run build
```

Docker:

```bash
docker build -f zeus/core/Dockerfile -t zeus-core:ci .
```

## Coverage is report-only

`pytest.ini` sets `--cov=zeus --cov-report=term-missing --cov-report=xml`. CI
prints the summary and uploads `coverage.xml` as an artifact but **does not fail
on a threshold** (current baseline ≈21%). To ratchet later, add
`--cov-fail-under=<N>` to `pytest.ini` once a target is agreed.

## Linting: check-only, with a burn-down list

Ruff is configured in [`pyproject.toml`](../pyproject.toml) with `select =
["E","F","I","UP","B"]`. It is **check-only**: CI never reformats the tree.

Because the codebase predates linting, the rule codes that already had violations
are quarantined in `[tool.ruff.lint] ignore` with `# TODO: burn down` comments.
Everything else is enforced now, so new violations of un-ignored rules (e.g.
`F821` undefined-name, which caught a real missing-import bug when this was set
up) fail CI.

To pay down the debt: pick one ignored code, remove it from the `ignore` list,
run `ruff check --fix .` (or fix by hand for non-autofixable rules), and commit.
Do them one code at a time to keep diffs reviewable.

## Deferred / possible follow-ups

- `.pre-commit-config.yaml` running ruff on commit (kept out of the initial setup
  to stay focused).
- A coverage floor once the baseline is raised.
- Burning down the ruff `ignore` list (import sorting `I001` and the `UP*`
  modernizations are the largest, mechanical wins).
