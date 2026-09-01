# Copyright (c) 2026 kraynux - Licence MIT
"""Application des surcharges utilisateur a un profil de base
(OMEGA-FUZZ_PLAN_DEV.md Phase 5 : « les options utilisateur peuvent
surcharger un preset dans les hard caps »)."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import fields, replace
from typing import Any

from omega_fuzz.core.errors import ValidationError
from omega_fuzz.domain.profiles.limits import Limits
from omega_fuzz.domain.services.limit_service import validate_limits

_LIMITS_FIELD_NAMES = frozenset(f.name for f in fields(Limits))


def apply_overrides(base: Limits, overrides: Mapping[str, Any]) -> Limits:
    """Leve `ValidationError` si un nom de champ est inconnu ou si le
    resultat depasse un hard cap (`limit_service.validate_limits`,
    Phase 3)."""
    unknown = set(overrides) - _LIMITS_FIELD_NAMES
    if unknown:
        raise ValidationError(f"champs de limite inconnus dans la surcharge : {sorted(unknown)}")

    effective = replace(base, **overrides)
    validate_limits(effective)
    return effective
