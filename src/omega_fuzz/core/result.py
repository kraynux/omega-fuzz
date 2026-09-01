# Copyright (c) 2026 kraynux - Licence MIT
"""Type de resultat generique (OMEGA-FUZZ_ARBORESCENCE.md §5.3) :
succes, echec controle ou resultat partiel. Utilise par les couches
`domain`/`application` pour representer un resultat sans lever
d'exception pour un cas attendu (ex. une decision de scope refusee n'est
pas une erreur, c'est un `Result` d'echec controle avec une raison)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Generic, TypeVar

T = TypeVar("T")


class ResultKind(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"


@dataclass(frozen=True, slots=True)
class Result(Generic[T]):
    """Resultat generique. `value` porte la charge utile pour SUCCESS et
    PARTIAL (partiel : une partie du travail a abouti, `reason` explique
    ce qui manque) ; `reason` porte le motif structure pour FAILURE et
    PARTIAL. Ne jamais construire directement — passer par les
    constructeurs `success`/`failure`/`partial` ci-dessous."""

    kind: ResultKind
    value: T | None
    reason: str | None

    @property
    def is_success(self) -> bool:
        return self.kind is ResultKind.SUCCESS

    @property
    def is_failure(self) -> bool:
        return self.kind is ResultKind.FAILURE

    @property
    def is_partial(self) -> bool:
        return self.kind is ResultKind.PARTIAL

    @classmethod
    def success(cls, value: T) -> Result[T]:
        return cls(kind=ResultKind.SUCCESS, value=value, reason=None)

    @classmethod
    def failure(cls, reason: str) -> Result[T]:
        return cls(kind=ResultKind.FAILURE, value=None, reason=reason)

    @classmethod
    def partial(cls, value: T, reason: str) -> Result[T]:
        return cls(kind=ResultKind.PARTIAL, value=value, reason=reason)
