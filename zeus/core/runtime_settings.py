# zeus/core/runtime_settings.py — Runtime-editable settings persisted to JSON.
#
# Runtime settings override environment variables at process start and can be
# mutated via `PATCH /settings` without restarting zeus-core. Used by LAB-322
# for the React Settings page to hot-reload Telegram / Aegis / model config.
from __future__ import annotations

import json
import logging
import os
import threading
from pathlib import Path
from typing import Any

logger = logging.getLogger("zeus.runtime_settings")

_DEFAULT_PATH = Path(
    os.getenv("ZEUS_RUNTIME_SETTINGS_PATH", "zeus/data/runtime_settings.json")
)


class RuntimeSettings:
    """Thread-safe JSON-backed settings store.

    Shape:
        {
          "telegram": {
            "enabled": bool,
            "bot_token": str,
            "allowed_chat_ids": list[int],
            "aegis_policy": str | None
          }
        }
    """

    def __init__(self, path: Path | str = _DEFAULT_PATH) -> None:
        self.path = Path(path)
        self._lock = threading.RLock()
        self._data: dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        with self._lock:
            if not self.path.is_file():
                return
            try:
                self._data = json.loads(self.path.read_text("utf-8")) or {}
            except Exception as exc:
                logger.warning("failed to load runtime settings %s: %s", self.path, exc)
                self._data = {}

    def save(self) -> None:
        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.path.with_suffix(self.path.suffix + ".tmp")
            tmp.write_text(json.dumps(self._data, indent=2), "utf-8")
            tmp.replace(self.path)

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return json.loads(json.dumps(self._data))

    def get_section(self, name: str) -> dict[str, Any]:
        with self._lock:
            return dict(self._data.get(name, {}))

    def update_section(self, name: str, values: dict[str, Any]) -> dict[str, Any]:
        """Merge ``values`` into section ``name`` and persist. Returns the new section."""
        with self._lock:
            section = dict(self._data.get(name, {}))
            section.update(values)
            self._data[name] = section
            self.save()
            return dict(section)
