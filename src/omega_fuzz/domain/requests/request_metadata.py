# Copyright (c) 2026 kraynux - Licence MIT
"""Metadonnees de mutation d'une requete (OMEGA-FUZZ_SPECIFICATIONS.md
§11). `payload_value`/`detection_pattern` (Phase 7b) : jamais dans un
`test_id`/`request_id` (critere explicite Phase 7), mais legitimement
ici — c'est precisement le role documente du bloc `metadata`. Necessaire
pour que `application.services.test_orchestrator.run_signature_test`
sache, au moment d'analyser une reponse, quel payload a ete envoye et
quel pattern chercher."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RequestMetadata:
    payload_index: int | None = None
    payload_type: str | None = None
    parameter_name: str | None = None
    mutation_strategy: str | None = None
    payload_value: str | None = None
    detection_pattern: str | None = None
