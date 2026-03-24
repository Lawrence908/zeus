# zeus/ingest/sources/chatgpt.py — Iris ChatGPT export parser
# Parses the conversations.json from a ChatGPT data export (Settings → Export).
# Each conversation is flattened into user+assistant turn pairs and chunked.
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
    Parse a ChatGPT conversations.json export and yield chunks.

    Export format (as of 2024):
      list[Conversation]
      Conversation = { "title": str, "create_time": float, "mapping": { id: Node } }
      Node = { "message": Message | null, "parent": str | null, "children": list[str] }
      Message = { "author": {"role": str}, "content": {"content_type": str, "parts": list} }
    """

    def __init__(
        self,
        path: str | Path,
        roles: set[str] = DEFAULT_ROLES,
        chunk_size: int = 512,
        chunk_overlap: int = 64,
        user_id: str = "chris",
        min_chars: int = 50,       # skip very short messages (greetings, ack)
    ) -> None:
        self.path = Path(path)
        self.roles = roles
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.user_id = user_id
        self.min_chars = min_chars

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
                # content_type "text" has a "parts" list of strings
                if content.get("content_type") != "text":
                    continue

                parts = content.get("parts", [])
                text = " ".join(p for p in parts if isinstance(p, str)).strip()

                if len(text) < self.min_chars:
                    continue

                yield title, role, text

    async def chunks(self) -> AsyncIterator[Chunk]:
        try:
            raw = self.path.read_text(encoding="utf-8")
            data = json.loads(raw)
        except (OSError, json.JSONDecodeError) as e:
            logger.error(f"chatgpt: cannot load {self.path} — {e}")
            return

        if not isinstance(data, list):
            logger.error(f"chatgpt: expected list at root, got {type(data).__name__}")
            return

        for conv_title, role, text in self._iter_messages(data):
            for chunk_text_piece in chunk_text(text, self.chunk_size, self.chunk_overlap):
                yield Chunk(
                    text=chunk_text_piece,
                    source=f"chatgpt:{conv_title}",
                    metadata={
                        "conversation": conv_title,
                        "role": role,
                        "type": "chatgpt_export",
                    },
                    user_id=self.user_id,
                )
