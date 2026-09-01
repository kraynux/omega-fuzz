# Copyright (c) 2026 kraynux - Licence MIT
"""Finding complet (OMEGA-FUZZ_SPECIFICATIONS.md §28.1). `severity` est
une propriete calculee (jamais stockee en double) : reflete
`severity_override` quand present, sinon `severity_auto` — evite toute
incoherence entre les deux. Un `severity_override` sans
`severity_override_reason` est bloquant (OMEGA-FUZZ_PLAN_DEV.md
Phase 8 : « tout override de severite possede une justification »)."""
from __future__ import annotations

from dataclasses import dataclass

from omega_fuzz.core.errors import ValidationError
from omega_fuzz.domain.findings.evidence import Evidence
from omega_fuzz.domain.findings.finding_metadata import FindingMetadata
from omega_fuzz.domain.findings.finding_status import FindingStatus
from omega_fuzz.domain.findings.finding_target import FindingTarget
from omega_fuzz.domain.findings.scoring import Scoring
from omega_fuzz.domain.findings.severity import Severity


@dataclass(frozen=True, slots=True)
class Finding:
    finding_id: str
    scan_id: str
    title: str
    type: str
    status: FindingStatus
    severity_auto: Severity
    target: FindingTarget
    evidence: Evidence
    scoring: Scoring
    metadata: FindingMetadata
    description: str = ""
    impact: str = ""
    recommendations: tuple[str, ...] = ()
    references: tuple[str, ...] = ()
    cwe: str | None = None
    owasp_category: str | None = None
    severity_override: Severity | None = None
    severity_override_reason: str | None = None

    def __post_init__(self) -> None:
        if self.severity_override is not None and not self.severity_override_reason:
            raise ValidationError(
                "severity_override necessite une severity_override_reason justifiee"
            )

    @property
    def severity(self) -> Severity:
        return self.severity_override if self.severity_override is not None else self.severity_auto
