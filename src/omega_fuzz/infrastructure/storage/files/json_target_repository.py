# Copyright (c) 2026 kraynux - Licence MIT
"""Implementation JSON du port TargetRepository (Phase 10j), meme
convention que json_settings_store.py."""
from __future__ import annotations

import json
from pathlib import Path


class JsonTargetRepository:
    """Implemente ports/target_repository.py::TargetRepository."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def add(self, url: str) -> None:
        urls = list(self.list_all())
        if url not in urls:
            urls.append(url)
        self._write(urls)

    def remove(self, url: str) -> None:
        urls = [existing for existing in self.list_all() if existing != url]
        self._write(urls)

    def list_all(self) -> list[str]:
        if not self._path.exists():
            return []
        return list(json.loads(self._path.read_text(encoding="utf-8")))

    def _write(self, urls: list[str]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(urls, indent=2, ensure_ascii=False), encoding="utf-8")
