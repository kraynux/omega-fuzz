# Copyright (c) 2026 kraynux - Licence MIT
"""Orchestration de scan bout-en-bout (Phase 10a,
OMEGA-FUZZ_ARBORESCENCE.md §16.2/§17) : enchaine decouverte (Phase 4),
generation+execution de tests fuzz/signatures (Phases 7a/7b) et
construction des findings (Phase 8) pour une cible deja preparee
(`application.commands.prepare_scan`).

Perimetre de generation automatique volontairement limite a 7a+7b :
7c (`logic_tests`/IDOR) reste hors du pipeline automatique
(OMEGA-FUZZ_PLAN_DEV.md Phase 7c : « tests de logique metier actives
explicitement ») — invocable separement, hors de cette fonction. Seuls
les parametres de query string des URLs decouvertes sont fuzzes :
`discovery_orchestrator.run_discovery` n'appelle jamais
`UrlDiscoverer.discover_forms`, donc aucune structure de formulaire
n'existe a ce stade pour alimenter `form_parameter_fuzzer` (coupe de
perimetre honnete, a completer par une extension future de la
decouverte elle-meme).

Ne genere/n'execute jamais les plans de test directement : delegue a
`ports.test_plan_generator.TestPlanGenerator`, dont l'implementation
concrete (`plugins.test_plan_generator.CompositeTestPlanGenerator`)
vit dans `plugins/` — la Dependency Rule interdit a `application`
d'importer `plugins` (couches soeurs, meme contournement deja etabli
pour `ResponseAnalyzer`).

Deux `ResponseAnalyzer` distincts, jamais un seul partage (bug trouve
par smoke-test manuel en Phase 10b, meme categorie que le bug
`re.Pattern` de la Phase 9b) : `response_analyzer` (XSS/injection) ne
doit JAMAIS verifier les headers de securite, sans quoi chaque reponse
XSS/injection generait aussi une observation « header manquant » qui
ecrasait le titre du finding reel (`Finding.title` derive de
`observation.kind`, pas de `test.subtype`). Seul le test
`security_headers_signature` (`kind="signature_headers"`) doit
declencher cette verification, via `security_headers_analyzer`."""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import TYPE_CHECKING
from urllib.parse import parse_qsl, urlsplit

from omega_fuzz.domain.reports.termination import TerminationReason, TerminationTrigger
from omega_fuzz.domain.scans.scan_status import ScanStatus
from omega_fuzz.domain.services.finding_builder_service import build_finding
from omega_fuzz.domain.services.finding_deduplication_service import deduplicate_findings
from omega_fuzz.domain.services.limit_service import determine_termination
from omega_fuzz.domain.targets.discovered_url import DiscoveredUrlState

from .discovery_orchestrator import run_discovery
from .test_orchestrator import run_signature_test, run_test

if TYPE_CHECKING:
    from omega_fuzz.domain.findings.finding import Finding
    from omega_fuzz.domain.findings.observation import Observation
    from omega_fuzz.domain.profiles.effective_configuration import EffectiveConfiguration
    from omega_fuzz.domain.reports.scan_statistics import ScanStatistics
    from omega_fuzz.domain.scans.scan import Scan
    from omega_fuzz.domain.targets.target import Target
    from omega_fuzz.domain.tests.test import Test
    from omega_fuzz.ports.clock import Clock
    from omega_fuzz.ports.http_client import HttpClient
    from omega_fuzz.ports.logger import Logger
    from omega_fuzz.ports.response_analyzer import ResponseAnalyzer
    from omega_fuzz.ports.session_provider import SessionProvider
    from omega_fuzz.ports.test_plan_generator import TestPlanGenerator
    from omega_fuzz.ports.url_discoverer import UrlDiscoverer


@dataclass
class ScanRunResult:
    scan: Scan
    tests: tuple[Test, ...]
    findings: tuple[Finding, ...]
    statistics: ScanStatistics


async def run_scan(
    *,
    http_client: HttpClient,
    url_discoverer: UrlDiscoverer,
    session_provider: SessionProvider,
    response_analyzer: ResponseAnalyzer,
    security_headers_analyzer: ResponseAnalyzer,
    test_plan_generator: TestPlanGenerator,
    scan: Scan,
    target: Target,
    configuration: EffectiveConfiguration,
    clock: Clock,
    logger: Logger,
    verify_tls: bool = True,
) -> ScanRunResult:
    scan_started_at = clock.now()
    limits = configuration.limits
    target_short = target.target_id.value

    discovery_result = await run_discovery(
        http_client=http_client,
        url_discoverer=url_discoverer,
        session_provider=session_provider,
        target=target,
        limits=limits,
        logger=logger,
        verify_tls=verify_tls,
    )
    stats = discovery_result.statistics

    accepted_urls = [
        discovered
        for discovered in discovery_result.discovered_urls
        if discovered.state is DiscoveredUrlState.ACCEPTED
    ]

    tests: list[Test] = []
    finding_inputs: list[tuple[Test, Observation]] = []
    termination_reason: TerminationReason | None = None

    for discovered in accepted_urls:
        query = urlsplit(discovered.url).query
        parameters = [name for name, _ in parse_qsl(query, keep_blank_values=True)]
        plans = test_plan_generator.generate_for_url(
            target_short=target_short, url=discovered.url, parameters=parameters, now=clock.now()
        )

        for test, requests, kind in plans:
            elapsed_seconds = (clock.now() - scan_started_at).total_seconds()
            termination_reason = determine_termination(
                stats=stats, limits=limits, elapsed_seconds=elapsed_seconds
            )
            if termination_reason is not None:
                break

            if kind == "fuzz":
                updated_test, stats = await run_test(
                    http_client=http_client,
                    test=test,
                    requests=requests,
                    limits=limits,
                    clock=clock,
                    logger=logger,
                    stats=stats,
                    verify_tls=verify_tls,
                )
                tests.append(updated_test)
            else:
                analyzer = security_headers_analyzer if kind == "signature_headers" else response_analyzer
                updated_test, stats, observations = await run_signature_test(
                    http_client=http_client,
                    response_analyzer=analyzer,
                    test=test,
                    requests=requests,
                    limits=limits,
                    clock=clock,
                    logger=logger,
                    stats=stats,
                    verify_tls=verify_tls,
                )
                tests.append(updated_test)
                finding_inputs.extend((updated_test, observation) for observation in observations)

        if termination_reason is not None:
            break

    if termination_reason is None:
        for form in discovery_result.discovered_forms:
            plans = test_plan_generator.generate_for_form(
                target_short=target_short, form=form, now=clock.now()
            )

            for test, requests, _kind in plans:
                elapsed_seconds = (clock.now() - scan_started_at).total_seconds()
                termination_reason = determine_termination(
                    stats=stats, limits=limits, elapsed_seconds=elapsed_seconds
                )
                if termination_reason is not None:
                    break

                updated_test, stats = await run_test(
                    http_client=http_client,
                    test=test,
                    requests=requests,
                    limits=limits,
                    clock=clock,
                    logger=logger,
                    stats=stats,
                    verify_tls=verify_tls,
                )
                tests.append(updated_test)

            if termination_reason is not None:
                break

    findings: list[Finding] = []
    for sequence, (test, observation) in enumerate(finding_inputs, start=1):
        findings.append(
            build_finding(
                scan_id=scan.scan_id.value,
                test=test,
                observation=observation,
                target_short=target_short,
                sequence=sequence,
                now=clock.now(),
            )
        )
    deduplicated_findings = deduplicate_findings(findings)

    final_status: ScanStatus
    if termination_reason is None:
        termination_reason = TerminationReason(trigger=TerminationTrigger.COMPLETED_NORMALLY)
        final_status = ScanStatus.COMPLETED
    else:
        final_status = ScanStatus.COMPLETED_TRUNCATED

    final_scan = replace(
        scan, status=final_status, completed_at=clock.now(), termination_reason=termination_reason
    )

    return ScanRunResult(
        scan=final_scan,
        tests=tuple(tests),
        findings=deduplicated_findings,
        statistics=stats,
    )
