# Copyright (c) 2026 kraynux - Licence MIT
"""Sous-commande `scan` (OMEGA-FUZZ_ARBORESCENCE.md §27) : assemble
`prepare_scan` (Phase 6) -> presentation de la configuration effective
-> (`--dry-run` : arret ici) -> `start_scan` (Phase 10a) -> presentation
des findings -> `build_scan_report` (Phase 10a) -> export via
`container.report_exporter`. Ne touche jamais `infrastructure`
directement : uniquement `application`/`domain` et les presenters
locaux, conforme a la Dependency Rule."""
from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from omega_fuzz.application.commands.prepare_scan import prepare_scan
from omega_fuzz.application.commands.start_scan import start_scan
from omega_fuzz.application.services.report_orchestrator import (
    build_scan_report,
    export_report,
    resolve_exports_dir,
)
from omega_fuzz.core.constants import CLI_EXIT_OK
from omega_fuzz.core.version import __version__
from omega_fuzz.domain.profiles.aggressiveness_level import AggressivenessLevel
from omega_fuzz.domain.profiles.preset import PresetName
from omega_fuzz.domain.profiles.scope_profile import ScopeProfileName
from omega_fuzz.interfaces.cli.presenters.configuration_presenter import render_configuration
from omega_fuzz.interfaces.cli.presenters.findings_presenter import render_findings

if TYPE_CHECKING:
    import argparse

    from omega_fuzz.app.container import Container, ScanRuntime

_OVERRIDE_FIELD_BY_ARG = {
    "max_duration": "max_duration_seconds",
    "max_requests": "max_total_requests",
    "max_tests": "max_tests",
    "max_concurrent": "max_concurrent_requests",
}


def _build_overrides(args: argparse.Namespace) -> dict[str, int]:
    overrides: dict[str, int] = {}
    for arg_name, field_name in _OVERRIDE_FIELD_BY_ARG.items():
        value = getattr(args, arg_name)
        if value is not None:
            overrides[field_name] = value
    return overrides


def run(container: Container, args: argparse.Namespace, scan_runtime: ScanRuntime) -> int:
    prepared = prepare_scan(
        raw_target=args.target,
        auth_context=scan_runtime.auth_context,
        preset=PresetName(args.preset) if args.preset else None,
        aggressiveness=AggressivenessLevel(args.aggressiveness) if args.aggressiveness else None,
        scope_profile=ScopeProfileName(args.scope_profile) if args.scope_profile else None,
        overrides=_build_overrides(args),
        verify_tls=not args.insecure_tls,
    )

    print(render_configuration(prepared))

    if args.dry_run:
        return CLI_EXIT_OK

    result = asyncio.run(
        start_scan(
            prepared=prepared,
            http_client=container.http_client,
            url_discoverer=container.url_discoverer,
            session_provider=scan_runtime.session_provider,
            response_analyzer=container.response_analyzer,
            security_headers_analyzer=container.security_headers_analyzer,
            test_plan_generator=container.test_plan_generator,
            scan_repository=container.scan_repository,
            finding_repository=container.finding_repository,
            confirmation_provider=scan_runtime.confirmation_provider,
            id_generator=container.id_generator,
            clock=container.clock,
            logger=container.logger,
        )
    )

    print(f"\nScan termine : {result.scan.status.value}\n")
    print(render_findings(result.findings))

    termination = result.scan.termination_reason
    assert termination is not None  # toujours renseigne en sortie de run_scan (Phase 10a)

    report = build_scan_report(
        scan=result.scan,
        target_url=prepared.entry_url.to_str(),
        version=__version__,
        configuration=prepared.configuration,
        termination=termination,
        tests=result.tests,
        findings=result.findings,
        statistics=result.statistics,
        catalog_versions=container.catalog_versions,
        verify_tls=prepared.verify_tls,
        now=container.clock.now(),
    )

    output_dir = args.output_dir or resolve_exports_dir(
        settings_store=container.settings_store, default_exports_dir=container.default_exports_dir
    )
    formats = ("json", "markdown", "html") if args.format == "all" else (args.format,)
    output_paths = export_report(
        report=report,
        formats=formats,
        output_dir=output_dir,
        report_exporter=container.report_exporter,
        theme_name=args.export_theme,
    )
    print()
    for format_name, output_path in zip(formats, output_paths, strict=True):
        print(f"Rapport {format_name} : {output_path}")

    return CLI_EXIT_OK
