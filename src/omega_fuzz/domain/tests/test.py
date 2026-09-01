# Copyright (c) 2026 kraynux - Licence MIT
"""Unite logique de test de securite (OMEGA-FUZZ_SPECIFICATIONS.md §9.2,
§10). `severity_hint` reste une chaine libre ("critical"/"high"/
"medium"/"low") plutot qu'un enum `Severity` : ce type appartient a
`domain.findings`, qui n'existe pas avant la Phase 8 — pas de dependance
anticipee sur un module futur."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from omega_fuzz.domain.tests.test_result import TestResult
from omega_fuzz.domain.tests.test_status import TestStatus
from omega_fuzz.domain.tests.test_type import TestType


@dataclass(frozen=True, slots=True)
class TestTarget:
    url: str
    method: str
    endpoint: str
    parameters: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class Test:
    test_id: str
    type: TestType
    subtype: str
    module: str
    target: TestTarget
    description: str
    created_at: datetime
    severity_hint: str | None = None
    status: TestStatus = TestStatus.PLANNED
    result: TestResult = TestResult.INCONCLUSIVE
    requests_count: int = 0
    errors_count: int = 0
    findings_count: int = 0
    started_at: datetime | None = None
    completed_at: datetime | None = None
