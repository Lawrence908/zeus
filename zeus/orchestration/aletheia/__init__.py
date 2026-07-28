# zeus/orchestration/aletheia/__init__.py
"""Aletheia: read-only documentation-drift investigator.

Aletheia walks documentation, resolves every concrete reference a doc makes to
the codebase, and reports what no longer holds. It never edits anything in v1.

Two config lists that must never be conflated (see config.py):

- ``ZEUS_ALETHEIA_OBSERVE_ROOTS`` - paths Aletheia may *read* (wide, server-wide).
- ``ZEUS_SWARM_REPO_ALLOWLIST``  - repos the coding swarm may *write* (narrow).

Design brief: docs/aletheia-plan.md. Aletheia reuses the swarm store/worker/
notifier *patterns* and the Kronos scheduler, but not the write-centric swarm
coordinator: it produces structured findings, not diffs.
"""
