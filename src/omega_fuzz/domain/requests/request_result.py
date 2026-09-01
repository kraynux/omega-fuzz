# Copyright (c) 2026 kraynux - Licence MIT
"""Resultat minimal d'une requete emise, proprie au domaine (jamais
d'import de `ports.http_client.HttpResponse` ici — le domaine ne
depend jamais des ports, c'est l'inverse). Les adaptateurs concrets
mappent leur `HttpResponse` vers ce DTO quand ils rapportent un resultat
a `application`/`domain`."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RequestResult:
    status_code: int
    elapsed_seconds: float
    final_url: str
    truncated: bool = False
