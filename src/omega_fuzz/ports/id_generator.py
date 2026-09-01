# Copyright (c) 2026 kraynux - Licence MIT
"""Contrat de generation d'identifiants (OMEGA-FUZZ_ARBORESCENCE.md
§15.3). Seul `scan_id` (D-006, OMEGA-FUZZ_SPECIFICATIONS.md §12.1) a
besoin d'une vraie source d'entropie et donc d'un port : `target_id`/
`test_id`/`request_id` sont des formats deterministes construits par des
fonctions pures du domaine (`domain.targets.target_id.build_target_id`,
`domain.tests.test_id.build_test_id`,
`domain.requests.request_id.build_request_id`) — revision par rapport a
la Phase 0, ou ce port portait a tort une methode generique
`new_scan_scoped_id` (convention deja etablie : les ports sont revises
en toute transparence quand une implementation reelle en revele le vrai
besoin)."""
from __future__ import annotations

from typing import Protocol


class IdGenerator(Protocol):
    def new_scan_id(self) -> str: ...
