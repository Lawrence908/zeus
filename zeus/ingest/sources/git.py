# zeus/ingest/sources/git.py — Git history ingest source (Sprint 10b)
# Reads git log from a local repository and yields one chunk per commit.
# Filters to commits by the configured author email to keep only your work.
# Uses subprocess (git CLI) to avoid the gitpython dependency where possible,
# but falls back to gitpython if installed.
import logging
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import AsyncIterator

from zeus.ingest.types import Chunk

logger = logging.getLogger("iris.git")

_GIT_LOG_FORMAT = "%H\x1f%ae\x1f%ai\x1f%s\x1f%an"
_RECORD_SEP = "\x1e"  # ASCII record separator between commits
_FIELD_SEP = "\x1f"   # ASCII unit separator between fields


def _run_git(repo_path: Path, args: list[str]) -> str:
    """Run a git command and return stdout. Raises on failure."""
    result = subprocess.run(
        ["git", *args],
        cwd=str(repo_path),
        capture_output=True,
        text=True,
        timeout=60,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {result.stderr.strip()}")
    return result.stdout


def _changed_files(repo_path: Path, commit_hash: str) -> str:
    """Return a space-joined list of files changed in a commit."""
    try:
        out = _run_git(repo_path, ["diff-tree", "--no-commit-id", "-r", "--name-only", commit_hash])
        files = [f.strip() for f in out.strip().splitlines() if f.strip()]
        return ", ".join(files[:10])  # cap at 10 to keep chunks lean
    except Exception:
        return ""


class GitSource:
    """
    Ingest git commit history from a local repository.

    Env vars:
      GIT_AUTHOR_EMAIL  — only ingest commits from this address
      ZEUS_REPO_PATH    — path to the repo (default: current directory)

    Config keys: repo_path, author_email, max_commits
    """

    target: str = "knowledge"

    def __init__(
        self,
        repo_path: str | Path | None = None,
        author_email: str | None = None,
        max_commits: int = 500,
        chunk_size: int = 512,
        chunk_overlap: int = 64,
        user_id: str = "user",
    ) -> None:
        self.repo_path = Path(repo_path or os.getenv("ZEUS_REPO_PATH", ".")).resolve()
        self.author_email = author_email or os.getenv("GIT_AUTHOR_EMAIL", "")
        self.max_commits = max_commits
        self.user_id = user_id
        # chunk_size/overlap unused (commits are naturally small), kept for interface parity

    def _fetch_commits(self) -> list[dict]:
        """Run git log and parse into commit dicts."""
        if not (self.repo_path / ".git").is_dir():
            logger.warning("git: no .git directory at %s", self.repo_path)
            return []

        log_args = [
            "log",
            "--all",
            f"--format={_GIT_LOG_FORMAT}{_RECORD_SEP}",
            f"--max-count={self.max_commits}",
        ]

        try:
            raw = _run_git(self.repo_path, log_args)
        except RuntimeError as exc:
            logger.error("git: log failed — %s", exc)
            return []

        commits = []
        for record in raw.split(_RECORD_SEP):
            record = record.strip()
            if not record:
                continue
            parts = record.split(_FIELD_SEP)
            if len(parts) < 5:
                continue
            commit_hash, author_email, date_str, subject, author_name = parts[:5]
            commits.append({
                "hash": commit_hash.strip(),
                "email": author_email.strip(),
                "date": date_str.strip(),
                "subject": subject.strip(),
                "author": author_name.strip(),
            })
        return commits

    async def chunks(self) -> AsyncIterator[Chunk]:
        commits = self._fetch_commits()
        if not commits:
            return

        repo_name = self.repo_path.name

        for commit in commits:
            # Filter by author email if set
            if self.author_email and commit["email"].lower() != self.author_email.lower():
                continue

            changed = _changed_files(self.repo_path, commit["hash"])

            date_label = commit["date"][:10]  # YYYY-MM-DD
            text_parts = [f"[{date_label}] git commit: {commit['subject']}"]
            if changed:
                text_parts.append(f"(files: {changed})")
            text_parts.append(f"(repo: {repo_name}, author: {commit['author']})")
            text = " ".join(text_parts)

            yield Chunk(
                text=text,
                source=f"git:{repo_name}:{commit['hash'][:8]}",
                metadata={
                    "repo": repo_name,
                    "repo_path": str(self.repo_path),
                    "commit_hash": commit["hash"],
                    "author": commit["author"],
                    "author_email": commit["email"],
                    "date": commit["date"],
                    "subject": commit["subject"],
                    "changed_files": changed,
                    "type": "git_commit",
                },
                user_id=self.user_id,
            )
