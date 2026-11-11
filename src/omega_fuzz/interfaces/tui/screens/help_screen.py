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
from omega_fuzz.interfaces.tui.screens.contact_support import contact_support_screen
from omega_fuzz.shared.i18n import _

_SHORTCUTS = (
    (_("Haut / Bas"), _("Naviguer entre les éléments d'un écran")),
    (_("Tab / Maj+Tab"), _("Naviguer entre les champs d'un formulaire")),
    (_("Échap"), _("Retour à l'écran précédent (confirmation de sortie sur l'accueil)")),
    ("t", _("Thème suivant (appliqué immédiatement, sans confirmation)")),
    ("r", _("Rafraîchir la détection du terminal")),
    ("a", _("Cette aide")),
    ("q", _("Quitter (avec confirmation)")),
)

_SCOPE_NOTICE = (
    _("Omega-fuzz découvre une cible dans un périmètre contrôlé (scope explicite, profondeur "
      "limitée) puis teste activement les points d'entrée trouvés (paramètres de requête, "
      "headers de sécurité) — jamais sans confirmation explicite pour les profils/modes à "
      "risque (agressivité violente, vérification TLS désactivée).")
)


class HelpScreen(OmegaScreen):
    """Reference statique, accessible depuis n'importe quel ecran (touche `a`)."""

    def __init__(self, *, container: object | None = None) -> None:
        super().__init__()
        # Aide -> Contact et support (D-016, 2026-11-09) : services prepares par le conteneur de
        # l'outil (app/) ; absents (bouton masque) si l'aide est ouverte sans conteneur.
        self._contact_support = getattr(container, "contact_support", None)

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll(classes="omega-panel"):
            yield Static(_("AIDE"), classes="omega-title")
            yield Static(_("Raccourcis clavier"), classes="omega-subtitle")
            for key, description in _SHORTCUTS:
                yield Static(_("{key:<14} {description}").format(key=key, description=description))
            yield Static("")
            yield Static(_SCOPE_NOTICE, classes="omega-subtitle")
            yield Static("")
            yield Static(_("Presets"), classes="omega-subtitle")
            yield DataTable(id="preset-table")
            with Horizontal(classes="omega-actions"):
                if self._contact_support is not None:
                    with Container(classes="omega-btn-frame"):
                        yield Button(_("Contact et support"), id="contact-support", variant="primary")
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Retour"), id="back")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#preset-table", DataTable)
        table.add_columns(
            _("Preset"),
            _("Scope"),
            _("Agressivité"),
            _("Durée max"),
            _("Requêtes max"),
            _("Tests max"),
            _("Profondeur max"),
            _("Confirmation"),
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
                _("oui") if definition.requires_confirmation else _("non"),
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.dismiss()
        elif event.button.id == "contact-support" and self._contact_support is not None:
            self.app.push_screen(contact_support_screen(self._contact_support))
