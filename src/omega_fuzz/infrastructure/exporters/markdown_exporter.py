# Copyright (c) 2026 kraynux - Licence MIT
"""Implemente ports/report_exporter.py::ReportExporter pour le format
Markdown (OMEGA-FUZZ_SPECIFICATIONS.md §27, OMEGA-FUZZ_PLAN_DEV.md
Phase 9 — les 12 sections). Pas de moteur de template : f-strings
simples, coherent avec "lecture, documentation et versionnement",
aucune dependance nouvelle. Le resume executif est genere a partir des
donnees (jamais de texte fige)."""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from omega_fuzz.domain.reports.report_model import (
    ReportModel,
    count_tests_by_type,
    findings_by_severity,
    requests_by_module,
)
from omega_fuzz.domain.reports.termination import describe_termination

if TYPE_CHECKING:
    from omega_fuzz.domain.findings.finding import Finding
    from omega_fuzz.domain.reports.report_model import ReportHeader


class MarkdownReportExporter:
    """Implemente ports/report_exporter.py::ReportExporter."""

    def export(
        self,
        *,
        report: ReportModel,
        format_name: str,
        output_path: Path,
        theme_name: str | None = None,
    ) -> None:
        if format_name != "markdown":
            raise ValueError(f"format non supporte par MarkdownReportExporter : {format_name!r}")
        output_path.write_text(_render(report), encoding="utf-8")


def _render(report: ReportModel) -> str:
    sections = [
        _render_header(report.header),
        _render_executive_summary(report),
        _render_target_and_scan_id(report),
        _render_preset_and_profile(report),
        _render_scope(report),
        _render_limits(report),
        _render_termination(report),
        _render_requests(report),
        _render_tests(report),
        _render_findings_by_severity(report),
        _render_finding_details(report),
        _render_appendix(report),
    ]
    return "\n\n".join(sections) + "\n"


def _render_header(header: ReportHeader) -> str:
    lines = [
        f"# Rapport {header.scanner_name}",
        "",
        f"- **Version** : {header.version}",
        f"- **Scan ID** : `{header.scan_id}`",
        f"- **Genere le** : {header.generated_at.isoformat()}",
        f"- **Cible** : {header.target_url}",
        f"- **Preset** : {header.preset}",
        f"- **Verification TLS** : {'activee' if header.tls_verification_enabled else '**DESACTIVEE**'}",
    ]
    if header.catalog_versions:
        versions = ", ".join(f"{name}={version}" for name, version in header.catalog_versions.items())
        lines.append(f"- **Versions des catalogues** : {versions}")
    if not header.tls_verification_enabled:
        lines += [
            "",
            (
                "> **ATTENTION** : la verification TLS etait desactivee pour ce scan. Les "
                "resultats peuvent avoir ete obtenus via une connexion interceptee ou usurpee."
            ),
        ]
    return "\n".join(lines)


def _render_executive_summary(report: ReportModel) -> str:
    severities = findings_by_severity(report.findings)
    lines = [
        "## Resume executif",
        "",
        (
            f"- **Resultat** : {len(report.findings)} finding(s) — "
            f"{severities['critical']} critique(s), {severities['high']} eleve(s), "
            f"{severities['medium']} moyen(s), {severities['low']} faible(s)."
        ),
        f"- **Terminaison** : {describe_termination(report.termination)}",
    ]
    if report.configuration.warnings:
        lines.append(f"- **Avertissements** : {'; '.join(report.configuration.warnings)}")
    return "\n".join(lines)


def _render_target_and_scan_id(report: ReportModel) -> str:
    return (
        "## Cible et scan ID\n\n"
        f"- **Cible** : {report.header.target_url}\n"
        f"- **Scan ID** : `{report.header.scan_id}`"
    )


def _render_preset_and_profile(report: ReportModel) -> str:
    config = report.configuration
    lines = [
        "## Preset, profils et surcharges",
        "",
        f"- **Preset** : {report.header.preset}",
        f"- **Agressivite** : {config.aggressiveness.value}",
        f"- **Profil de scope** : {config.scope_profile.value}",
        f"- **Confirmation requise** : {'oui' if config.requires_confirmation else 'non'}",
    ]
    if config.overrides:
        overrides_text = ", ".join(f"{name}={value}" for name, value in config.overrides.items())
        lines.append(f"- **Surcharges utilisateur** : {overrides_text}")
    else:
        lines.append("- **Surcharges utilisateur** : aucune")
    return "\n".join(lines)


def _render_scope(report: ReportModel) -> str:
    scope = report.configuration.scope
    stats = report.statistics
    lines = [
        "## Scope effectif et exclusions",
        "",
        f"- **Host racine** : {scope.root_host}",
        f"- **Mode** : {scope.mode.value}",
        f"- **Schemas autorises** : {', '.join(sorted(scope.allowed_schemes))}",
        f"- **Port** : {scope.scope_port}",
        f"- **Profondeur max** : {scope.max_depth}",
    ]
    if scope.allowed_subdomains:
        lines.append(f"- **Sous-domaines autorises** : {', '.join(sorted(scope.allowed_subdomains))}")
    if scope.blocked_subdomains:
        lines.append(f"- **Sous-domaines bloques** : {', '.join(sorted(scope.blocked_subdomains))}")
    if scope.allowed_paths:
        lines.append(f"- **Chemins autorises** : {', '.join(scope.allowed_paths)}")
    if scope.blocked_paths:
        lines.append(f"- **Chemins bloques** : {', '.join(scope.blocked_paths)}")
    lines += [
        "",
        "### Decouverte",
        "",
        f"- URLs vues : {stats.urls_seen}",
        f"- URLs dans le scope : {stats.urls_in_scope}",
        f"- URLs hors scope : {stats.urls_out_of_scope}",
        f"- URLs au-dela de la profondeur : {stats.urls_beyond_depth}",
        "",
        "### Redirections",
        "",
        f"- Suivies : {stats.redirects_followed}",
        f"- Ignorees (externes) : {stats.redirects_external_ignored}",
        f"- Ignorees (hors scope) : {stats.redirects_out_of_scope_ignored}",
    ]
    return "\n".join(lines)


def _render_limits(report: ReportModel) -> str:
    limits = report.configuration.limits
    return (
        "## Limites configurees\n\n"
        f"- Duree max : {limits.max_duration_seconds} s\n"
        f"- Requetes max : {limits.max_total_requests}\n"
        f"- Tests max : {limits.max_tests}\n"
        f"- Concurrence max : {limits.max_concurrent_requests}"
    )


def _render_termination(report: ReportModel) -> str:
    return f"## Raison de terminaison\n\n{describe_termination(report.termination)}"


def _render_requests(report: ReportModel) -> str:
    stats = report.statistics
    by_module = requests_by_module(report.tests)
    lines = [
        "## Statistiques de requetes",
        "",
        (
            "Ces compteurs correspondent a la decouverte et aux tests de securite, pas a un "
            "test de charge."
        ),
        "",
        f"- Total : {stats.total_requests}",
        f"- Decouverte : {stats.discovery_requests}",
        f"- Test : {stats.test_requests}",
        "",
        "### Par module",
        "",
    ]
    if by_module:
        lines.extend(f"- {module} : {count}" for module, count in sorted(by_module.items()))
    else:
        lines.append("- (aucune requete de test)")
    lines += [
        "",
        "### Par statut",
        "",
        f"- 2xx : {stats.status_2xx}",
        f"- 3xx : {stats.status_3xx}",
        f"- 4xx : {stats.status_4xx}",
        f"- 5xx : {stats.status_5xx}",
        f"- Timeouts : {stats.timeouts}",
        f"- Erreurs de transport : {stats.transport_errors}",
    ]
    return "\n".join(lines)


def _render_tests(report: ReportModel) -> str:
    stats = report.statistics
    by_type = count_tests_by_type(report.tests)
    lines = [
        "## Statistiques de tests",
        "",
        f"- Planifies : {len(report.tests)}",
        f"- Executes : {stats.tests_executed}",
        f"- Termines : {stats.tests_completed}",
        f"- Abandonnes : {stats.tests_aborted}",
        f"- Non concluants : {stats.tests_inconclusive}",
        "",
        "### Par type",
        "",
    ]
    if by_type:
        lines.extend(f"- {type_name} : {count}" for type_name, count in sorted(by_type.items()))
    else:
        lines.append("- (aucun test)")
    return "\n".join(lines)


def _render_findings_by_severity(report: ReportModel) -> str:
    severities = findings_by_severity(report.findings)
    return (
        "## Findings par severite\n\n"
        f"- Total : {len(report.findings)}\n"
        f"- Critique : {severities['critical']}\n"
        f"- Eleve : {severities['high']}\n"
        f"- Moyen : {severities['medium']}\n"
        f"- Faible : {severities['low']}"
    )


def _render_single_finding(finding: Finding) -> str:
    lines = [
        f"### {finding.finding_id} — {finding.title}",
        "",
        f"**Statut** : `{finding.status.value}`  ",
        f"**Severite** : `{finding.severity.value}`  ",
        f"**Type** : `{finding.type}`  ",
        f"**Confiance** : `{finding.metadata.confidence.value}`",
        "",
        "#### Cible",
        "",
        f"- **URL** : `{finding.target.url}`",
        f"- **Endpoint** : `{finding.target.endpoint}`",
        f"- **Methode** : `{finding.target.method}`",
        f"- **Parametre** : `{finding.target.parameter or 'N/A'}`",
        "",
        "#### Preuve",
        "",
        f"**Comportement observe** : {finding.evidence.observed_behavior}",
        "",
        f"**Extrait (expurge)** : `{finding.evidence.evidence_summary}`",
        "",
        f"- Test ID : `{finding.evidence.test_id}`",
        f"- Request ID : `{finding.evidence.request_id}`",
    ]
    if finding.severity_override is not None:
        lines += [
            "",
            (
                f"**Severite ajustee manuellement** : `{finding.severity_auto.value}` -> "
                f"`{finding.severity_override.value}` — {finding.severity_override_reason}"
            ),
        ]
    return "\n".join(lines)


def _render_finding_details(report: ReportModel) -> str:
    if not report.findings:
        return "## Detail des findings\n\nAucun finding."
    blocks = ["## Detail des findings", ""]
    blocks.extend(_render_single_finding(finding) for finding in report.findings)
    return "\n\n".join(blocks)


def _render_appendix(report: ReportModel) -> str:
    versions = ", ".join(
        f"{name}={version}" for name, version in report.header.catalog_versions.items()
    )
    return (
        "## Annexes techniques\n\n"
        f"- Versions des catalogues : {versions or 'N/A'}\n"
        "- Le detail brut complet (toutes les requetes, tous les tests) est disponible "
        "dans l'export JSON correspondant."
    )
