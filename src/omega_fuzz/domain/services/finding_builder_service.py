# Copyright (c) 2026 kraynux - Licence MIT
"""Construction de `Finding` a partir d'une `Observation` deja produite
par un analyseur (Phase 7b/7c) et du `Test` qui l'a generee
(OMEGA-FUZZ_PLAN_DEV.md Phase 8 : « un finding peut etre lie a un
test_id et un request_id »). `cwe`/`owasp_category`/`recommendations`/
`references`/`impact` restent vides — un mapping pattern-precis
necessite un humain ou une table plus fine que ce que `Observation.kind`
permet de distinguer automatiquement, pas de contenu fabrique sans
base reelle."""
from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

from omega_fuzz.domain.findings.evidence import Evidence
from omega_fuzz.domain.findings.finding import Finding
from omega_fuzz.domain.findings.finding_id import build_finding_id
from omega_fuzz.domain.findings.finding_metadata import FindingMetadata
from omega_fuzz.domain.findings.finding_status import FindingStatus
from omega_fuzz.domain.findings.finding_target import FindingTarget
from omega_fuzz.domain.findings.observation import Observation
from omega_fuzz.domain.services.finding_deduplication_service import deduplicate_findings
from omega_fuzz.domain.services.severity_service import (
    map_score_to_severity,
    score_for_observation_kind,
)
from omega_fuzz.domain.tests.test import Test


def build_finding(
    *,
    scan_id: str,
    test: Test,
    observation: Observation,
    target_short: str,
    sequence: int,
    now: datetime,
) -> Finding:
    scoring = score_for_observation_kind(observation.kind)
    severity_auto = map_score_to_severity(scoring.raw_score)
    parameter = test.target.parameters[0] if test.target.parameters else None

    return Finding(
        finding_id=build_finding_id(module=test.module, target_short=target_short, sequence=sequence),
        scan_id=scan_id,
        title=f"{observation.kind.replace('_', ' ').capitalize()} sur {test.target.endpoint}",
        type=test.subtype,
        status=FindingStatus.SUSPECTED,
        severity_auto=severity_auto,
        target=FindingTarget(
            url=test.target.url,
            endpoint=test.target.endpoint,
            method=test.target.method,
            parameter=parameter,
        ),
        evidence=Evidence(
            request_id=observation.request_id,
            test_id=test.test_id,
            observed_behavior=observation.description,
            evidence_summary=observation.evidence_summary,
        ),
        scoring=scoring,
        metadata=FindingMetadata(module=test.module, timestamp=now, confidence=observation.confidence),
        description=observation.description,
    )


def build_findings_from_observations(
    *,
    scan_id: str,
    test: Test,
    observations: Sequence[Observation],
    target_short: str,
    now: datetime,
) -> tuple[Finding, ...]:
    findings = tuple(
        build_finding(
            scan_id=scan_id,
            test=test,
            observation=observation,
            target_short=target_short,
            sequence=index,
            now=now,
        )
        for index, observation in enumerate(observations, start=1)
    )
    return deduplicate_findings(findings)
