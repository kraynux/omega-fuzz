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
from omega_fuzz.shared.i18n import _


def _tr(value: str | None) -> str | None:
    """R1 : texte enregistre en francais (titre, impact...) retraduit dans la langue de l'export."""
    return _(value) if value else value

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
        _("# Rapport {scanner_name}").format(scanner_name=header.scanner_name),
        "",
        _("- **Version** : {version}").format(version=header.version),
        _("- **Scan ID** : `{scan_id}`").format(scan_id=header.scan_id),
        _("- **Généré le** : {isoformat}").format(isoformat=header.generated_at.isoformat()),
        _("- **Cible** : {target_url}").format(target_url=header.target_url),
        _("- **Preset** : {preset}").format(preset=header.preset),
        _("- **Vérification TLS** : {value}").format(value=_("activée") if header.tls_verification_enabled else _("**DÉSACTIVÉE**")),
    ]
    if header.catalog_versions:
        versions = ", ".join(f"{name}={version}" for name, version in header.catalog_versions.items())
        lines.append(_("- **Versions des catalogues** : {versions}").format(versions=versions))
    if not header.tls_verification_enabled:
        lines += [
            "",
            (
                _("> **ATTENTION** : la vérification TLS était désactivée pour ce scan. Les "
                  "résultats peuvent avoir été obtenus via une connexion interceptée ou "
                  "usurpée.")
            ),
        ]
    return "\n".join(lines)


def _render_executive_summary(report: ReportModel) -> str:
    severities = findings_by_severity(report.findings)
    lines = [
        _("## Résumé exécutif"),
        "",
        (
            _("- **Résultat** : {count} finding(s) — {critical} critique(s), {high} élevé(s), "
              "{medium} moyen(s), {low} faible(s).").format(count=len(report.findings), critical=severities['critical'], high=severities['high'], medium=severities['medium'], low=severities['low'])
        ),
        _("- **Terminaison** : {value}").format(value=describe_termination(report.termination)),
    ]
    if report.configuration.warnings:
        lines.append(_("- **Avertissements** : {join}").format(join='; '.join(report.configuration.warnings)))
    return "\n".join(lines)


def _render_target_and_scan_id(report: ReportModel) -> str:
    return (
        _("## Cible et scan ID\n\n- **Cible** : {target_url}\n- **Scan ID** : `{scan_id}`").format(target_url=report.header.target_url, scan_id=report.header.scan_id)
    )


def _render_preset_and_profile(report: ReportModel) -> str:
    config = report.configuration
    lines = [
        _("## Preset, profils et surcharges"),
        "",
        _("- **Preset** : {preset}").format(preset=report.header.preset),
        _("- **Agressivité** : {value}").format(value=config.aggressiveness.value),
        _("- **Profil de scope** : {value}").format(value=config.scope_profile.value),
        _("- **Confirmation requise** : {value}").format(value=_("oui") if config.requires_confirmation else _("non")),
    ]
    if config.overrides:
        overrides_text = ", ".join(f"{name}={value}" for name, value in config.overrides.items())
        lines.append(_("- **Surcharges utilisateur** : {overrides_text}").format(overrides_text=overrides_text))
    else:
        lines.append(_("- **Surcharges utilisateur** : aucune"))
    return "\n".join(lines)


def _render_scope(report: ReportModel) -> str:
    scope = report.configuration.scope
    stats = report.statistics
    lines = [
        _("## Scope effectif et exclusions"),
        "",
        _("- **Host racine** : {root_host}").format(root_host=scope.root_host),
        _("- **Mode** : {value}").format(value=scope.mode.value),
        _("- **Schémas autorisés** : {join}").format(join=', '.join(sorted(scope.allowed_schemes))),
        _("- **Port** : {scope_port}").format(scope_port=scope.scope_port),
        _("- **Profondeur max** : {max_depth}").format(max_depth=scope.max_depth),
    ]
    if scope.allowed_subdomains:
        lines.append(_("- **Sous-domaines autorisés** : {join}").format(join=', '.join(sorted(scope.allowed_subdomains))))
    if scope.blocked_subdomains:
        lines.append(_("- **Sous-domaines bloqués** : {join}").format(join=', '.join(sorted(scope.blocked_subdomains))))
    if scope.allowed_paths:
        lines.append(_("- **Chemins autorisés** : {join}").format(join=', '.join(scope.allowed_paths)))
    if scope.blocked_paths:
        lines.append(_("- **Chemins bloqués** : {join}").format(join=', '.join(scope.blocked_paths)))
    lines += [
        "",
        _("### Découverte"),
        "",
        _("- URLs vues : {urls_seen}").format(urls_seen=stats.urls_seen),
        _("- URLs dans le scope : {urls_in_scope}").format(urls_in_scope=stats.urls_in_scope),
        _("- URLs hors scope : {urls_out_of_scope}").format(urls_out_of_scope=stats.urls_out_of_scope),
        _("- URLs au-delà de la profondeur : {urls_beyond_depth}").format(urls_beyond_depth=stats.urls_beyond_depth),
        "",
        _("### Redirections"),
        "",
        _("- Suivies : {redirects_followed}").format(redirects_followed=stats.redirects_followed),
        _("- Ignorées (externes) : {redirects_external_ignored}").format(redirects_external_ignored=stats.redirects_external_ignored),
        _("- Ignorées (hors scope) : {redirects_out_of_scope_ignored}").format(redirects_out_of_scope_ignored=stats.redirects_out_of_scope_ignored),
    ]
    return "\n".join(lines)


def _render_limits(report: ReportModel) -> str:
    limits = report.configuration.limits
    return (
        _("## Limites configurées\n\n- Durée max : {max_duration_seconds} s\n- Requêtes max : "
          "{max_total_requests}\n- Tests max : {max_tests}\n- Concurrence max : "
          "{max_concurrent_requests}").format(max_duration_seconds=limits.max_duration_seconds, max_total_requests=limits.max_total_requests, max_tests=limits.max_tests, max_concurrent_requests=limits.max_concurrent_requests)
    )


def _render_termination(report: ReportModel) -> str:
    return _("## Raison de terminaison\n\n{value}").format(value=describe_termination(report.termination))


def _render_requests(report: ReportModel) -> str:
    stats = report.statistics
    by_module = requests_by_module(report.tests)
    lines = [
        _("## Statistiques de requêtes"),
        "",
        (
            _("Ces compteurs correspondent à la découverte et aux tests de sécurité, pas à un "
              "test de charge.")
        ),
        "",
        _("- Total : {total_requests}").format(total_requests=stats.total_requests),
        _("- Découverte : {discovery_requests}").format(discovery_requests=stats.discovery_requests),
        _("- Test : {test_requests}").format(test_requests=stats.test_requests),
        "",
        _("### Par module"),
        "",
    ]
    if by_module:
        lines.extend(f"- {module} : {count}" for module, count in sorted(by_module.items()))
    else:
        lines.append(_("- (aucune requête de test)"))
    lines += [
        "",
        _("### Par statut"),
        "",
        f"- 2xx : {stats.status_2xx}",
        f"- 3xx : {stats.status_3xx}",
        f"- 4xx : {stats.status_4xx}",
        f"- 5xx : {stats.status_5xx}",
        _("- Timeouts : {timeouts}").format(timeouts=stats.timeouts),
        _("- Erreurs de transport : {transport_errors}").format(transport_errors=stats.transport_errors),
    ]
    return "\n".join(lines)


def _render_tests(report: ReportModel) -> str:
    stats = report.statistics
    by_type = count_tests_by_type(report.tests)
    lines = [
        _("## Statistiques de tests"),
        "",
        _("- Planifiés : {count}").format(count=len(report.tests)),
        _("- Exécutés : {tests_executed}").format(tests_executed=stats.tests_executed),
        _("- Terminés : {tests_completed}").format(tests_completed=stats.tests_completed),
        _("- Abandonnés : {tests_aborted}").format(tests_aborted=stats.tests_aborted),
        _("- Non concluants : {tests_inconclusive}").format(tests_inconclusive=stats.tests_inconclusive),
        "",
        _("### Par type"),
        "",
    ]
    if by_type:
        lines.extend(f"- {type_name} : {count}" for type_name, count in sorted(by_type.items()))
    else:
        lines.append(_("- (aucun test)"))
    return "\n".join(lines)


def _render_findings_by_severity(report: ReportModel) -> str:
    severities = findings_by_severity(report.findings)
    return (
        _("## Findings par sévérité\n\n- Total : {count}\n- Critique : {critical}\n- Élevé : "
          "{high}\n- Moyen : {medium}\n- Faible : {low}").format(count=len(report.findings), critical=severities['critical'], high=severities['high'], medium=severities['medium'], low=severities['low'])
    )


def _render_single_finding(finding: Finding) -> str:
    lines = [
        _("### {finding_id} — {title}").format(finding_id=finding.finding_id, title=_tr(finding.title)),
        "",
        _("**Statut** : `{value}`  ").format(value=finding.status.value),
        _("**Sévérité** : `{value}`  ").format(value=finding.severity.value),
        _("**Type** : `{type}`  ").format(type=finding.type),
        _("**Confiance** : `{value}`").format(value=finding.metadata.confidence.value),
        "",
        _("#### Cible"),
        "",
        _("- **URL** : `{url}`").format(url=finding.target.url),
        _("- **Endpoint** : `{endpoint}`").format(endpoint=finding.target.endpoint),
        _("- **Méthode** : `{method}`").format(method=finding.target.method),
        _("- **Paramètre** : `{value}`").format(value=finding.target.parameter or _("N/A")),
        "",
        _("#### Preuve"),
        "",
        _("**Comportement observé** : {observed_behavior}").format(observed_behavior=_tr(finding.evidence.observed_behavior)),
        "",
        _("**Extrait (expurgé)** : `{evidence_summary}`").format(evidence_summary=_tr(finding.evidence.evidence_summary)),
        "",
        _("- Test ID : `{test_id}`").format(test_id=finding.evidence.test_id),
        _("- Request ID : `{request_id}`").format(request_id=finding.evidence.request_id),
    ]
    if finding.severity_override is not None:
        lines += [
            "",
            (
                _("**Sévérité ajustée manuellement** : `{value}` -> `{value2}` — "
                  "{severity_override_reason}").format(value=finding.severity_auto.value, value2=finding.severity_override.value, severity_override_reason=finding.severity_override_reason)
            ),
        ]
    return "\n".join(lines)


def _render_finding_details(report: ReportModel) -> str:
    if not report.findings:
        return _("## Détail des findings\n\nAucun finding.")
    blocks = [_("## Détail des findings"), ""]
    blocks.extend(_render_single_finding(finding) for finding in report.findings)
    return "\n\n".join(blocks)


def _render_appendix(report: ReportModel) -> str:
    versions = ", ".join(
        f"{name}={version}" for name, version in report.header.catalog_versions.items()
    )
    return (
        _("## Annexes techniques\n\n- Versions des catalogues : {value}\n- Le détail brut "
          "complet (toutes les requêtes, tous les tests) est disponible dans l'export JSON "
          "correspondant.").format(value=versions or _("N/A"))
    )
