# Copyright (c) 2026 kraynux - Licence MIT
"""Tables des 5 profils de scope prets a l'emploi
(OMEGA-FUZZ_SPECIFICATIONS.md §17.1-17.5, valeurs YAML reprises
exactement). `blocked_url_patterns` reste une chaine brute ici (pas
encore compilee) — la compilation/validation reelle se fait dans
`domain.targets.scope.build_scope`, seul point d'entree qui doit lever
sur une regex invalide (OMEGA-FUZZ_SPECIFICATIONS.md §18.4)."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from omega_fuzz.domain.targets.scope_mode import ScopeMode

_ALLOWED_SCHEMES = frozenset({"http", "https"})


class ScopeProfileName(str, Enum):
    STRICT = "strict"
    STANDARD = "standard"
    LARGE = "large"
    API = "api"
    CUSTOM = "custom"


@dataclass(frozen=True, slots=True)
class ScopeProfileDefinition:
    scope_mode: ScopeMode
    max_depth: int
    allowed_schemes: frozenset[str] = _ALLOWED_SCHEMES
    allowed_subdomains: tuple[str, ...] = ()
    blocked_subdomains: tuple[str, ...] = ()
    allowed_paths: tuple[str, ...] = ()
    blocked_paths: tuple[str, ...] = ()
    blocked_url_patterns: tuple[str, ...] = field(default_factory=tuple)


SCOPE_PROFILES: dict[ScopeProfileName, ScopeProfileDefinition] = {
    ScopeProfileName.STRICT: ScopeProfileDefinition(
        scope_mode=ScopeMode.EXACT,
        max_depth=1,
        blocked_paths=("/health", "/ready", "/metrics", "/favicon.ico", "/robots.txt"),
    ),
    ScopeProfileName.STANDARD: ScopeProfileDefinition(
        scope_mode=ScopeMode.SUBDOMAINS,
        max_depth=2,
        blocked_subdomains=("cdn.example.com", "static.example.com", "assets.example.com"),
        blocked_paths=("/health", "/ready", "/metrics", "/static", "/assets"),
        blocked_url_patterns=(r".*\.(png|jpg|jpeg|gif|svg|css|js|woff2?|ttf|eot)$",),
    ),
    ScopeProfileName.LARGE: ScopeProfileDefinition(
        scope_mode=ScopeMode.SUBDOMAINS,
        max_depth=4,
        blocked_paths=("/health", "/ready", "/metrics"),
        blocked_url_patterns=(
            r".*\.(png|jpg|jpeg|gif|svg|css|js|woff2?|ttf|eot|pdf|zip|tar\.gz)$",
        ),
    ),
    ScopeProfileName.API: ScopeProfileDefinition(
        scope_mode=ScopeMode.EXACT,
        max_depth=3,
        allowed_paths=("/api", "/v1", "/v2"),
        blocked_paths=("/health", "/ready", "/metrics", "/docs", "/swagger", "/openapi"),
        blocked_url_patterns=(r".*\.(png|jpg|jpeg|gif|svg|css|js|woff2?|ttf|eot|html|pdf)$",),
    ),
    ScopeProfileName.CUSTOM: ScopeProfileDefinition(
        scope_mode=ScopeMode.SUBDOMAINS,
        max_depth=3,
    ),
}
