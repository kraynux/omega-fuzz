# Copyright (c) 2026 kraynux - Licence MIT
"""Contrat d'emission d'evenements structures (OMEGA-FUZZ_ARBORESCENCE.md
§15.3). Distinct du module `logging` standard consomme directement par
`infrastructure` : ce port existe pour que `domain`/`application`
puissent emettre des evenements sans dependre d'une bibliotheque de
logging concrete."""
from __future__ import annotations

from typing import Any, Protocol


class Logger(Protocol):
    def info(self, event: str, **fields: Any) -> None: ...

    def warning(self, event: str, **fields: Any) -> None: ...

    def error(self, event: str, **fields: Any) -> None: ...
