# Copyright (c) 2026 kraynux - Licence MIT
"""Bandeau texte OMEGA-FUZZ affiche en haut de screens/home.py (logo fourni
par l'utilisateur, voir ~/DEV/FUZZ/ascii.txt, lignes du bloc "MENU PRINCIPAL"
— caracteres non modifies, meme regle que le logo de omega-check). Couleur
par jetons de theme Rich/Textual (`$accent`/`$foreground`) directement dans
le markup — pas des couleurs hex figees, reactif au changement de theme
(meme mecanisme que widgets/splash_hero.py)."""
from __future__ import annotations

from textual.widgets import Static

_WORDMARK_LINES: tuple[str, str, str] = (
    '┌╦═══╦┐ ┌╦═╦═╦┐ ┌╦═══╦┐ ┌╦═══╦┐ ┌╦═══╦┐   ┌╦═══╦┐ ┌╦   ╦┐ ┌╦═══╦┐ ┌╦═══╦┐',
    '│║   ║│ │║ ║ ║│ ├╬══    │║  ═╦┐ ├╬═══╬┤ ═ ├╬══    │║   ║│ ┌╦═══╩┘ ┌╦═══╩┘',
    '└╩═══╩┘ └╩   ╩┘ └╩═══╩┘ └╩═══╩┘ └╩   ╩┘   └╩      └╩═══╩┘ └╩═══╩┘ └╩═══╩┘',
)
"""OMEGA-FUZZ en un seul bandeau de lettres, fourni par l'utilisateur
(~/DEV/FUZZ/ascii.txt), caracteres non modifies."""

_MARKUP = "\n".join((
    f"[$accent]{_WORDMARK_LINES[0]}[/]",
    f"[$foreground]{_WORDMARK_LINES[1]}[/]",
    f"[$accent]{_WORDMARK_LINES[2]}[/]",
))


class HomeWordmark(Static):
    """Bandeau decoratif centre en haut de screens/home.py."""

    def __init__(self) -> None:
        super().__init__(_MARKUP, classes="omega-home-wordmark")
