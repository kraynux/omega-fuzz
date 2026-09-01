# Copyright (c) 2026 kraynux - Licence MIT
"""Charge le fichier `--auth-config` (OMEGA-FUZZ_SPECIFICATIONS.md §8.5)
— YAML strictement declaratif, `yaml.safe_load` (jamais `yaml.load`,
meme discipline que les catalogues de signatures, decision P de la
passe de coherence). Jamais d'identifiants en clair dans les logs/
exports (§28.3) : ce module ne journalise jamais le contenu du fichier
charge."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from omega_fuzz.core.errors import ConfigurationError
from omega_fuzz.domain.auth.auth_context import AuthContext, AuthMode

_REQUIRED_FIELDS_BY_MODE: dict[AuthMode, tuple[str, ...]] = {
    AuthMode.NONE: (),
    AuthMode.COOKIE: ("cookie",),
    AuthMode.BEARER_TOKEN: ("bearer_token",),
    AuthMode.LOGIN_FORM: (
        "login_url",
        "username_field",
        "password_field",
        "username",
        "password",
    ),
}


def load_auth_context(path: Path) -> AuthContext:
    try:
        raw_text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConfigurationError(f"fichier auth-config illisible : {path}") from exc

    data = yaml.safe_load(raw_text)
    if data is None:
        data = {}
    if not isinstance(data, dict):
        raise ConfigurationError(f"auth-config invalide (attendu un mapping) : {path}")

    return _build_auth_context(data, source=str(path))


def _build_auth_context(data: dict[str, Any], *, source: str) -> AuthContext:
    raw_mode = data.get("mode", AuthMode.NONE.value)
    try:
        mode = AuthMode(raw_mode)
    except ValueError as exc:
        raise ConfigurationError(f"mode auth-config inconnu : {raw_mode!r} ({source})") from exc

    missing = [field for field in _REQUIRED_FIELDS_BY_MODE[mode] if not data.get(field)]
    if missing:
        raise ConfigurationError(
            f"auth-config mode={mode.value} : champs manquants {missing} ({source})"
        )

    return AuthContext(
        mode=mode,
        cookie=data.get("cookie"),
        bearer_token=data.get("bearer_token"),
        login_url=data.get("login_url"),
        username_field=data.get("username_field"),
        password_field=data.get("password_field"),
        username=data.get("username"),
        password=data.get("password"),
    )
