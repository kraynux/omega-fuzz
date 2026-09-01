# Copyright (c) 2026 kraynux - Licence MIT
"""Ecran de saisie : cible, preset ou configuration manuelle, auth,
verification TLS, surcharges de limites (Phase 10d). Meme surface que la
CLI `scan` (interfaces/cli/parser.py), meme patron general que
omega-check/interfaces/tui/screens/scan_setup.py (Select revelant des
champs additionnels sur "configuration manuelle" = motif CUSTOM de CHECK).

`scan_runtime_factory` doit etre appelee ICI (pas dans l'ecran de
progression) : `prepare_scan()` a besoin d'un `AuthContext` deja resolu
(depuis le chemin `--auth-config` choisi), et seule la factory injectee
depuis app/composition_root.py peut le construire (interfaces/tui/ ne
peut pas appeler `infrastructure.configuration.auth_config_loader`
directement, Dependency Rule).

Phase 10j : `+ initial_target` — permet a `targets_screen.py`
("Scanner cette cible") de preremplir `#target-input`."""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Input, Select, Static, Switch

from omega_fuzz.application.commands.prepare_scan import prepare_scan
from omega_fuzz.core.errors import ValidationError
from omega_fuzz.domain.profiles.aggressiveness_level import AggressivenessLevel
from omega_fuzz.domain.profiles.preset import PresetName
from omega_fuzz.domain.profiles.scope_profile import ScopeProfileName
from omega_fuzz.domain.targets.url import UrlNormalizationError
from omega_fuzz.interfaces.tui.screens._base import OmegaScreen
from omega_fuzz.interfaces.tui.screens.scan_review_screen import ScanReviewScreen

if TYPE_CHECKING:
    from collections.abc import Callable

    from omega_fuzz.app.container import Container as AppContainer
    from omega_fuzz.app.container import ScanRuntime

_MANUAL = "__manual__"
_MODE_OPTIONS: tuple[tuple[str, str], ...] = (
    *((f"Preset : {preset.value}", preset.value) for preset in PresetName),
    ("Configuration manuelle", _MANUAL),
)
_SCOPE_PROFILE_OPTIONS = [(profile.value, profile.value) for profile in ScopeProfileName]
_AGGRESSIVENESS_OPTIONS = [(level.value, level.value) for level in AggressivenessLevel]

_OVERRIDE_FIELDS: tuple[tuple[str, str, str], ...] = (
    ("max-duration-input", "max_duration_seconds", "Duree max (s)"),
    ("max-requests-input", "max_total_requests", "Requetes max"),
    ("max-tests-input", "max_tests", "Tests max"),
    ("max-concurrent-input", "max_concurrent_requests", "Concurrence max"),
)


class ScanSetupScreen(OmegaScreen):
    """Formulaire de lancement d'un scan."""

    def __init__(
        self,
        *,
        container: AppContainer,
        scan_runtime_factory: Callable[[Path | None], ScanRuntime],
        initial_target: str | None = None,
    ) -> None:
        super().__init__()
        self._container = container
        self._scan_runtime_factory = scan_runtime_factory
        self._initial_target = initial_target

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="omega-form-panel"):
            yield Static("NOUVEAU SCAN", classes="omega-title")

            yield Static("Cible", classes="omega-subtitle")
            yield Input(
                value=self._initial_target or "", placeholder="https://example.com/", id="target-input"
            )

            yield Static("Configuration", classes="omega-subtitle")
            yield Select(_MODE_OPTIONS, value=PresetName.PROD_SAFE.value, id="mode-select")

            yield Select(_SCOPE_PROFILE_OPTIONS, value="standard", id="scope-profile-select", classes="omega-hidden")
            yield Select(
                _AGGRESSIVENESS_OPTIONS, value="standard", id="aggressiveness-select", classes="omega-hidden"
            )

            yield Static("Authentification (optionnel)", classes="omega-subtitle")
            yield Input(placeholder="chemin d'un fichier YAML --auth-config", id="auth-config-input")

            with Horizontal(classes="omega-form-switch-row"):
                yield Static("Verification TLS")
                yield Switch(value=True, id="verify-tls-switch")

            yield Static("Limites (optionnel, laisser vide pour garder le profil)", classes="omega-subtitle")
            for input_id, _field_name, label in _OVERRIDE_FIELDS:
                yield Input(placeholder=label, type="integer", id=input_id)

            with Horizontal(classes="omega-actions"):
                with Container(classes="omega-btn-frame"):
                    yield Button("Suivant", id="next", variant="primary")
                with Container(classes="omega-btn-frame"):
                    yield Button("Retour", id="back")
        yield Footer()

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id != "mode-select":
            return
        is_manual = event.value == _MANUAL
        self.query_one("#scope-profile-select", Select).set_class(not is_manual, "omega-hidden")
        self.query_one("#aggressiveness-select", Select).set_class(not is_manual, "omega-hidden")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.dismiss()
            return
        if event.button.id != "next":
            return

        target = self.query_one("#target-input", Input).value.strip()
        if not target:
            self.app.notify("Saisissez une cible.", severity="warning")
            return

        overrides: dict[str, int] = {}
        for input_id, field_name, label in _OVERRIDE_FIELDS:
            raw = self.query_one(f"#{input_id}", Input).value.strip()
            if raw:
                try:
                    overrides[field_name] = int(raw)
                except ValueError:
                    self.app.notify(f"Valeur invalide pour {label} : {raw!r}", severity="warning")
                    return

        auth_config_raw = self.query_one("#auth-config-input", Input).value.strip()
        auth_config_path = Path(auth_config_raw) if auth_config_raw else None
        verify_tls = self.query_one("#verify-tls-switch", Switch).value

        mode = str(self.query_one("#mode-select", Select).value)

        scan_runtime = self._scan_runtime_factory(auth_config_path)

        try:
            if mode == _MANUAL:
                scope_profile = ScopeProfileName(self.query_one("#scope-profile-select", Select).value)
                aggressiveness = AggressivenessLevel(
                    self.query_one("#aggressiveness-select", Select).value
                )
                prepared = prepare_scan(
                    raw_target=target,
                    auth_context=scan_runtime.auth_context,
                    aggressiveness=aggressiveness,
                    scope_profile=scope_profile,
                    overrides=overrides,
                    verify_tls=verify_tls,
                )
            else:
                prepared = prepare_scan(
                    raw_target=target,
                    auth_context=scan_runtime.auth_context,
                    preset=PresetName(mode),
                    overrides=overrides,
                    verify_tls=verify_tls,
                )
        except (UrlNormalizationError, ValidationError) as exc:
            self.app.notify(str(exc), severity="error")
            return

        self.app.push_screen(
            ScanReviewScreen(prepared=prepared, scan_runtime=scan_runtime, container=self._container)
        )
