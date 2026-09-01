# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

import inspect

import pytest

from omega_fuzz.application.commands import prepare_scan as prepare_scan_module
from omega_fuzz.application.commands.prepare_scan import prepare_scan
from omega_fuzz.application.exceptions import IncompleteScanConfigurationError
from omega_fuzz.domain.auth.auth_context import AuthContext, AuthMode
from omega_fuzz.domain.profiles.aggressiveness_level import AggressivenessLevel
from omega_fuzz.domain.profiles.preset import PresetName
from omega_fuzz.domain.profiles.scope_profile import ScopeProfileName
from omega_fuzz.domain.targets.url import UrlNormalizationError

_NONE_AUTH = AuthContext(mode=AuthMode.NONE)


def test_prepare_scan_with_preset() -> None:
    prepared = prepare_scan(
        raw_target="https://example.com/", auth_context=_NONE_AUTH, preset=PresetName.PROD_SAFE
    )
    assert prepared.target_id == "example_root"
    assert prepared.configuration.preset is PresetName.PROD_SAFE
    assert prepared.plan.target_url == "https://example.com/"


def test_prepare_scan_with_manual_profile() -> None:
    prepared = prepare_scan(
        raw_target="https://example.com/",
        auth_context=_NONE_AUTH,
        aggressiveness=AggressivenessLevel.STANDARD,
        scope_profile=ScopeProfileName.STANDARD,
    )
    assert prepared.configuration.preset is None
    assert prepared.configuration.aggressiveness is AggressivenessLevel.STANDARD


def test_prepare_scan_without_preset_or_manual_combo_raises() -> None:
    with pytest.raises(IncompleteScanConfigurationError):
        prepare_scan(raw_target="https://example.com/", auth_context=_NONE_AUTH)


def test_prepare_scan_with_partial_manual_combo_raises() -> None:
    with pytest.raises(IncompleteScanConfigurationError):
        prepare_scan(
            raw_target="https://example.com/",
            auth_context=_NONE_AUTH,
            aggressiveness=AggressivenessLevel.STANDARD,
        )


def test_prepare_scan_with_invalid_target_propagates_normalization_error() -> None:
    with pytest.raises(UrlNormalizationError):
        prepare_scan(
            raw_target="not a url", auth_context=_NONE_AUTH, preset=PresetName.PROD_SAFE
        )


def test_lab_extreme_preset_makes_confirmation_clearly_visible() -> None:
    prepared = prepare_scan(
        raw_target="https://example.com/",
        auth_context=_NONE_AUTH,
        preset=PresetName.LAB_EXTREME,
    )
    assert prepared.configuration.requires_confirmation is True


def test_verify_tls_false_forces_confirmation_even_on_safe_preset() -> None:
    """OMEGA-FUZZ_SPECIFICATIONS.md §16 : `verify_tls=false` est traite
    comme une action a risque au meme titre qu'un profil violent,
    independamment du profil reellement selectionne — meme prod-safe
    doit declencher une confirmation."""
    prepared = prepare_scan(
        raw_target="https://example.com/",
        auth_context=_NONE_AUTH,
        preset=PresetName.PROD_SAFE,
        verify_tls=False,
    )
    assert prepared.verify_tls is False
    assert prepared.configuration.requires_confirmation is True
    assert any("tls" in warning.lower() for warning in prepared.configuration.warnings)


def test_verify_tls_true_by_default() -> None:
    prepared = prepare_scan(
        raw_target="https://example.com/", auth_context=_NONE_AUTH, preset=PresetName.PROD_SAFE
    )
    assert prepared.verify_tls is True
    assert prepared.configuration.requires_confirmation is False


def test_prepare_scan_never_imports_http_client() -> None:
    """Garantie structurelle du critere « --dry-run n'emet aucune
    requete » : prepare_scan ne depend d'aucun port/adaptateur HTTP.
    Seules les lignes `import`/`from ... import` comptent (le texte de
    la docstring du module mentionne HttpClient en prose, sans
    l'importer)."""
    import_lines = [
        line
        for line in inspect.getsource(prepare_scan_module).splitlines()
        if line.strip().startswith(("import ", "from "))
    ]
    assert not any("http_client" in line.lower() for line in import_lines)
