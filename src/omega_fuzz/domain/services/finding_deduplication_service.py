# Copyright (c) 2026 kraynux - Licence MIT
"""Deduplication des findings (OMEGA-FUZZ_ARBORESCENCE.md §14 :
« regrouper les anomalies identiques ou equivalentes, conserver la
meilleure preuve »). Deux findings sont equivalents s'ils partagent le
meme `(type, target.endpoint, target.parameter)` — meme nature de
probleme sur le meme point d'entree. La meilleure preuve est retenue
via `confidence_strength` (omega_lib.core.confidence), puis par
`raw_score` en cas d'egalite."""
from __future__ import annotations

from collections.abc import Sequence

from omega_lib.core.confidence import confidence_strength

from omega_fuzz.domain.findings.finding import Finding


def _equivalence_key(finding: Finding) -> tuple[str, str, str | None]:
    return finding.type, finding.target.endpoint, finding.target.parameter


def _is_better(candidate: Finding, current_best: Finding) -> bool:
    candidate_strength = confidence_strength(candidate.metadata.confidence)
    best_strength = confidence_strength(current_best.metadata.confidence)
    if candidate_strength != best_strength:
        return candidate_strength > best_strength
    return candidate.scoring.raw_score > current_best.scoring.raw_score


def deduplicate_findings(findings: Sequence[Finding]) -> tuple[Finding, ...]:
    best_by_key: dict[tuple[str, str, str | None], Finding] = {}
    order: list[tuple[str, str, str | None]] = []

    for finding in findings:
        key = _equivalence_key(finding)
        if key not in best_by_key:
            best_by_key[key] = finding
            order.append(key)
        elif _is_better(finding, best_by_key[key]):
            best_by_key[key] = finding

    return tuple(best_by_key[key] for key in order)
