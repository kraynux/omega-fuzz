# Copyright (c) 2026 kraynux - Licence MIT
"""Construit un graphe de navigation controle a partir d'une cible
(OMEGA-FUZZ_PLAN_DEV.md Phase 4, OMEGA-FUZZ_ARBORESCENCE.md §16.2/§17).
Une seule coroutine asyncio sequentielle (pas de workers paralleles ici
— le fuzzing multi-workers reel arrive en Phase 7, ou
`application.services.limit_orchestrator.LimitOrchestrator` devient
necessaire) : la verification de budget utilise directement la decision
pure `domain.services.limit_service.can_reserve_request`.

Formulaires (comblement de trou de couverture, post-Phase 10) :
`discover_forms` est appele a cote de `discover_urls` sur chaque reponse
HTML acceptee, mais filtre strictement — seuls les formulaires `GET`
sont retenus (`POST`/`PUT`/`DELETE` exclus : risque d'ecriture non
desiree sur la cible, decision produit, jamais reconsidere plus loin
dans le pipeline) et leur `action_url` doit passer `evaluate_scope`
(sans ca, un formulaire dont l'action pointe hors du domaine cible —
passerelle de paiement, inscription newsletter tierce — serait fuzze
comme le reste : fuite de scope silencieuse)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from omega_fuzz.domain.reports.scan_statistics import (
    ScanStatistics,
    record_redirect_external_ignored,
    record_redirect_followed,
    record_redirect_out_of_scope_ignored,
    record_request,
    record_response_status,
    record_url_evaluated,
)
from omega_fuzz.domain.requests.request_id import build_request_id
from omega_fuzz.domain.requests.request_phase import RequestPhase
from omega_fuzz.domain.services.depth_service import next_depth, should_expand
from omega_fuzz.domain.services.limit_service import can_reserve_request
from omega_fuzz.domain.services.scope_service import decide_redirect, evaluate_scope
from omega_fuzz.domain.targets.discovered_url import DiscoveredUrl, DiscoveredUrlState
from omega_fuzz.domain.targets.exclusions import ExclusionReason

if TYPE_CHECKING:
    from omega_fuzz.domain.profiles.limits import Limits
    from omega_fuzz.domain.targets.target import Target
    from omega_fuzz.ports.http_client import HttpClient
    from omega_fuzz.ports.logger import Logger
    from omega_fuzz.ports.session_provider import SessionProvider
    from omega_fuzz.ports.url_discoverer import DiscoveredForm, UrlDiscoverer

_DISCOVERY_MODULE = "crawler"


@dataclass
class DiscoveryResult:
    discovered_urls: tuple[DiscoveredUrl, ...]
    statistics: ScanStatistics
    discovered_forms: tuple[DiscoveredForm, ...] = field(default_factory=tuple)


async def run_discovery(
    *,
    http_client: HttpClient,
    url_discoverer: UrlDiscoverer,
    session_provider: SessionProvider,
    target: Target,
    limits: Limits,
    logger: Logger,
    verify_tls: bool = True,
) -> DiscoveryResult:
    target_short = target.target_id.value
    session = await session_provider.get_session()
    headers = dict(session.headers)
    if session.cookies:
        headers["Cookie"] = "; ".join(f"{name}={value}" for name, value in session.cookies.items())

    stats = ScanStatistics()
    discovered: dict[str, DiscoveredUrl] = {}
    seen_urls: set[str] = set()
    discovered_forms: list[DiscoveredForm] = []
    seen_forms: set[tuple[str, tuple[str, ...]]] = set()
    queue: list[tuple[str, int]] = [(target.entry_url.to_str(), 0)]
    request_sequence = 0

    while queue:
        raw_url, depth = queue.pop(0)

        decision = evaluate_scope(raw_url=raw_url, scope=target.scope, depth=depth)
        beyond_depth = decision.reason == ExclusionReason.MAX_DEPTH_EXCEEDED.value
        stats = record_url_evaluated(
            stats, decision_accepted=decision.accepted, beyond_depth=beyond_depth
        )

        normalized_key = decision.normalized_url or raw_url
        if normalized_key in seen_urls:
            continue
        seen_urls.add(normalized_key)

        if beyond_depth:
            state = DiscoveredUrlState.OUT_OF_DEPTH
        elif decision.accepted:
            state = DiscoveredUrlState.ACCEPTED
        else:
            state = DiscoveredUrlState.REJECTED
        discovered[normalized_key] = DiscoveredUrl(
            url=normalized_key, depth=depth, state=state, decision=decision
        )

        if not decision.accepted:
            # Hors scope ou hors profondeur : conservee comme information,
            # jamais developpee ni emise (OMEGA-FUZZ_PLAN_DEV.md Phase 1/4).
            continue

        if not can_reserve_request(stats=stats, limits=limits):
            logger.warning("discovery_budget_exhausted", target_id=target.target_id.value)
            break

        request_sequence += 1
        request_id = build_request_id(
            module=_DISCOVERY_MODULE,
            target_short=target_short,
            test_sequence=1,
            request_sequence=request_sequence,
        )
        logger.info(
            "discovery_request",
            request_id=request_id,
            url=normalized_key,
            depth=depth,
        )

        response = await http_client.send(
            method="GET",
            url=normalized_key,
            headers=headers,
            max_response_body_size=limits.max_response_body_size,
            verify_tls=verify_tls,
        )
        stats = record_request(stats, phase=RequestPhase.DISCOVERY)
        stats = record_response_status(
            stats, status_code=response.status_code, fetch_error=response.fetch_error
        )

        if response.fetch_error is not None:
            logger.warning(
                "discovery_fetch_error", url=normalized_key, error=response.fetch_error
            )
            continue

        if 300 <= response.status_code < 400:
            location = response.headers.get("location") or response.headers.get("Location")
            if not location:
                continue
            redirect_decision = decide_redirect(
                current_url=normalized_key, location=location, scope=target.scope, depth=depth
            )
            if redirect_decision.accepted:
                stats = record_redirect_followed(stats)
                queue.append((redirect_decision.normalized_url or location, depth))
            elif redirect_decision.reason == ExclusionReason.EXTERNAL_REDIRECT.value:
                stats = record_redirect_external_ignored(stats)
                logger.info(
                    "redirect_external_ignored", from_url=normalized_key, location=location
                )
            else:
                stats = record_redirect_out_of_scope_ignored(stats)
                logger.info(
                    "redirect_out_of_scope_ignored", from_url=normalized_key, location=location
                )
            continue

        if 200 <= response.status_code < 300 and should_expand(
            depth=depth, max_depth=target.scope.max_depth
        ):
            html_body = response.body.decode("utf-8", errors="replace")
            for link in url_discoverer.discover_urls(base_url=normalized_key, html_body=html_body):
                if link not in seen_urls:
                    queue.append((link, next_depth(depth)))

            for form in url_discoverer.discover_forms(base_url=normalized_key, html_body=html_body):
                if form.method.upper() != "GET":
                    continue
                form_decision = evaluate_scope(raw_url=form.action_url, scope=target.scope, depth=depth)
                if not form_decision.accepted:
                    continue
                form_key = (form_decision.normalized_url or form.action_url, tuple(sorted(form.fields)))
                if form_key not in seen_forms:
                    seen_forms.add(form_key)
                    discovered_forms.append(form)

    return DiscoveryResult(
        discovered_urls=tuple(discovered.values()),
        statistics=stats,
        discovered_forms=tuple(discovered_forms),
    )
