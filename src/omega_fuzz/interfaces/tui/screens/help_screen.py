# Copyright (c) 2026 kraynux - Licence MIT
"""Ecran Aide : reference statique des raccourcis et fonctions de l'application.
Adapte du patron screens/help_screen.py d'omega-check (D-007/D-008) — memes
raccourcis (chrome partage par toute la suite), contenu propre a FUZZ. Reste
volontairement generique sur les fonctions (Scanner/Historique/Cibles) : ces
ecrans n'existent pas encore (Phase 10c ne livre que splash + home), aucune
instruction de navigation vers un ecran inexistant.

Phase 10j : tableau des presets (`domain.profiles.preset.PRESETS`, deja
construit Phase 5), meme patron que le tableau `SYSTEM_PROFILES` de
omega-check/interfaces/tui/screens/help_screen.py — demande explicite
("integrer le tableau des valeurs de mesure de test des presets")."""
from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.widgets import Button, DataTable, Footer, Header, Static

from omega_fuzz.domain.profiles.preset import PRESETS
from omega_fuzz.interfaces.tui.screens._base import OmegaScreen

_SHORTCUTS = (
    ("Haut / Bas", "Naviguer entre les elements d'un ecran"),
    ("Tab / Maj+Tab", "Naviguer entre les champs d'un formulaire"),
    ("Echap", "Retour a l'ecran precedent (confirmation de sortie sur l'accueil)"),
    ("t", "Theme suivant (applique immediatement, sans confirmation)"),
    ("r", "Rafraichir la detection du terminal"),
    ("a", "Cette aide"),
    ("q", "Quitter (avec confirmation)"),
)

_SCOPE_NOTICE = (
    "Omega-fuzz decouvre une cible dans un perimetre controle (scope explicite, "
    "profondeur limitee) puis teste activement les points d'entree trouves "
    "(parametres de requete, headers de securite) — jamais sans confirmation "
    "explicite pour les profils/modes a risque (agressivite violente, "
    "verification TLS desactivee)."
)


class HelpScreen(OmegaScreen):
    """Reference statique, accessible depuis n'importe quel ecran (touche `a`)."""

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll(classes="omega-panel"):
            yield Static("AIDE", classes="omega-title")
            yield Static("Raccourcis clavier", classes="omega-subtitle")
            for key, description in _SHORTCUTS:
                yield Static(f"{key:<14} {description}")
            yield Static("")
            yield Static(_SCOPE_NOTICE, classes="omega-subtitle")
            yield Static("")
            yield Static("Presets", classes="omega-subtitle")
            yield DataTable(id="preset-table")
            with Horizontal(classes="omega-actions"), Container(classes="omega-btn-frame"):
                yield Button("Retour", id="back")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#preset-table", DataTable)
        table.add_columns(
            "Preset",
            "Scope",
            "Agressivite",
            "Duree max",
            "Requetes max",
            "Tests max",
            "Profondeur max",
            "Confirmation",
        )
        for name, definition in PRESETS.items():
            table.add_row(
                name.value,
                definition.scope_profile.value,
                definition.aggressiveness.value,
                f"{definition.max_duration_seconds} s",
                str(definition.max_total_requests),
                str(definition.max_tests),
                str(definition.max_depth),
                "oui" if definition.requires_confirmation else "non",
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.dismiss()
