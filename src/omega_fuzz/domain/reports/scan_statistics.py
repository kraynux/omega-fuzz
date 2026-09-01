# Copyright (c) 2026 kraynux - Licence MIT
"""Compteurs de scan (OMEGA-FUZZ_SPECIFICATIONS.md §13.1). Les compteurs
de decouverte/redirections ont leurs fonctions d'increment depuis la
Phase 4 (`domain.services.discovery_orchestrator`) ; ceux qui dependent
de modules pas encore construits (codes de statut par famille,
findings) restent a 0 par defaut sans fonction dediee — ajoutes quand
leurs evenements existeront reellement (Phase 7+). `record_request`/
`record_test_executed` suffisent a reproduire l'exemple multi-etapes du
§9.4."""
from __future__ import annotations

from dataclasses import dataclass, replace

from omega_fuzz.domain.requests.request_phase import RequestPhase


@dataclass(frozen=True, slots=True)
class ScanStatistics:
    total_requests: int = 0
    discovery_requests: int = 0
    test_requests: int = 0

    tests_planned: int = 0
    tests_executed: int = 0
    tests_completed: int = 0
    tests_aborted: int = 0
    tests_inconclusive: int = 0

    urls_seen: int = 0
    urls_in_scope: int = 0
    urls_out_of_scope: int = 0
    urls_beyond_depth: int = 0

    redirects_followed: int = 0
    redirects_external_ignored: int = 0
    redirects_out_of_scope_ignored: int = 0

    status_2xx: int = 0
    status_3xx: int = 0
    status_4xx: int = 0
    status_5xx: int = 0
    timeouts: int = 0
    transport_errors: int = 0

    findings_total: int = 0
    findings_critical: int = 0
    findings_high: int = 0
    findings_medium: int = 0
    findings_low: int = 0


def record_request(stats: ScanStatistics, *, phase: RequestPhase) -> ScanStatistics:
    """Toute requete HTTP effectivement emise compte toujours
    (OMEGA-FUZZ_SPECIFICATIONS.md §9.1/§9.3)."""
    return replace(
        stats,
        total_requests=stats.total_requests + 1,
        discovery_requests=stats.discovery_requests + (1 if phase is RequestPhase.DISCOVERY else 0),
        test_requests=stats.test_requests + (1 if phase is RequestPhase.TEST else 0),
    )


def record_test_executed(stats: ScanStatistics) -> ScanStatistics:
    """Un test est execute des qu'au moins une requete a ete emise dans
    son contexte — reste une unite metier unique quel que soit le nombre
    de requetes qu'il a emises (OMEGA-FUZZ_SPECIFICATIONS.md §9.4)."""
    return replace(stats, tests_executed=stats.tests_executed + 1)


def record_url_evaluated(
    stats: ScanStatistics, *, decision_accepted: bool, beyond_depth: bool
) -> ScanStatistics:
    """Toute URL rencontree est vue une fois (`urls_seen`), puis classee
    dans exactement une des trois categories restantes selon la decision
    de `scope_service.evaluate_scope` combinee a la verification de
    profondeur (OMEGA-FUZZ_PLAN_DEV.md Phase 4)."""
    if beyond_depth:
        return replace(stats, urls_seen=stats.urls_seen + 1, urls_beyond_depth=stats.urls_beyond_depth + 1)
    if decision_accepted:
        return replace(stats, urls_seen=stats.urls_seen + 1, urls_in_scope=stats.urls_in_scope + 1)
    return replace(stats, urls_seen=stats.urls_seen + 1, urls_out_of_scope=stats.urls_out_of_scope + 1)


def record_redirect_followed(stats: ScanStatistics) -> ScanStatistics:
    return replace(stats, redirects_followed=stats.redirects_followed + 1)


def record_redirect_external_ignored(stats: ScanStatistics) -> ScanStatistics:
    return replace(stats, redirects_external_ignored=stats.redirects_external_ignored + 1)


def record_redirect_out_of_scope_ignored(stats: ScanStatistics) -> ScanStatistics:
    return replace(
        stats, redirects_out_of_scope_ignored=stats.redirects_out_of_scope_ignored + 1
    )


def record_observation_found(stats: ScanStatistics) -> ScanStatistics:
    """Une observation suspecte a ete detectee (Phase 7b). Seul
    `findings_total` est incremente ici — `findings_critical`/`high`/
    `medium`/`low` dependent du scoring de severite, construit en
    Phase 8, pas encore disponible."""
    return replace(stats, findings_total=stats.findings_total + 1)


def record_response_status(
    stats: ScanStatistics, *, status_code: int, fetch_error: str | None = None
) -> ScanStatistics:
    """Repartition par statut HTTP, necessaire a la section `Requests`
    obligatoire du rapport (OMEGA-FUZZ_SPECIFICATIONS.md §27.6). Une
    erreur reseau dont le message contient "timeout" est classee dans
    `timeouts`, les autres dans `transport_errors` (heuristique : le
    port `HttpClient` ne distingue pas ces deux cas explicitement,
    seulement un `fetch_error: str | None` libre)."""
    if fetch_error is not None:
        if "timeout" in fetch_error.lower():
            return replace(stats, timeouts=stats.timeouts + 1)
        return replace(stats, transport_errors=stats.transport_errors + 1)
    if 200 <= status_code < 300:
        return replace(stats, status_2xx=stats.status_2xx + 1)
    if 300 <= status_code < 400:
        return replace(stats, status_3xx=stats.status_3xx + 1)
    if 400 <= status_code < 500:
        return replace(stats, status_4xx=stats.status_4xx + 1)
    if status_code >= 500:
        return replace(stats, status_5xx=stats.status_5xx + 1)
    return replace(stats, transport_errors=stats.transport_errors + 1)
