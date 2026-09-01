# Copyright (c) 2026 kraynux - Licence MIT
"""Modele de rapport commun (OMEGA-FUZZ_SPECIFICATIONS.md §27,
OMEGA-FUZZ_PLAN_DEV.md Phase 9 : « les trois formats reposent sur un
modele de rapport commun »). Reutilise integralement les types deja
construits (Phases 2/3/5/8) — pas de duplication. Les repartitions
`by_module`/`by_type`/`by_severity` (§27.6/§27.7/§27.8) ne sont jamais
stockees : calculees a la demande a partir de `tests`/`findings`, un
seul endroit de verite."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from omega_fuzz.domain.findings.finding import Finding
    from omega_fuzz.domain.profiles.effective_configuration import EffectiveConfiguration
    from omega_fuzz.domain.reports.scan_statistics import ScanStatistics
    from omega_fuzz.domain.reports.termination import TerminationReason
    from omega_fuzz.domain.tests.test import Test

_SCANNER_NAME = "OMEGA-FUZZ"


@dataclass(frozen=True, slots=True)
class ReportHeader:
    scanner_name: str
    version: str
    scan_id: str
    generated_at: datetime
    target_url: str
    preset: str
    tls_verification_enabled: bool
    catalog_versions: Mapping[str, str] = field(default_factory=dict)


def build_report_header(
    *,
    scan_id: str,
    version: str,
    target_url: str,
    configuration: EffectiveConfiguration,
    catalog_versions: Mapping[str, str],
    verify_tls: bool,
    now: datetime,
) -> ReportHeader:
    """`preset` vaut le nom du preset resolu, ou "custom" si le scan a
    ete configure manuellement (agressivite + scope profile, sans
    preset — OMEGA-FUZZ_SPECIFICATIONS.md §27.2)."""
    preset_label = configuration.preset.value if configuration.preset is not None else "custom"
    return ReportHeader(
        scanner_name=_SCANNER_NAME,
        version=version,
        scan_id=scan_id,
        generated_at=now,
        target_url=target_url,
        preset=preset_label,
        tls_verification_enabled=verify_tls,
        catalog_versions=dict(catalog_versions),
    )


@dataclass(frozen=True, slots=True)
class ReportModel:
    header: ReportHeader
    configuration: EffectiveConfiguration
    termination: TerminationReason
    statistics: ScanStatistics
    tests: tuple[Test, ...] = ()
    findings: tuple[Finding, ...] = ()


def requests_by_module(tests: Sequence[Test]) -> dict[str, int]:
    """OMEGA-FUZZ_SPECIFICATIONS.md §27.6 : repartition des requetes de
    test par module (crawler/fuzzer_http/signatures/logic...)."""
    result: dict[str, int] = {}
    for test in tests:
        result[test.module] = result.get(test.module, 0) + test.requests_count
    return result


def count_tests_by_type(tests: Sequence[Test]) -> dict[str, int]:
    """OMEGA-FUZZ_SPECIFICATIONS.md §27.7. Nomme `count_tests_by_type`
    (pas `tests_by_type`) : un nom de fonction commencant par "tests"
    est collecte par erreur par pytest comme test lorsqu'il est importe
    dans un module de test (meme categorie de piege que `Test`/
    `TestStatus`, deja rencontree Phase 2 — `python_classes = []` ne
    couvre que les classes, pas les fonctions)."""
    result: dict[str, int] = {}
    for test in tests:
        result[test.type.value] = result.get(test.type.value, 0) + 1
    return result


def findings_by_severity(findings: Sequence[Finding]) -> dict[str, int]:
    """OMEGA-FUZZ_SPECIFICATIONS.md §27.8."""
    result = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for finding in findings:
        result[finding.severity.value] += 1
    return result
