# Copyright (c) 2026 kraynux - Licence MIT
"""Implemente ports/logger.py::Logger via le module standard `logging`
(Phase 10b). Format `event key=value ...` : lisible directement dans un
terminal, pas de dependance a une bibliotheque de structured logging
tierce pour ce besoin minimal.

Phase 10c : `console=False` (sous le TUI) n'attache aucun handler
d'ecriture — Textual controle l'ecran en mode alternatif, une ecriture
directe sur stderr pendant que le TUI tourne corromprait son rendu (meme
raison que `omega_check.app.bootstrap.bootstrap(console_logging=...)`)."""
from __future__ import annotations

import logging
from typing import Any


class StdlibLogger:
    """Implemente ports/logger.py::Logger."""

    def __init__(self, *, name: str = "omega_fuzz", console: bool = True) -> None:
        self._logger = logging.getLogger(name)
        self._logger.handlers.clear()
        if console:
            handler: logging.Handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
        else:
            handler = logging.NullHandler()
        self._logger.addHandler(handler)
        self._logger.setLevel(logging.INFO)
        self._logger.propagate = False

    @staticmethod
    def _format(event: str, fields: dict[str, Any]) -> str:
        rendered_fields = " ".join(f"{key}={value!r}" for key, value in fields.items())
        return f"{event} {rendered_fields}" if rendered_fields else event

    def info(self, event: str, **fields: Any) -> None:
        self._logger.info(self._format(event, fields))

    def warning(self, event: str, **fields: Any) -> None:
        self._logger.warning(self._format(event, fields))

    def error(self, event: str, **fields: Any) -> None:
        self._logger.error(self._format(event, fields))
