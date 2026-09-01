# Copyright (c) 2026 kraynux - Licence MIT
"""Composition ASCII de l'ecran de demarrage. Logo fourni par l'utilisateur,
voir ~/DEV/FUZZ/ascii.txt — caracteres extraits PROGRAMMATIQUEMENT du
fichier source (`expandtabs(4)`, seul tabsize qui garde le petit boitier
serveur aligne sur ses 4 lignes — `expandtabs(8)` casse cet alignement),
jamais retranscrits a la main (meme discipline que l'ancienne composition
ASCII d'omega-stress, qui documentait deja ce risque de decalage).

Couleur par jetons de theme Rich/Textual (`$accent`=vif, `$foreground`
=clair) directement dans le markup, jamais des couleurs hex figees — meme
mecanisme que widgets/home_wordmark.py, reactif au changement de theme. Le
widget lui-meme porte `color: $accent` (styles/base.tcss, .omega-splash-hero) :
tout texte NON explicitement enveloppe dans ce module herite donc du vif
par defaut — seules les parties clair/nuancees ont besoin d'un marquage
explicite (meme optimisation que le "|"-vif/mots-clair de la tagline).

Regles de couleur fournies dans ascii.txt :
- cadres/"containers" (box-drawing : cadres du titre, du bandeau OMEGA-FUZZ,
  du petit boitier serveur, connecteurs ╠╣╔╗╚╝) : clair.
- "LINUX VULNERABILITY SCAN" et "v1.0" : vif (herite du defaut du widget,
  aucun marquage necessaire).
- bandeau OMEGA-FUZZ (3 lignes, dans son cadre) : vif / clair / vif.
- tagline du bas : "|" vifs (defaut), mots clairs (marques explicitement).
- █=clair, ▓=moins clair, ▒=encore moins, ░=encore moins : echelle a 4
  niveaux rendue via l'opacite de jeton de theme (`$foreground`, `75%`,
  `50%`, `25%` — verifie fonctionnel, Textual 8.2.8). `▄` (bloc plein)
  traite comme `█` : aucune regle dediee, meme poids visuel qu'un bloc
  plein.
"""
from __future__ import annotations

from textual.widgets import Static

_FOREGROUND = "$foreground"
_ACCENT = "$accent"

_ART_ROWS: tuple[str, ...] = (
    '                          ┌────────────────────────────┐',
    '                          │  LINUX VULNERABILITY SCAN  │',
    '                          └────────────────────────────┘',
    '                                       ╔╗',
    '                                       ║║',
    '                                  ░╠▓▓▓╣╠▓▓▓╣░',
    '                              ░╠▓▓▓▓▓▓v1.0▓▓▓▓▓▓╣░',
    '┌────────────────────────────────────────────────────────────────────────────┐',
    '│ ┌╦═══╦┐ ┌╦═╦═╦┐ ┌╦═══╦┐ ┌╦═══╦┐ ┌╦═══╦┐    ┌╦═══╦┐ ┌╦   ╦┐ ┌╦═══╦┐ ┌╦═══╦┐ │',
    '│ │║   ║│ │║ ║ ║│ ├╬══    │║  ═╦┐ ├╬═══╬┤ ═  ├╬══    │║   ║│ ┌╦═══╩┘ ┌╦═══╩┘ │',
    '│ └╩═══╩┘ └╩   ╩┘ └╩═══╩┘ └╩═══╩┘ └╩   ╩┘    └╩      └╩═══╩┘ └╩═══╩┘ └╩═══╩┘ │',
    '└────────────────────────────────────────────────────────────────────────────┘',
    '                     ░╠▓▓╣   ╠█╣░      ╔╗      ░╠█╣   ╠▓▓╣░',
    '                 ░╠════════════╣░   ░╠═╣╠═╣░   ░╠════════════╣░',
    '                     ░╠▓▓╣   ╠█╣░      ╚╝      ░╠█╣   ╠▓▓╣░',
    '               ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄█╣░            ░╠█▄▄▄▄▄▄▄▄▄▄▄▄▄▄',
    '               █┌─────────────┐█ █╣░░░ ╔╗ ░░░╠█╣╔█░░░░░░░░░░░░█┐',
    '               █│░░░░░░░░░░░░░│█  ╠████╣╠████╣  ║█░▒▓█▒░░▒▓▓▒░█│',
    '               █│░░░░░░░░░░░░░│█▓╣     ║║       ║█░░░░░░░░░░░░█│',
    '               █└─────────────┘█ ▓▓▓▓▓▓╣╠▓▓▓▓▓▓▓║█░▒▓▓▒░░▒▓█▒░█╣',
    '               ████████▓████████  ░╠▓▓▓╣╠▓▓▓╣░  ║█░░░░░░░░░░░░█│',
    '                     ║███║             ║║        ██████████████',
    '                                       ╚╝',
    '         SCAN | NETWORKS  | SERVER | VULNERABILITY | ANALYSE | EXPORT',
)

_SHADE_TOKENS: dict[str, str] = {
    "█": _FOREGROUND,
    "▄": _FOREGROUND,
    "▓": f"{_FOREGROUND} 75%",
    "▒": f"{_FOREGROUND} 50%",
    "░": f"{_FOREGROUND} 25%",
}
_FRAME_CHARS = frozenset("┌┬┐├┼┤└┴┘│─╔╦╗╠╬╣╚╩╝║═")

_EXCEPTIONS: frozenset[tuple[int, int]] = frozenset({(19, 59), (20, 23)})
"""Coordonnees (ligne, colonne) 0-indexees dans `_ART_ROWS` des deux
caracteres "voyant" (vif) signales par ascii.txt : le seul `▓` de la ligne
`████████▓████████` (base du petit boitier serveur — "▓ dans le bas de
l'ecran") et le dernier `█` de la texture d'ecran du moniteur, ligne 19,
juste avant le `╣` de fermeture ("█ dans le serveur en bas a droite a
l'interieur"). Lecture necessairement interpretative : le texte source ne
designe pas un caractere unique sans ambiguite (deux formes plausibles
existent pour chaque description) — corrigible en changeant uniquement
ces deux coordonnees si ce n'est pas ce qui etait visualise."""


def _char_markup(row_index: int, col_index: int, char: str) -> str | None:
    """Couleur a appliquer a un caractere de la scene (lignes 3-22,
    connecteurs/bloc de boitier/tagline exclue) : `None` = herite du vif
    par defaut du widget (espace, ou tout glyphe non specifiquement
    couvert par une regle de couleur)."""
    if (row_index, col_index) in _EXCEPTIONS:
        return _ACCENT
    if char in _SHADE_TOKENS:
        return _SHADE_TOKENS[char]
    if char in _FRAME_CHARS:
        return _FOREGROUND
    return None


def _wrap(color: str | None, text: str) -> str:
    return text if color is None else f"[{color}]{text}[/]"


def _colorize_scene_row(row_index: int, row: str) -> str:
    """Regroupe les caracteres consecutifs de meme couleur en un seul
    span de markup (lisibilite, pas une contrainte de rendu)."""
    spans: list[str] = []
    run: list[str] = []
    run_color: str | None = None
    for col_index, char in enumerate(row):
        color = _char_markup(row_index, col_index, char)
        if color != run_color and run:
            spans.append(_wrap(run_color, "".join(run)))
            run = []
        run.append(char)
        run_color = color
    if run:
        spans.append(_wrap(run_color, "".join(run)))
    return "".join(spans)


def _split_frame_row(row: str, *, inner_color: str | None) -> str:
    """Ligne du type '│ ... │' : cadre clair, interieur dans
    `inner_color` (`None` = vif, le defaut du widget)."""
    first = row.index("│")
    last = row.rindex("│")
    prefix = row[:first]
    inner = row[first + 1 : last]
    suffix = row[last + 1 :]
    return (
        f"{prefix}[{_FOREGROUND}]│[/]"
        f"{_wrap(inner_color, inner)}"
        f"[{_FOREGROUND}]│[/]{suffix}"
    )


def _colorize_tagline(row: str) -> str:
    """'|' vifs (defaut, non enveloppes), mots clairs."""
    return "|".join(f"[{_FOREGROUND}]{part}[/]" for part in row.split("|"))


def _build_markup() -> tuple[str, ...]:
    lines: list[str] = []
    for index, row in enumerate(_ART_ROWS):
        if index in (0, 2, 3, 4, 7, 11, 22):
            lines.append(_wrap(_FOREGROUND, row))
        elif index == 1 or index == 8:
            lines.append(_split_frame_row(row, inner_color=None))
        elif index == 9:
            lines.append(_split_frame_row(row, inner_color=_FOREGROUND))
        elif index == 10:
            lines.append(_split_frame_row(row, inner_color=None))
        elif index == 23:
            lines.append(_colorize_tagline(row))
        else:
            lines.append(_colorize_scene_row(index, row))
    return tuple(lines)


_ART_MARKUP = "\n".join(_build_markup())


class SplashHero(Static):
    """Bloc decoratif de l'ecran de demarrage (screens/splash.py). Masque
    entierement en profil REDUCED/MONO (styles/reduced.tcss, mono.tcss :
    `.omega-splash-hero { display: none; }`) — degradation structurelle
    par feuille de style, jamais de version compacte recalculee en Python
    (meme mecanisme que omega-check)."""

    def __init__(self) -> None:
        super().__init__(_ART_MARKUP, classes="omega-splash-hero")
