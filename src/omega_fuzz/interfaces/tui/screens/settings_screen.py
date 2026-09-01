# Copyright (c) 2026 kraynux - Licence MIT
"""Ecran Reglages : theme, profil de rendu, dossiers d'export et de
captures d'ecran, purge de l'historique/des exports/des captures.
Adapte du patron screens/settings_screen.py d'omega-check (D-007/D-008)
— simplifie a ce que le stockage reel d'omega-fuzz supporte : une seule
purge d'historique (`ScanRepository.clear()` vide deja tout d'un coup,
rien a granulariser en historique/cibles distincts comme CHECK).

Phase 10f : `+ exports-dir-input`/`clear-exports` (bug/demande reels :
"permettre de choisir le dossier d'exports, par defaut var/exports/ a
introduire") — contrairement a CHECK, dont l'equivalent
`exports_dir_override` est persiste mais jamais relu au moment reel de
l'export (`export_dialog.py` utilise `container.default_exports_dir`
sans condition), la surcharge ecrite ici est bien relue par
`application.services.report_orchestrator.resolve_exports_dir`, appelee
par `scan_results_screen.py` ET `interfaces/cli/commands/scan_command.py`
— sinon changer ce reglage n'aurait aucun effet reel.

Phase 10k : `+ screenshots-dir-input`/`clear-screenshots` (demande reelle :
"rajouter le bouton supprimer les screenshots... et le dossier par
defaut var/screenshots a introduire avec possibilite de le modifier,
comme pour les exports") — meme patron, la surcharge est relue par
`application.services.screenshot_settings.resolve_screenshots_dir`,
appelee par `interfaces/tui/app.py` au moment reel de la capture."""
from __future__ import annotations

from typing import TYPE_CHECKING

from omega_lib.terminal.models import RenderProfile
from omega_lib.theme.policies import TUI_THEMES
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Input, Select, Static

from omega_fuzz.application.commands.clear_exports import clear_exports
from omega_fuzz.application.commands.clear_scan_history import clear_scan_history
from omega_fuzz.application.commands.clear_screenshots import clear_screenshots
from omega_fuzz.application.commands.select_render_profile import select_render_profile
from omega_fuzz.application.commands.select_theme import select_theme
from omega_fuzz.application.exceptions import UnknownThemeError
from omega_fuzz.application.services.report_orchestrator import resolve_exports_dir
from omega_fuzz.application.services.screenshot_settings import resolve_screenshots_dir
from omega_fuzz.interfaces.tui.screens._base import OmegaScreen
from omega_fuzz.interfaces.tui.screens.confirm_screen import ConfirmScreen

if TYPE_CHECKING:
    from omega_fuzz.app.container import Container as AppContainer

_AUTO = "auto"
_RENDER_PROFILE_OVERRIDE_KEY = "render_profile_override"
_EXPORTS_DIR_OVERRIDE_KEY = "exports_dir_override"
_SCREENSHOTS_DIR_OVERRIDE_KEY = "screenshots_dir_override"


class SettingsScreen(OmegaScreen):
    def __init__(self, *, container: AppContainer) -> None:
        super().__init__()
        self._container = container

    def compose(self) -> ComposeResult:
        store = self._container.settings_store
        yield Header()
        with Vertical(classes="omega-form-panel"):
            yield Static("REGLAGES", classes="omega-title")

            yield Static("Theme", classes="omega-subtitle")
            yield Select([(name, name) for name in TUI_THEMES], value=self.app.theme, id="theme-select")

            yield Static("Profil de rendu (redemarrage requis)", classes="omega-subtitle")
            current_override = store.get(_RENDER_PROFILE_OVERRIDE_KEY, "")
            yield Select(
                [("Automatique", _AUTO), *((profile.value, profile.value) for profile in RenderProfile)],
                value=current_override or _AUTO,
                id="render-profile-select",
            )

            yield Static("Dossier d'export", classes="omega-subtitle")
            yield Input(
                value=store.get(_EXPORTS_DIR_OVERRIDE_KEY, str(self._container.default_exports_dir))
                or "",
                id="exports-dir-input",
            )

            yield Static("Dossier des captures d'ecran", classes="omega-subtitle")
            yield Input(
                value=store.get(
                    _SCREENSHOTS_DIR_OVERRIDE_KEY, str(self._container.default_screenshots_dir)
                )
                or "",
                id="screenshots-dir-input",
            )

            yield Static("Purge", classes="omega-subtitle")
            with Horizontal(classes="omega-actions"):
                with Container(classes="omega-btn-frame"):
                    yield Button("Vider l'historique", id="clear-history", variant="error")
                with Container(classes="omega-btn-frame"):
                    yield Button("Supprimer les exports", id="clear-exports", variant="error")
            with Horizontal(classes="omega-actions"), Container(classes="omega-btn-frame"):
                yield Button(
                    "Supprimer les captures d'ecran", id="clear-screenshots", variant="error"
                )

            with Horizontal(classes="omega-actions"), Container(classes="omega-btn-frame"):
                yield Button("Retour", id="back")
        yield Footer()

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "theme-select":
            if str(event.value) == self.app.theme:
                return
            self._apply_theme(str(event.value))
        elif event.select.id == "render-profile-select":
            current_override = (
                self._container.settings_store.get(_RENDER_PROFILE_OVERRIDE_KEY, "") or _AUTO
            )
            if str(event.value) == current_override:
                return
            self._apply_render_profile(str(event.value))

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "exports-dir-input":
            self._container.settings_store.set(_EXPORTS_DIR_OVERRIDE_KEY, event.value)
        elif event.input.id == "screenshots-dir-input":
            self._container.settings_store.set(_SCREENSHOTS_DIR_OVERRIDE_KEY, event.value)

    def _apply_theme(self, theme_name: str) -> None:
        try:
            select_theme(settings_store=self._container.settings_store, theme_name=theme_name)
        except UnknownThemeError as exc:
            self.app.notify(str(exc), severity="error")
            return
        self.app.theme = theme_name

    def _apply_render_profile(self, value: str) -> None:
        profile = None if value == _AUTO else RenderProfile(value)
        select_render_profile(settings_store=self._container.settings_store, render_profile=profile)
        self.app.notify("Applique au prochain demarrage.", title="Profil de rendu")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.dismiss()
        elif event.button.id == "clear-history":
            self.app.push_screen(
                ConfirmScreen(
                    title="VIDER L'HISTORIQUE ?",
                    message="Tous les scans et findings persistes seront definitivement supprimes.",
                ),
                self._clear_history_if_confirmed,
            )
        elif event.button.id == "clear-exports":
            self.app.push_screen(
                ConfirmScreen(
                    title="SUPPRIMER LES EXPORTS ?",
                    message="Tous les fichiers du dossier d'export seront definitivement supprimes.",
                ),
                self._clear_exports_if_confirmed,
            )
        elif event.button.id == "clear-screenshots":
            self.app.push_screen(
                ConfirmScreen(
                    title="SUPPRIMER LES CAPTURES D'ECRAN ?",
                    message="Tous les fichiers du dossier de captures d'ecran seront definitivement supprimes.",
                ),
                self._clear_screenshots_if_confirmed,
            )

    def _clear_history_if_confirmed(self, confirmed: bool | None) -> None:
        if not confirmed:
            return
        clear_scan_history(scan_repository=self._container.scan_repository)
        self.app.notify("Historique vide.")

    def _clear_exports_if_confirmed(self, confirmed: bool | None) -> None:
        if not confirmed:
            return
        exports_dir = resolve_exports_dir(
            settings_store=self._container.settings_store,
            default_exports_dir=self._container.default_exports_dir,
        )
        clear_exports(exports_dir)
        self.app.notify("Exports supprimes.")

    def _clear_screenshots_if_confirmed(self, confirmed: bool | None) -> None:
        if not confirmed:
            return
        screenshots_dir = resolve_screenshots_dir(
            settings_store=self._container.settings_store,
            default_screenshots_dir=self._container.default_screenshots_dir,
        )
        clear_screenshots(screenshots_dir)
        self.app.notify("Captures d'ecran supprimees.")
