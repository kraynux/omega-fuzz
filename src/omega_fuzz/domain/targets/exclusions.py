# Copyright (c) 2026 kraynux - Licence MIT
"""Raisons d'exclusion de scope (OMEGA-FUZZ_ARBORESCENCE.md §8) — liste
figee, une `ScopeDecision` de rejet porte toujours l'une de ces
valeurs."""
from __future__ import annotations

from enum import Enum


class ExclusionReason(str, Enum):
    INVALID_URL = "invalid_url"
    UNSUPPORTED_SCHEME = "unsupported_scheme"
    HOST_OUT_OF_SCOPE = "host_out_of_scope"
    SUBDOMAIN_NOT_ALLOWED = "subdomain_not_allowed"
    SUBDOMAIN_BLOCKED = "subdomain_blocked"
    PORT_OUT_OF_SCOPE = "port_out_of_scope"
    PATH_NOT_ALLOWED = "path_not_allowed"
    PATH_BLOCKED = "path_blocked"
    PATTERN_BLOCKED = "pattern_blocked"
    MAX_DEPTH_EXCEEDED = "max_depth_exceeded"
    EXTERNAL_REDIRECT = "external_redirect"
