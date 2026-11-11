# Copyright (c) 2026 kraynux - Licence MIT
"""Point d'entree Textual de l'application, cable par le composition root
(app/main.py). Adapte du patron app.py d'omega-check (D-007/D-008)."""
from __future__ import annotations

import logging
from pathlib import PurePath
from typing import TYPE_CHECKING, ClassVar, cast

from omega_lib.terminal.models import RenderProfile
from omega_lib.theme.policies import TUI_THEMES
from textual.app import App, SystemCommand
from textual.binding import Binding, BindingType

from omega_fuzz.application.commands.select_theme import select_theme
from omega_fuzz.application.exceptions import UnknownThemeError
from omega_fuzz.application.queries.detect_terminal import detect_terminal
from omega_fuzz.application.services.screenshot_settings import resolve_screenshots_dir
from omega_fuzz.interfaces.tui.controllers.startup_controller import (
    StartupState,
    resolve_startup_state,
)
from omega_fuzz.interfaces.tui.language_setting import notify_language_at_startup
from omega_fuzz.interfaces.tui.rendering.stylesheet_loader import load_paths_for
from omega_fuzz.interfaces.tui.rendering.textual_theme_builder import build_all_textual_themes
from omega_fuzz.interfaces.tui.screens.help_screen import HelpScreen
from omega_fuzz.interfaces.tui.screens.home import HomeScreen
from omega_fuzz.interfaces.tui.screens.quit_confirm import QuitConfirmScreen
from omega_fuzz.interfaces.tui.screens.splash import SplashScreen
from omega_fuzz.interfaces.tui.screens.terminal_warning import TerminalWarningScreen
from omega_fuzz.shared.i18n import N_, _

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable
    from pathlib import Path

    from textual.screen import Screen

    from omega_fuzz.app.container import Container, ScanRuntime

TITLE = _("🗱 OMEGA-FUZZ")
"""Icone incluse DANS la chaine de titre (memes raisons que le reste de la
suite : HeaderIcon/HeaderTitle sont deux widgets Textual distincts, les
fondre dans une seule chaine les fait apparaitre comme une unite)."""


class OmegaFuzzApp(App[None]):
    """Application TUI d'omega-fuzz : resout theme/profil de rendu au
    demarrage, puis enchaine splash -> (avertissement terminal) -> accueil."""

    TITLE = TITLE
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("q", "quit", _("Quitter"), show=True),
        Binding("ctrl+q", "quit", _("Quitter"), show=False),
        Binding("t", "cycle_theme", _("Thème suivant"), show=True),
        Binding("r", "refresh_terminal", _("Rafraîchir"), show=True),
        Binding("a", "help", _("Aide"), show=True),
    ]

    def __init__(
        self,
        container: Container,
        *,
        scan_runtime_factory: Callable[[Path | None], ScanRuntime],
    ) -> None:
        self._container = container
        self._scan_runtime_factory = scan_runtime_factory
        self._startup_state = resolve_startup_state(
            terminal_detector=container.terminal_detector,
            settings_store=container.settings_store,
        )
        css_path = cast(
            "list[str | PurePath]", load_paths_for(self._startup_state.theme.render_profile)
        )
        self.pending_language: str | None = None
        """Langue choisie dans les Reglages : __main__.py relance l'interface apres la fermeture."""
        super().__init__(css_path=css_path)
        for theme in build_all_textual_themes():
            self.register_theme(theme)
        self.theme = self._startup_state.theme.theme_name

    def on_mount(self) -> None:
        notify_language_at_startup(self)
        self.push_screen(SplashScreen(), self._after_splash)

    def _after_splash(self, _result: None) -> None:
        terminal = self._startup_state.terminal
        too_small = terminal.signals.columns < 80 or terminal.signals.rows < 24
        if terminal.render_profile == RenderProfile.MONO or too_small:
            message = (
                _("Terminal détecté : {family} ({columns}x{rows}). Rendu appliqué : {value}.").format(family=terminal.signals.family, columns=terminal.signals.columns, rows=terminal.signals.rows, value=terminal.render_profile.value)
            )
            self.push_screen(TerminalWarningScreen(message=message), self._show_home)
        else:
            self._show_home(None)

    def _show_home(self, _result: None) -> None:
        self.push_screen(
            HomeScreen(
                container=self._container, scan_runtime_factory=self._scan_runtime_factory
            )
        )

    def watch_theme(self, _theme_name: str) -> None:
        terminal = self._startup_state.terminal
        self.sub_title = _("{theme} | {columns}x{rows}").format(theme=self.theme, columns=terminal.signals.columns, rows=terminal.signals.rows)

    async def action_quit(self) -> None:
        """Surcharge : demande confirmation avant de fermer."""
        self.push_screen(QuitConfirmScreen(), self._quit_if_confirmed)

    def _quit_if_confirmed(self, confirmed: bool | None) -> None:
        if confirmed:
            self.exit()

    def action_cycle_theme(self) -> None:
        """Touche `t` : bascule vers le theme SUIVANT du catalogue, sans
        confirmation."""
        names = list(TUI_THEMES.keys())
        current_index = names.index(self.theme) if self.theme in names else 0
        next_name = names[(current_index + 1) % len(names)]
        try:
            select_theme(settings_store=self._container.settings_store, theme_name=next_name)
        except UnknownThemeError as exc:
            self.notify(str(exc), severity="error")
            return
        except OSError as exc:
            # Retour utilisateur (GROS BUG omega-fire : "t" fermait
            # l'application) - meme correctif applique ici par coherence
            # (audit de la suite) : une simple erreur de persistance
            # (permissions, disque plein, systeme de fichiers en lecture
            # seule) faisait planter cette action sans aucun rattrapage.
            # Le theme change quand meme visuellement (self.theme =
            # next_name plus bas) : seule la PERSISTANCE du choix
            # echoue, pas la fonctionnalite immediate.
            self.notify(_("Thème appliqué mais non enregistré : {exc}").format(exc=exc), severity="warning")
        self.theme = next_name

    def action_refresh_terminal(self) -> None:
        """Touche `r` : redetecte taille/famille du terminal et met a jour
        le sous-titre du Header."""
        terminal = detect_terminal(terminal_detector=self._container.terminal_detector)
        self._startup_state = StartupState(terminal=terminal, theme=self._startup_state.theme)
        self.sub_title = _("{theme} | {columns}x{rows}").format(theme=self.theme, columns=terminal.signals.columns, rows=terminal.signals.rows)
        self.notify(
            _("{family} ({columns}x{rows})").format(family=terminal.signals.family, columns=terminal.signals.columns, rows=terminal.signals.rows),
            title=_("Terminal rafraîchi"),
        )

    def action_help(self) -> None:
        self.push_screen(HelpScreen(container=self._container))

    def get_system_commands(self, screen: Screen) -> Iterable[SystemCommand]:
        """Remplace la liste par defaut de Textual plutot que d'appeler
        `super()` (meme raisonnement que le reste de la suite), mais garde
        "Screenshot" (export SVG de l'ecran courant) : utile pour documenter
        un bug rencontre dans l'app."""
        yield SystemCommand(_("Thème"), _("Changer le thème actif"), self.action_change_theme)
        yield SystemCommand(
            _("Quitter"), _("Quitter l'application (avec confirmation)"), self.action_quit
        )
        yield SystemCommand(
            _("Screenshot"),
            _("Enregistrer une capture SVG de l'écran actuel"),
            self._save_screenshot,
        )

    def _save_screenshot(self) -> None:
        """Respecte la surcharge de dossier de l'ecran Reglages
        (`screenshots_dir_override`) — `App.deliver_screenshot` n'ecrit pas
        dans le repertoire courant s'il n'existe pas encore, contrairement a
        `export_report` qui le cree lui-meme."""
        screenshots_dir = resolve_screenshots_dir(
            settings_store=self._container.settings_store,
            default_screenshots_dir=self._container.default_screenshots_dir,
        )
        screenshots_dir.mkdir(parents=True, exist_ok=True)
        self.set_timer(0.1, lambda: self.deliver_screenshot(path=str(screenshots_dir)))

    def _handle_exception(self, error: Exception) -> None:
        """Filet de securite unique cote TUI : toute exception technique
        non prevue est journalisee puis affichee comme notification, sans
        jamais fermer l'application."""
        logging.getLogger("omega_fuzz").error(N_("Exception non prévue"), exc_info=error)
        self.notify(
            str(error) or type(error).__name__,
            title=_("Erreur inattendue"),
            severity="error",
            timeout=10,
        )
