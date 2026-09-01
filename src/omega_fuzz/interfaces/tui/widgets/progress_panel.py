# Copyright (c) 2026 kraynux - Licence MIT
"""Indicateur de progression indetermine, avec le detail des operations en
cours. Porte depuis omega-check (D-007/D-008), adapte (Phase 10g/10l) :
`extra` accepte des widgets supplementaires (le bouton "Arreter",
omega-fuzz n'a pas d'equivalent cote CHECK) inseres apres le RichLog,
dans le meme bloc centre par `.omega-progress-panel` (`align: center
middle`) — plutot qu'en frere du panneau, ce qui le poussait tout en bas
de l'ecran, colle a gauche (bug reel rapporte)."""
from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Middle
from textual.widgets import LoadingIndicator, RichLog, Static

if TYPE_CHECKING:
    from collections.abc import Iterable

    from textual.widget import Widget


class ProgressPanel(Middle):
    """Ecran d'attente pendant l'execution d'un scan."""

    def __init__(self, *, message: str, extra: Iterable[Widget] = ()) -> None:
        super().__init__(
            Static(message, classes="omega-subtitle"),
            LoadingIndicator(),
            RichLog(classes="omega-progress-log", max_lines=200, auto_scroll=True, markup=False),
            *extra,
            classes="omega-progress-panel",
        )

    def write_line(self, line: str) -> None:
        self.query_one(RichLog).write(line)
