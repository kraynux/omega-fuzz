# Copyright (c) 2026 kraynux - Licence MIT
"""Evaluation de scope (OMEGA-FUZZ_ARBORESCENCE.md §14, PLAN_DEV
Phase 1). Ordre de verification volontairement fixe : schema, host/
sous-domaine, port, path (extensions binaires bloquees, puis patterns
bloques, puis paths bloques/autorises), profondeur, puis redirection
externe — chaque etape produit une `ScopeDecision` explicable des le
premier rejet. Une URL hors scope n'est jamais mise en file ; une URL
hors profondeur est conservee comme information mais jamais developpee
ni testee (a la charge de l'appelant : ce service se contente de le
signaler via `reason`).

`_check_path` rejette d'abord `domain.targets.binary_extensions.
BLOCKED_EXTENSIONS_PATTERN` (bug reel : crawl qui semble fige sur un
dossier de fichiers `.iso`) — inconditionnel, avant meme les
`blocked_url_patterns` propres au profil de scope choisi. Une URL
rejetee ici n'est jamais recuperee par `discovery_orchestrator`
(`continue` avant tout appel HTTP) et n'entre jamais dans
`accepted_urls` cote `scan_orchestrator` : ni le crawl, ni le fuzzing de
parametres/headers/formulaires ne peuvent donc jamais l'atteindre."""
from __future__ import annotations

from urllib.parse import urljoin

from omega_fuzz.domain.services.url_normalization_service import normalize_url
from omega_fuzz.domain.targets.binary_extensions import BLOCKED_EXTENSIONS_PATTERN
from omega_fuzz.domain.targets.exclusions import ExclusionReason
from omega_fuzz.domain.targets.scope import Scope
from omega_fuzz.domain.targets.scope_decision import ACCEPTED_REASON, ScopeDecision
from omega_fuzz.domain.targets.scope_mode import ScopeMode
from omega_fuzz.domain.targets.url import NormalizedUrl, UrlNormalizationError


def evaluate_scope(
    *, raw_url: str, scope: Scope, depth: int, is_redirect: bool = False
) -> ScopeDecision:
    try:
        normalized = normalize_url(raw_url)
    except UrlNormalizationError as exc:
        return ScopeDecision(
            accepted=False, normalized_url=None, reason=exc.reason.value, rule="url", depth=None
        )

    if normalized.scheme not in scope.allowed_schemes:
        return _reject(normalized, ExclusionReason.UNSUPPORTED_SCHEME, "scheme", depth)

    host_reason = _check_host(normalized.host, scope)
    if host_reason is not None:
        if is_redirect:
            return _reject(normalized, ExclusionReason.EXTERNAL_REDIRECT, "redirect", depth)
        return _reject(normalized, host_reason, "host", depth)

    if normalized.port != scope.scope_port:
        return _reject(normalized, ExclusionReason.PORT_OUT_OF_SCOPE, "port", depth)

    path_reason = _check_path(normalized.path, scope)
    if path_reason is not None:
        return _reject(normalized, path_reason, "path", depth)

    if depth > scope.max_depth:
        return _reject(normalized, ExclusionReason.MAX_DEPTH_EXCEEDED, "depth", depth)

    return ScopeDecision(
        accepted=True,
        normalized_url=normalized.to_str(),
        reason=ACCEPTED_REASON,
        rule="ok",
        depth=depth,
    )


def _check_host(host: str, scope: Scope) -> ExclusionReason | None:
    if host == scope.root_host:
        return None
    is_subdomain = host.endswith(f".{scope.root_host}")
    if not is_subdomain:
        return ExclusionReason.HOST_OUT_OF_SCOPE
    if scope.mode is ScopeMode.EXACT:
        return ExclusionReason.SUBDOMAIN_NOT_ALLOWED
    if host in scope.blocked_subdomains:
        return ExclusionReason.SUBDOMAIN_BLOCKED
    if scope.allowed_subdomains and host not in scope.allowed_subdomains:
        return ExclusionReason.SUBDOMAIN_NOT_ALLOWED
    return None


def _check_path(path: str, scope: Scope) -> ExclusionReason | None:
    if BLOCKED_EXTENSIONS_PATTERN.search(path):
        return ExclusionReason.PATTERN_BLOCKED
    for pattern in scope.blocked_url_patterns:
        if pattern.search(path):
            return ExclusionReason.PATTERN_BLOCKED
    if any(path.startswith(blocked) for blocked in scope.blocked_paths):
        return ExclusionReason.PATH_BLOCKED
    if scope.allowed_paths and not any(path.startswith(allowed) for allowed in scope.allowed_paths):
        return ExclusionReason.PATH_NOT_ALLOWED
    return None


def _reject(
    normalized: NormalizedUrl, reason: ExclusionReason, rule: str, depth: int
) -> ScopeDecision:
    return ScopeDecision(
        accepted=False,
        normalized_url=normalized.to_str(),
        reason=reason.value,
        rule=rule,
        depth=depth,
    )


def decide_redirect(*, current_url: str, location: str, scope: Scope, depth: int) -> ScopeDecision:
    """Politique de redirection (OMEGA-FUZZ_PLAN_DEV.md Phase 4 : reponse
    3xx -> resoudre l'URL cible -> normaliser -> evaluer le scope ->
    suivre uniquement si autorisee, sinon journaliser comme redirection
    ignoree). `location` peut etre relative (RFC 7231) — resolue contre
    `current_url` avant evaluation. Purement domaine (`urllib.parse` est
    stdlib, pas une technologie a confiner) : ne vit pas dans
    `infrastructure.network` malgre son nom, pour rester appelable
    depuis `application` sans violer la Dependency Rule."""
    resolved_url = urljoin(current_url, location)
    return evaluate_scope(raw_url=resolved_url, scope=scope, depth=depth, is_redirect=True)
