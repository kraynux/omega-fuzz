# Copyright (c) 2026 kraynux - Licence MIT
"""Configuration d'authentification (OMEGA-FUZZ_SPECIFICATIONS.md §8.5,
OMEGA-FUZZ_ARBORESCENCE.md §45). Charge depuis le fichier `--auth-config`
(`infrastructure.configuration.auth_config_loader`), jamais depuis la
ligne de commande en clair — voir la politique de redaction §28.3."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class AuthMode(str, Enum):
    NONE = "none"
    COOKIE = "cookie"
    BEARER_TOKEN = "bearer_token"
    LOGIN_FORM = "login_form"


@dataclass(frozen=True, slots=True)
class AuthContext:
    mode: AuthMode
    cookie: str | None = None
    bearer_token: str | None = None
    login_url: str | None = None
    username_field: str | None = None
    password_field: str | None = None
    username: str | None = None
    password: str | None = None
