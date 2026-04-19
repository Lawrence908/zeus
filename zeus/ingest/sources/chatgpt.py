# zeus/ingest/sources/chatgpt.py — Iris ChatGPT export parser
# Parses ChatGPT data exports (Settings → Export).
# Supports both the legacy single-file format (conversations.json) and the
# newer multi-file export (conversations-000.json, conversations-001.json, …
# plus media directories).  Pass a file or a directory as `path`.
# Only user messages are ingested by default — they contain Chris's actual
# thoughts, preferences, and questions, which is what mnemosyne needs.
import json
import logging
from pathlib import Path
from typing import AsyncIterator

from zeus.ingest.pipeline import Chunk, chunk_text

logger = logging.getLogger("iris")

# Which roles to ingest. "user" = Chris's messages; add "assistant" if you want
# the AI's responses too (useful for capturing answers Chris relied on).
DEFAULT_ROLES = {"user"}


class ChatGPTSource:
    """
    Parse a ChatGPT export and yield chunks.

    Accepts either:
      - A single JSON file (legacy conversations.json)
      - A directory containing conversations-NNN.json files (2025+ export format)

    Export format (both variants):
      list[Conversation]
      Conversation = { "title": str, "create_time": float, "mapping": { id: Node } }
      Node = { "message": Message | null, "parent": str | null, "children": list[str] }
      Message = { "author": {"role": str}, "content": {"content_type": str, "parts": list} }
    """

    target: str = "knowledge"

    def __init__(
        self,
        path: str | Path,
        roles: set[str] = DEFAULT_ROLES,
        chunk_size: int = 512,
        chunk_overlap: int = 64,
        user_id: str = "chris",
        min_chars: int = 50,
    ) -> None:
        self.path = Path(path)
        self.roles = roles
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.user_id = user_id
        self.min_chars = min_chars

    def _discover_files(self) -> list[Path]:
        """Return conversation JSON files to process."""
        if self.path.is_file():
            return [self.path]

        if self.path.is_dir():
            files = sorted(self.path.glob("conversations*.json"))
            if not files:
                logger.error(f"chatgpt: no conversations*.json files in {self.path}")
            else:
                logger.info(f"chatgpt: found {len(files)} conversation file(s) in {self.path}")
            return files

        logger.error(f"chatgpt: path does not exist — {self.path}")
        return []

    def _load_file(self, filepath: Path) -> list[dict]:
        """Load and validate a single conversation JSON file."""
        try:
            raw = filepath.read_text(encoding="utf-8")
            data = json.loads(raw)
        except (OSError, json.JSONDecodeError) as e:
            logger.error(f"chatgpt: cannot load {filepath} — {e}")
            return []

        if not isinstance(data, list):
            logger.error(
                f"chatgpt: expected list at root of {filepath.name}, "
                f"got {type(data).__name__}"
            )
            return []

        return data

    def _iter_messages(self, data: list[dict]):
        """Walk each conversation tree and yield (conv_title, role, text) tuples."""
        for conv in data:
            title = conv.get("title", "untitled")
            mapping = conv.get("mapping", {})

            for node in mapping.values():
                msg = node.get("message")
                if not msg:
                    continue

                role = msg.get("author", {}).get("role", "")
                if role not in self.roles:
                    continue

                content = msg.get("content", {})
                if content.get("content_type") != "text":
                    continue

                parts = content.get("parts", [])
                text = " ".join(p for p in parts if isinstance(p, str)).strip()

                if len(text) < self.min_chars:
                    continue

                yield title, role, text

    async def chunks(self) -> AsyncIterator[Chunk]:
        files = self._discover_files()
        if not files:
            return

        total_convs = 0
        for filepath in files:
            data = self._load_file(filepath)
            if not data:
                continue

            total_convs += len(data)
            logger.info(f"chatgpt: processing {filepath.name} ({len(data)} conversations)")

            for conv_title, role, text in self._iter_messages(data):
                for chunk_text_piece in chunk_text(text, self.chunk_size, self.chunk_overlap):
                    yield Chunk(
                        text=chunk_text_piece,
                        source=f"chatgpt:{conv_title}",
                        metadata={
                            "conversation": conv_title,
                            "role": role,
                            "type": "chatgpt_export",
                            "source_file": filepath.name,
                        },
                        user_id=self.user_id,
                    )

        logger.info(f"chatgpt: finished — {total_convs} conversations across {len(files)} file(s)")
