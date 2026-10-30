# Copyright (c) 2026 kraynux - Licence MIT
"""Affiche la configuration effective d'un scan prepare
(OMEGA-FUZZ_ARBORESCENCE.md §27, OMEGA-FUZZ_SPECIFICATIONS.md §16.1 :
« l'interface doit afficher la cible normalisee, le scope effectif, les
exclusions effectives, le profil d'agressivite, les limites
effectives »). Reutilise a la fois par `--dry-run` et par l'ecran de
confirmation avant lancement."""
from __future__ import annotations

from typing import TYPE_CHECKING

from omega_fuzz.shared.i18n import _

if TYPE_CHECKING:
    from omega_fuzz.application.commands.prepare_scan import PreparedScan


def render_configuration(prepared: PreparedScan) -> str:
    configuration = prepared.configuration
    scope = configuration.scope
    limits = configuration.limits
    preset_label = configuration.preset.value if configuration.preset is not None else "custom"

    lines = [
        _("Cible            : {to_str}").format(to_str=prepared.entry_url.to_str()),
        _("Preset           : {preset_label}").format(preset_label=preset_label),
        _("Agressivité      : {value}").format(value=configuration.aggressiveness.value),
        _("Profil de scope  : {value}").format(value=configuration.scope_profile.value),
        _("Vérification TLS : {value}").format(value=_("activée") if prepared.verify_tls else _("DÉSACTIVÉE")),
        "",
        (
            _("Scope : {value}, host racine {root_host}, port {scope_port}, profondeur max "
              "{max_depth}").format(value=scope.mode.value, root_host=scope.root_host, scope_port=scope.scope_port, max_depth=scope.max_depth)
        ),
    ]
    if scope.blocked_subdomains:
        lines.append(_("  Sous-domaines bloqués : {join}").format(join=', '.join(sorted(scope.blocked_subdomains))))
    if scope.blocked_paths:
        lines.append(_("  Chemins bloqués       : {join}").format(join=', '.join(scope.blocked_paths)))

    lines.extend(
        [
            "",
            _("Limites :"),
            _("  Durée max        : {max_duration_seconds} s").format(max_duration_seconds=limits.max_duration_seconds),
            _("  Requêtes max     : {max_total_requests}").format(max_total_requests=limits.max_total_requests),
            _("  Tests max        : {max_tests}").format(max_tests=limits.max_tests),
            _("  Concurrence max  : {max_concurrent_requests}").format(max_concurrent_requests=limits.max_concurrent_requests),
        ]
    )

    if configuration.warnings:
        lines.append("")
        lines.append(_("Avertissements :"))
        lines.extend(f"  - {warning}" for warning in configuration.warnings)

    plan = prepared.plan
    lines.extend(
        [
            "",
            (
                _("Estimation : ~{estimated_tests} tests, ~{estimated_requests} requêtes, "
                  "profondeur ~{estimated_depth}").format(estimated_tests=plan.estimated_tests, estimated_requests=plan.estimated_requests, estimated_depth=plan.estimated_depth)
            ),
        ]
    )

    return "\n".join(lines)
