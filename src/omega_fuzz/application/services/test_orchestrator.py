# Copyright (c) 2026 kraynux - Licence MIT
"""Execute un `Test` deja construit (par un fuzzer/signature/logic_test
de `plugins/`) contre `HttpClient`, en respectant le budget
(OMEGA-FUZZ_PLAN_DEV.md Phase 7, « principes de module »). Generique :
ne connait aucun module par son nom — recoit un `Test`/`Sequence[
ScanRequest]` deja prets, quelle que soit leur origine (7a fuzzers, 7b
signatures, 7c logic_tests plus tard).

Porte aussi la logique de mise a jour du `Test` apres execution
(equivalent de `plugins/fuzzers/common/fuzz_result_mapper.py` de
OMEGA-FUZZ_ARBORESCENCE.md §30, absorbee ici plutot que dans `plugins/`
— la Dependency Rule interdit a `application` d'importer `plugins`, donc
le mapping des resultats HTTP reels, qui n'existe qu'apres l'emission,
ne peut vivre que du cote de l'appelant reel de `HttpClient`)."""
from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from typing import TYPE_CHECKING

from omega_fuzz.domain.reports.scan_statistics import (
    ScanStatistics,
    record_observation_found,
    record_request,
    record_response_status,
    record_test_executed,
)
from omega_fuzz.domain.requests.request_phase import RequestPhase
from omega_fuzz.domain.services.limit_service import can_reserve_request
from omega_fuzz.domain.tests.test_result import TestResult
from omega_fuzz.domain.tests.test_status import TestStatus

if TYPE_CHECKING:
    from collections.abc import Sequence

    from omega_fuzz.domain.findings.observation import Observation
    from omega_fuzz.domain.profiles.limits import Limits
    from omega_fuzz.domain.requests.scan_request import ScanRequest
    from omega_fuzz.domain.tests.test import Test
    from omega_fuzz.ports.access_control_analyzer import AccessControlAnalyzer
    from omega_fuzz.ports.clock import Clock
    from omega_fuzz.ports.http_client import HttpClient
    from omega_fuzz.ports.logger import Logger
    from omega_fuzz.ports.response_analyzer import ResponseAnalyzer
    from omega_fuzz.ports.session_provider import SessionProvider


async def run_test(
    *,
    http_client: HttpClient,
    test: Test,
    requests: Sequence[ScanRequest],
    limits: Limits,
    clock: Clock,
    logger: Logger,
    stats: ScanStatistics | None = None,
    verify_tls: bool = True,
) -> tuple[Test, ScanStatistics]:
    stats = stats if stats is not None else ScanStatistics()
    started_at: datetime = clock.now()

    executed_count = 0
    error_count = 0
    for request in requests:
        if not can_reserve_request(stats=stats, limits=limits):
            logger.warning("test_budget_exhausted", test_id=test.test_id)
            break

        body = request.body if isinstance(request.body, bytes) else None
        response = await http_client.send(
            method=request.method,
            url=request.url,
            headers=dict(request.headers),
            body=body,
            max_response_body_size=limits.max_response_body_size,
            verify_tls=verify_tls,
        )
        stats = record_request(stats, phase=RequestPhase.TEST)
        stats = record_response_status(
            stats, status_code=response.status_code, fetch_error=response.fetch_error
        )
        executed_count += 1
        if response.fetch_error is not None or response.status_code >= 500:
            error_count += 1

    if executed_count > 0:
        stats = record_test_executed(stats)

    completed_fully = executed_count == len(requests)
    updated_test = replace(
        test,
        status=TestStatus.COMPLETED if completed_fully else TestStatus.ABORTED,
        requests_count=executed_count,
        errors_count=error_count,
        started_at=started_at,
        completed_at=clock.now(),
    )
    return updated_test, stats


async def run_signature_test(
    *,
    http_client: HttpClient,
    response_analyzer: ResponseAnalyzer,
    test: Test,
    requests: Sequence[ScanRequest],
    limits: Limits,
    clock: Clock,
    logger: Logger,
    stats: ScanStatistics | None = None,
    verify_tls: bool = True,
) -> tuple[Test, ScanStatistics, tuple[Observation, ...]]:
    """Variante de `run_test` (Phase 7b) qui appelle en plus
    `ResponseAnalyzer` sur chaque reponse et fixe `Test.result` en
    consequence. `Test.result` reste `INCONCLUSIVE` si aucune requete
    n'a pu aboutir (budget epuise avant la premiere emission)."""
    stats = stats if stats is not None else ScanStatistics()
    started_at: datetime = clock.now()

    executed_count = 0
    error_count = 0
    observations: list[Observation] = []
    for request in requests:
        if not can_reserve_request(stats=stats, limits=limits):
            logger.warning("test_budget_exhausted", test_id=test.test_id)
            break

        body = request.body if isinstance(request.body, bytes) else None
        response = await http_client.send(
            method=request.method,
            url=request.url,
            headers=dict(request.headers),
            body=body,
            max_response_body_size=limits.max_response_body_size,
            verify_tls=verify_tls,
        )
        stats = record_request(stats, phase=RequestPhase.TEST)
        stats = record_response_status(
            stats, status_code=response.status_code, fetch_error=response.fetch_error
        )
        executed_count += 1
        if response.fetch_error is not None or response.status_code >= 500:
            error_count += 1

        observations.extend(
            response_analyzer.analyze(
                response=response,
                request_id=request.request_id,
                payload_value=request.metadata.payload_value,
                detection_pattern=request.metadata.detection_pattern,
            )
        )

    if executed_count > 0:
        stats = record_test_executed(stats)
    if observations:
        stats = record_observation_found(stats)

    if executed_count == 0:
        result = TestResult.INCONCLUSIVE
    elif observations:
        result = TestResult.FINDING_SUSPECTED
    else:
        result = TestResult.NO_FINDING

    completed_fully = executed_count == len(requests)
    updated_test = replace(
        test,
        status=TestStatus.COMPLETED if completed_fully else TestStatus.ABORTED,
        result=result,
        requests_count=executed_count,
        errors_count=error_count,
        findings_count=len(observations),
        started_at=started_at,
        completed_at=clock.now(),
    )
    return updated_test, stats, tuple(observations)


async def run_logic_test(
    *,
    http_client: HttpClient,
    session_provider: SessionProvider,
    access_control_analyzer: AccessControlAnalyzer,
    test: Test,
    requests: Sequence[ScanRequest],
    limits: Limits,
    clock: Clock,
    logger: Logger,
    stats: ScanStatistics | None = None,
    expected_denial_status_codes: Sequence[int] = (401, 403, 404),
    verify_tls: bool = True,
) -> tuple[Test, ScanStatistics, tuple[Observation, ...]]:
    """Variante de `run_test` (Phase 7c) : applique la session courante
    (cookies/headers, meme logique que `discovery_orchestrator`) a
    chaque requete avant emission, puis appelle `AccessControlAnalyzer`
    sur chaque reponse. `logic_tests` necessite une session
    authentifiee — avertit (non bloquant) si la session obtenue est
    vide, signal probable d'un scan lance sans authentification reelle
    malgre `logic_tests` active (voir domain.services.test_planning_service,
    Phase 6)."""
    stats = stats if stats is not None else ScanStatistics()
    started_at: datetime = clock.now()

    session = await session_provider.get_session()
    if not session.cookies and not session.headers:
        logger.warning("logic_test_without_authenticated_session", test_id=test.test_id)

    executed_count = 0
    error_count = 0
    observations: list[Observation] = []
    for request in requests:
        if not can_reserve_request(stats=stats, limits=limits):
            logger.warning("test_budget_exhausted", test_id=test.test_id)
            break

        headers = dict(request.headers)
        headers.update(session.headers)
        if session.cookies:
            headers["Cookie"] = "; ".join(f"{name}={value}" for name, value in session.cookies.items())

        body = request.body if isinstance(request.body, bytes) else None
        response = await http_client.send(
            method=request.method,
            url=request.url,
            headers=headers,
            body=body,
            max_response_body_size=limits.max_response_body_size,
            verify_tls=verify_tls,
        )
        stats = record_request(stats, phase=RequestPhase.TEST)
        stats = record_response_status(
            stats, status_code=response.status_code, fetch_error=response.fetch_error
        )
        executed_count += 1
        if response.fetch_error is not None or response.status_code >= 500:
            error_count += 1

        observation = access_control_analyzer.check(
            response=response,
            request_id=request.request_id,
            expected_denial_status_codes=expected_denial_status_codes,
        )
        if observation is not None:
            observations.append(observation)

    if executed_count > 0:
        stats = record_test_executed(stats)
    if observations:
        stats = record_observation_found(stats)

    if executed_count == 0:
        result = TestResult.INCONCLUSIVE
    elif observations:
        result = TestResult.FINDING_SUSPECTED
    else:
        result = TestResult.NO_FINDING

    completed_fully = executed_count == len(requests)
    updated_test = replace(
        test,
        status=TestStatus.COMPLETED if completed_fully else TestStatus.ABORTED,
        result=result,
        requests_count=executed_count,
        errors_count=error_count,
        findings_count=len(observations),
        started_at=started_at,
        completed_at=clock.now(),
    )
    return updated_test, stats, tuple(observations)
