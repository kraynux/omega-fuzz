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

from pathlib import Path
from typing import TYPE_CHECKING

from omega_lib.terminal.models import RenderProfile
from omega_lib.theme.policies import TUI_THEMES
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Input, Select, Static

from omega_fuzz.application.commands.clear_directory import (
    ClearResult,
    UnsafeDirectoryError,
    clear_directory,
)
from omega_fuzz.application.commands.clear_scan_history import clear_scan_history
from omega_fuzz.application.commands.select_render_profile import select_render_profile
from omega_fuzz.application.commands.select_theme import select_theme
from omega_fuzz.application.exceptions import UnknownThemeError
from omega_fuzz.application.services.report_orchestrator import resolve_exports_dir
from omega_fuzz.application.services.screenshot_settings import resolve_screenshots_dir
from omega_fuzz.interfaces.tui.language_setting import LanguageSetting
from omega_fuzz.interfaces.tui.screens._base import OmegaScreen
from omega_fuzz.interfaces.tui.screens.confirm_screen import ConfirmScreen
from omega_fuzz.shared.i18n import _

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
            yield Static(_("RÉGLAGES"), classes="omega-title")

            yield Static(_("Thème"), classes="omega-subtitle")
            yield Select([(name, name) for name in TUI_THEMES], value=self.app.theme, id="theme-select")

            yield Static(_("Profil de rendu (redémarrage requis)"), classes="omega-subtitle")
            current_override = store.get(_RENDER_PROFILE_OVERRIDE_KEY, "")
            yield Select(
                [(_("Automatique"), _AUTO), *((profile.value, profile.value) for profile in RenderProfile)],
                value=current_override or _AUTO,
                id="render-profile-select",
            )

            yield LanguageSetting(self._container.settings_store)

            yield Static(_("Dossier d'export"), classes="omega-subtitle")
            yield Input(
                value=store.get(_EXPORTS_DIR_OVERRIDE_KEY, str(self._container.default_exports_dir))
                or "",
                id="exports-dir-input",
            )

            yield Static(_("Dossier des captures d'écran"), classes="omega-subtitle")
            yield Input(
                value=store.get(
                    _SCREENSHOTS_DIR_OVERRIDE_KEY, str(self._container.default_screenshots_dir)
                )
                or "",
                id="screenshots-dir-input",
            )

            yield Static(_("Purge"), classes="omega-subtitle")
            with Horizontal(classes="omega-actions"):
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Vider l'historique"), id="clear-history", variant="error")
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Supprimer les exports"), id="clear-exports", variant="error")
            with Horizontal(classes="omega-actions"), Container(classes="omega-btn-frame"):
                yield Button(
                    _("Supprimer les captures d'écran"), id="clear-screenshots", variant="error"
                )

            with Horizontal(classes="omega-actions"), Container(classes="omega-btn-frame"):
                yield Button(_("Retour"), id="back")
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
        self.app.notify(_("Appliqué au prochain démarrage."), title=_("Profil de rendu"))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.dismiss()
        elif event.button.id == "clear-history":
            self.app.push_screen(
                ConfirmScreen(
                    title=_("VIDER L'HISTORIQUE ?"),
                    message=_("Tous les scans et findings persistés seront définitivement "
                              "supprimés."),
                ),
                self._clear_history_if_confirmed,
            )
        elif event.button.id == "clear-exports":
            exports_dir = resolve_exports_dir(
                settings_store=self._container.settings_store,
                default_exports_dir=self._container.default_exports_dir,
            )
            self._confirm_clear(exports_dir, _("SUPPRIMER LES EXPORTS ?"))
        elif event.button.id == "clear-screenshots":
            screenshots_dir = resolve_screenshots_dir(
                settings_store=self._container.settings_store,
                default_screenshots_dir=self._container.default_screenshots_dir,
            )
            self._confirm_clear(screenshots_dir, _("SUPPRIMER LES CAPTURES D'ÉCRAN ?"))

    def _confirm_clear(self, directory: Path, title: str) -> None:
        """Correctif 2026-10-27 (commun a la suite) : chemin exact montre avant de supprimer,
        garde-fous et suppression hors du thread de l'interface (clear_directory.py)."""
        self.app.push_screen(
            ConfirmScreen(
                title=title,
                message=_("Tout le contenu de ce dossier sera définitivement supprimé "
                          ":\n{directory}").format(directory=directory),
            ),
            lambda confirmed: self._clear_if_confirmed(directory, confirmed),
        )

    def _clear_if_confirmed(self, directory: Path, confirmed: bool | None) -> None:
        if not confirmed:
            return
        self.app.notify(_("Suppression en cours..."), timeout=3)
        self.run_worker(lambda: self._clear_in_thread(directory), thread=True, exclusive=True)

    def _clear_in_thread(self, directory: Path) -> None:
        # Racine de l'application = parent de var/ (dossier d'exports par defaut = var/exports).
        app_root = self._container.default_exports_dir.parent.parent
        try:
            result = clear_directory(directory, app_root)
        except (UnsafeDirectoryError, OSError) as exc:
            self.app.call_from_thread(self.app.notify, str(exc), severity="error", timeout=10)
            return
        self.app.call_from_thread(self._on_cleared, result)

    def _on_cleared(self, result: ClearResult) -> None:
        if not result.failed:
            self.app.notify(_("{removed} élément(s) supprimé(s) : {directory}").format(removed=result.removed, directory=result.directory))
            return
        shown = ", ".join(result.failed[:3]) + (" ..." if len(result.failed) > 3 else "")
        self.app.notify(
            _("{removed} élément(s) supprimé(s), {count} impossible(s) à supprimer : {shown}").format(removed=result.removed, count=len(result.failed), shown=shown),
            severity="warning", timeout=15,
        )

    def _clear_history_if_confirmed(self, confirmed: bool | None) -> None:
        if not confirmed:
            return
        clear_scan_history(scan_repository=self._container.scan_repository)
        self.app.notify(_("Historique vidé."))
