# Copyright (c) 2026 kraynux - Licence MIT
"""Tableau texte des findings en fin de scan (OMEGA-FUZZ_ARBORESCENCE.md
§27)."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

    from omega_fuzz.domain.findings.finding import Finding

_SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def render_findings(findings: Sequence[Finding]) -> str:
    if not findings:
        return "Aucun finding."

    ordered = sorted(findings, key=lambda finding: _SEVERITY_ORDER[finding.severity.value])
    lines = [f"{len(findings)} finding(s) :", ""]
    for finding in ordered:
        parameter = f" (parametre {finding.target.parameter})" if finding.target.parameter else ""
        lines.append(
            f"[{finding.severity.value.upper():>8}] {finding.type} sur "
            f"{finding.target.endpoint}{parameter} — {finding.title}"
        )
    return "\n".join(lines)
