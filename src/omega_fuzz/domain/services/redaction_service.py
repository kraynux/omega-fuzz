# Copyright (c) 2026 kraynux - Licence MIT
"""Expurgation des secrets avant persistance/export
(OMEGA-FUZZ_SPECIFICATIONS.md §28.3, OMEGA-FUZZ_PLAN_DEV.md Phase 8).
Fonction pure (regex sur chaines) : place en `domain.services` plutot
que `infrastructure.analyzers.redactor` (nom envisage a la Phase 7b) —
meme correction de placement que `redirect_policy`/
`rate_limit_backoff_service` (Phase 4) et `payload_catalog` (Phase 7b) :
doit rester appelable depuis les analyseurs sans probleme de couche,
aucune dependance technique reelle."""
from __future__ import annotations

import re
from collections.abc import Mapping

_SECRET_HEADER_NAMES = frozenset(
    {"cookie", "set-cookie", "authorization", "x-api-key", "x-csrf-token"}
)

_SECRET_BODY_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = tuple(
    (re.compile(rf'("{field}"\s*:\s*")[^"]*(")', re.IGNORECASE), r"\1[EXPURGE]\2")
    for field in ("password", "token", "api_key", "secret")
)

_DEFAULT_MAX_LENGTH = 200
_TRUNCATION_SUFFIX = "...[tronque]"


def redact_headers(headers: Mapping[str, str]) -> dict[str, str]:
    return {
        name: ("[EXPURGE]" if name.lower() in _SECRET_HEADER_NAMES else value)
        for name, value in headers.items()
    }


def redact_body_snippet(body: str, *, max_length: int = _DEFAULT_MAX_LENGTH) -> str:
    redacted = body
    for pattern, replacement in _SECRET_BODY_PATTERNS:
        redacted = pattern.sub(replacement, redacted)
    if len(redacted) > max_length:
        return redacted[:max_length] + _TRUNCATION_SUFFIX
    return redacted
