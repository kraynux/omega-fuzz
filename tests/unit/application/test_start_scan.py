# Copyright (c) 2026 kraynux - Licence MIT
"""Verifie le contrat de `start_scan` (Phase 10a,
OMEGA-FUZZ_ARBORESCENCE.md §16.3) independamment du reste du pipeline
(la mecanique de scan reelle est couverte par
`tests/integration/test_scan_orchestrator.py`) : confirmation refusee
bloque et ne persiste rien, confirmation non requise ne consulte jamais
`ConfirmationProvider`, et le `Scan`/les `Finding` finaux sont bien
persistes."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import pytest

from omega_fuzz.application.commands.prepare_scan import prepare_scan
from omega_fuzz.application.commands.start_scan import start_scan
from omega_fuzz.application.exceptions import ApplicationError
from omega_fuzz.domain.auth.auth_context import AuthContext, AuthMode
from omega_fuzz.domain.auth.session import Session
from omega_fuzz.domain.profiles.aggressiveness_level import AggressivenessLevel
from omega_fuzz.domain.profiles.scope_profile import ScopeProfileName
from omega_fuzz.domain.scans.scan_status import ScanStatus
from omega_fuzz.ports.http_client import HttpResponse

_NONE_AUTH = AuthContext(mode=AuthMode.NONE)


class _FakeHttpResponse:
    status_code = 200
    headers: Mapping[str, str] = {}
    body = b"<html></html>"
    elapsed_seconds = 0.0
    final_url = "https://example.com/"
    truncated = False
    fetch_error: str | None = None


class _FakeHttpClient:
    def __init__(self) -> None:
        self.received_verify_tls: list[bool] = []

    async def send(
        self,
        *,
        method: str,
        url: str,
        headers: Mapping[str, str] | None = None,
        body: bytes | None = None,
        timeout: float | None = None,
        verify_tls: bool = True,
        max_response_body_size: int | None = None,
    ) -> HttpResponse:
        self.received_verify_tls.append(verify_tls)
        return _FakeHttpResponse()


class _FakeUrlDiscoverer:
    def discover_urls(self, *, base_url: str, html_body: str) -> Sequence[str]:
        return ()

    def discover_forms(self, *, base_url: str, html_body: str) -> Sequence[Any]:
        return ()


class _FakeSessionProvider:
    async def get_session(self) -> Session:
        return Session()


class _FakeResponseAnalyzer:
    def analyze(
        self,
        *,
        response: HttpResponse,
        request_id: str,
        payload_value: str | None = None,
        detection_pattern: str | None = None,
    ) -> Sequence[Any]:
        return ()


class _FakeTestPlanGenerator:
    def generate_for_url(
        self, *, target_short: str, url: str, parameters: Sequence[str], now: Any
    ) -> Sequence[Any]:
        return ()


class _FakeFindingRepository:
    """Implemente ports/finding_repository.py::FindingRepository."""

    def __init__(self) -> None:
        self.saved: list[Any] = []

    def save(self, finding: Any) -> None:
        self.saved.append(finding)

    def list_for_scan(self, scan_id: str) -> Sequence[Any]:
        return [finding for finding in self.saved if finding.scan_id == scan_id]

    def clear_for_scan(self, scan_id: str) -> None:
        self.saved = [finding for finding in self.saved if finding.scan_id != scan_id]


class _FakeIdGenerator:
    def new_scan_id(self) -> str:
        return "fixed-scan-id"


class _FakeConfirmationProvider:
    def __init__(self, *, accept: bool) -> None:
        self._accept = accept
        self.calls = 0
        self.received_required_phrases: list[str | None] = []

    def confirm(self, *, message: str, required_phrase: str | None = None) -> bool:
        self.calls += 1
        self.received_required_phrases.append(required_phrase)
        return self._accept


def _prepared(*, requires_confirmation_preset: bool) -> Any:
    from omega_fuzz.domain.profiles.preset import PresetName

    if requires_confirmation_preset:
        return prepare_scan(
            raw_target="https://example.com/", auth_context=_NONE_AUTH, preset=PresetName.LAB_EXTREME
        )
    return prepare_scan(
        raw_target="https://example.com/",
        auth_context=_NONE_AUTH,
        aggressiveness=AggressivenessLevel.STANDARD,
        scope_profile=ScopeProfileName.STANDARD,
    )


async def _start(
    *, prepared: Any, confirmation_provider: Any, scan_repository, clock, logger, http_client=None
):
    return await start_scan(
        prepared=prepared,
        http_client=http_client if http_client is not None else _FakeHttpClient(),
        url_discoverer=_FakeUrlDiscoverer(),
        session_provider=_FakeSessionProvider(),
        response_analyzer=_FakeResponseAnalyzer(),
        security_headers_analyzer=_FakeResponseAnalyzer(),
        test_plan_generator=_FakeTestPlanGenerator(),
        scan_repository=scan_repository,
        finding_repository=_FakeFindingRepository(),
        confirmation_provider=confirmation_provider,
        id_generator=_FakeIdGenerator(),
        clock=clock,
        logger=logger,
    )


async def test_confirmation_not_required_never_consults_provider(scan_repository, clock, logger) -> None:
    prepared = _prepared(requires_confirmation_preset=False)
    assert prepared.configuration.requires_confirmation is False
    confirmation_provider = _FakeConfirmationProvider(accept=False)

    result = await _start(
        prepared=prepared,
        confirmation_provider=confirmation_provider,
        scan_repository=scan_repository,
        clock=clock,
        logger=logger,
    )

    assert confirmation_provider.calls == 0
    assert result.scan.status is ScanStatus.COMPLETED
    assert scan_repository.get(result.scan.scan_id.value) is not None


async def test_confirmation_refused_raises_and_persists_nothing(scan_repository, clock, logger) -> None:
    prepared = _prepared(requires_confirmation_preset=True)
    assert prepared.configuration.requires_confirmation is True
    confirmation_provider = _FakeConfirmationProvider(accept=False)

    with pytest.raises(ApplicationError):
        await _start(
            prepared=prepared,
            confirmation_provider=confirmation_provider,
            scan_repository=scan_repository,
            clock=clock,
            logger=logger,
        )

    assert confirmation_provider.calls == 1
    assert scan_repository.list_history() == []


async def test_confirmation_accepted_persists_final_scan(scan_repository, clock, logger) -> None:
    prepared = _prepared(requires_confirmation_preset=True)
    confirmation_provider = _FakeConfirmationProvider(accept=True)

    result = await _start(
        prepared=prepared,
        confirmation_provider=confirmation_provider,
        scan_repository=scan_repository,
        clock=clock,
        logger=logger,
    )

    assert confirmation_provider.calls == 1
    persisted = scan_repository.get(result.scan.scan_id.value)
    assert persisted is not None
    assert persisted.status is ScanStatus.COMPLETED


async def test_lab_extreme_requires_strict_phrase(scan_repository, clock, logger) -> None:
    prepared = _prepared(requires_confirmation_preset=True)  # preset=LAB_EXTREME
    confirmation_provider = _FakeConfirmationProvider(accept=True)

    await _start(
        prepared=prepared,
        confirmation_provider=confirmation_provider,
        scan_repository=scan_repository,
        clock=clock,
        logger=logger,
    )

    assert confirmation_provider.received_required_phrases == ["OUI-J-AI-L-AUTORISATION"]


async def test_unusual_combination_alone_uses_simple_confirmation(scan_repository, clock, logger) -> None:
    """`strict + agressif` est une combinaison inhabituelle
    (`domain.profiles.profile_policies.UNUSUAL_COMBINATIONS`) mais ni
    violent, ni lab-extreme, ni verify_tls=false : confirmation simple
    (pas de phrase stricte exigee), OMEGA-FUZZ_SPECIFICATIONS.md §16.1."""
    prepared = prepare_scan(
        raw_target="https://example.com/",
        auth_context=_NONE_AUTH,
        aggressiveness=AggressivenessLevel.AGRESSIF,
        scope_profile=ScopeProfileName.STRICT,
    )
    assert prepared.configuration.requires_confirmation is True
    confirmation_provider = _FakeConfirmationProvider(accept=True)

    await _start(
        prepared=prepared,
        confirmation_provider=confirmation_provider,
        scan_repository=scan_repository,
        clock=clock,
        logger=logger,
    )

    assert confirmation_provider.received_required_phrases == [None]


async def test_verify_tls_false_requires_strict_phrase_even_on_safe_preset(
    scan_repository, clock, logger
) -> None:
    from omega_fuzz.domain.profiles.preset import PresetName

    prepared = prepare_scan(
        raw_target="https://example.com/",
        auth_context=_NONE_AUTH,
        preset=PresetName.PROD_SAFE,
        verify_tls=False,
    )
    confirmation_provider = _FakeConfirmationProvider(accept=True)

    await _start(
        prepared=prepared,
        confirmation_provider=confirmation_provider,
        scan_repository=scan_repository,
        clock=clock,
        logger=logger,
    )

    assert confirmation_provider.received_required_phrases == ["OUI-J-AI-L-AUTORISATION"]


async def test_verify_tls_propagates_to_http_client(scan_repository, clock, logger) -> None:
    from omega_fuzz.domain.profiles.preset import PresetName

    prepared = prepare_scan(
        raw_target="https://example.com/",
        auth_context=_NONE_AUTH,
        preset=PresetName.PROD_SAFE,
        verify_tls=False,
    )
    http_client = _FakeHttpClient()

    await _start(
        prepared=prepared,
        confirmation_provider=_FakeConfirmationProvider(accept=True),
        scan_repository=scan_repository,
        clock=clock,
        logger=logger,
        http_client=http_client,
    )

    assert http_client.received_verify_tls
    assert all(value is False for value in http_client.received_verify_tls)
