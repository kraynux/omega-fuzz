# Copyright (c) 2026 kraynux - Licence MIT
"""Lance un scan prepare (Phase 10a, OMEGA-FUZZ_ARBORESCENCE.md §16.3) :
demande confirmation si necessaire, cree le `Scan` initial, delegue
l'execution a `application.services.scan_orchestrator.run_scan`, puis
persiste le resultat final (`Scan` + chaque `Finding`)."""
from __future__ import annotations

from typing import TYPE_CHECKING

from omega_fuzz.application.exceptions import ApplicationError
from omega_fuzz.application.services.scan_orchestrator import ScanRunResult, run_scan
from omega_fuzz.domain.profiles.aggressiveness_level import AggressivenessLevel
from omega_fuzz.domain.profiles.preset import PresetName
from omega_fuzz.domain.scans.scan import Scan
from omega_fuzz.domain.scans.scan_id import ScanId
from omega_fuzz.domain.scans.scan_status import ScanStatus
from omega_fuzz.domain.targets.target import Target
from omega_fuzz.domain.targets.target_id import TargetId

if TYPE_CHECKING:
    from datetime import datetime

    from omega_fuzz.application.commands.prepare_scan import PreparedScan
    from omega_fuzz.ports.clock import Clock
    from omega_fuzz.ports.confirmation_provider import ConfirmationProvider
    from omega_fuzz.ports.finding_repository import FindingRepository
    from omega_fuzz.ports.http_client import HttpClient
    from omega_fuzz.ports.id_generator import IdGenerator
    from omega_fuzz.ports.logger import Logger
    from omega_fuzz.ports.response_analyzer import ResponseAnalyzer
    from omega_fuzz.ports.scan_repository import ScanRepository
    from omega_fuzz.ports.session_provider import SessionProvider
    from omega_fuzz.ports.test_plan_generator import TestPlanGenerator
    from omega_fuzz.ports.url_discoverer import UrlDiscoverer

_CONFIRMATION_MESSAGE = (
    "Ce scan a ete signale comme necessitant une confirmation explicite "
    "(profil agressif/etendu ou combinaison inhabituelle) : confirmez-vous "
    "vouloir le lancer ?"
)
_STRICT_CONFIRMATION_PHRASE = "OUI-J-AI-L-AUTORISATION"


def required_confirmation_phrase(prepared: PreparedScan) -> str | None:
    """Phrase stricte exigee (OMEGA-FUZZ_SPECIFICATIONS.md §16.1) pour
    les cas explicitement listes comme equivalents a un profil violent
    (§16) : agressivite `violent`, preset `lab-extreme`, ou verification
    TLS desactivee. Une combinaison inhabituelle seule (sans l'un de ces
    trois facteurs) ne declenche qu'une confirmation simple oui/non.

    Publique (Phase 10d) : seule source de verite du calcul, reutilisee
    par `interfaces/tui/screens/scan_review_screen.py` pour piloter le
    champ de saisie de confirmation renforcee — la confirmation TUI se
    fait dans l'ecran (widgets), pas via `ConfirmationProvider.confirm()`
    (bloquant, incompatible avec push_screen()+callback asynchrone)."""
    configuration = prepared.configuration
    if (
        configuration.aggressiveness is AggressivenessLevel.VIOLENT
        or configuration.preset is PresetName.LAB_EXTREME
        or not prepared.verify_tls
    ):
        return _STRICT_CONFIRMATION_PHRASE
    return None


async def start_scan(
    *,
    prepared: PreparedScan,
    http_client: HttpClient,
    url_discoverer: UrlDiscoverer,
    session_provider: SessionProvider,
    response_analyzer: ResponseAnalyzer,
    security_headers_analyzer: ResponseAnalyzer,
    test_plan_generator: TestPlanGenerator,
    scan_repository: ScanRepository,
    finding_repository: FindingRepository,
    confirmation_provider: ConfirmationProvider,
    id_generator: IdGenerator,
    clock: Clock,
    logger: Logger,
) -> ScanRunResult:
    if prepared.configuration.requires_confirmation and not confirmation_provider.confirm(
        message=_CONFIRMATION_MESSAGE, required_phrase=required_confirmation_phrase(prepared)
    ):
        raise ApplicationError("scan refuse : confirmation requise non obtenue")

    now: datetime = clock.now()
    scan = Scan(
        scan_id=ScanId(id_generator.new_scan_id()),
        target_id=prepared.target_id,
        status=ScanStatus.RUNNING,
        created_at=now,
        started_at=now,
    )
    scan_repository.save(scan)

    target = Target(
        target_id=TargetId(prepared.target_id),
        entry_url=prepared.entry_url,
        scope=prepared.configuration.scope,
    )

    result = await run_scan(
        http_client=http_client,
        url_discoverer=url_discoverer,
        session_provider=session_provider,
        response_analyzer=response_analyzer,
        security_headers_analyzer=security_headers_analyzer,
        test_plan_generator=test_plan_generator,
        scan=scan,
        target=target,
        configuration=prepared.configuration,
        clock=clock,
        logger=logger,
        verify_tls=prepared.verify_tls,
    )

    scan_repository.save(result.scan)
    for finding in result.findings:
        finding_repository.save(finding)

    return result
