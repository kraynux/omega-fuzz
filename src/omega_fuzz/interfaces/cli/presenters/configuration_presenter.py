# Copyright (c) 2026 kraynux - Licence MIT
"""Affiche la configuration effective d'un scan prepare
(OMEGA-FUZZ_ARBORESCENCE.md §27, OMEGA-FUZZ_SPECIFICATIONS.md §16.1 :
« l'interface doit afficher la cible normalisee, le scope effectif, les
exclusions effectives, le profil d'agressivite, les limites
effectives »). Reutilise a la fois par `--dry-run` et par l'ecran de
confirmation avant lancement."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from omega_fuzz.application.commands.prepare_scan import PreparedScan


def render_configuration(prepared: PreparedScan) -> str:
    configuration = prepared.configuration
    scope = configuration.scope
    limits = configuration.limits
    preset_label = configuration.preset.value if configuration.preset is not None else "custom"

    lines = [
        f"Cible            : {prepared.entry_url.to_str()}",
        f"Preset           : {preset_label}",
        f"Agressivite      : {configuration.aggressiveness.value}",
        f"Profil de scope  : {configuration.scope_profile.value}",
        f"Verification TLS : {'activee' if prepared.verify_tls else 'DESACTIVEE'}",
        "",
        (
            f"Scope : {scope.mode.value}, host racine {scope.root_host}, port {scope.scope_port}, "
            f"profondeur max {scope.max_depth}"
        ),
    ]
    if scope.blocked_subdomains:
        lines.append(f"  Sous-domaines bloques : {', '.join(sorted(scope.blocked_subdomains))}")
    if scope.blocked_paths:
        lines.append(f"  Chemins bloques       : {', '.join(scope.blocked_paths)}")

    lines.extend(
        [
            "",
            "Limites :",
            f"  Duree max        : {limits.max_duration_seconds} s",
            f"  Requetes max     : {limits.max_total_requests}",
            f"  Tests max        : {limits.max_tests}",
            f"  Concurrence max  : {limits.max_concurrent_requests}",
        ]
    )

    if configuration.warnings:
        lines.append("")
        lines.append("Avertissements :")
        lines.extend(f"  - {warning}" for warning in configuration.warnings)

    plan = prepared.plan
    lines.extend(
        [
            "",
            (
                f"Estimation : ~{plan.estimated_tests} tests, ~{plan.estimated_requests} "
                f"requetes, profondeur ~{plan.estimated_depth}"
            ),
        ]
    )

    return "\n".join(lines)
