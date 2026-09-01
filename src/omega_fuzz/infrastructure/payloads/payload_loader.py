# Copyright (c) 2026 kraynux - Licence MIT
"""Chargement des catalogues de payloads (OMEGA-FUZZ_ARBORESCENCE.md
§21) : `yaml.safe_load` uniquement (jamais `yaml.load` — pas
d'execution de tags Python arbitraires), rejette toute entree qui ne
correspond pas exactement au schema declaratif attendu."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from omega_fuzz.core.errors import ConfigurationError
from omega_fuzz.domain.findings.payload_catalog import (
    PayloadCatalog,
    PayloadEntry,
    RequiredHeader,
    SecurityHeadersCatalog,
)


def _load_yaml_mapping(path: Path) -> dict[str, Any]:
    try:
        raw_text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConfigurationError(f"catalogue illisible : {path}") from exc

    data = yaml.safe_load(raw_text)
    if not isinstance(data, dict):
        raise ConfigurationError(f"catalogue invalide (attendu un mapping) : {path}")
    return data


def load_payload_catalog(path: Path, *, category: str) -> PayloadCatalog:
    data = _load_yaml_mapping(path)

    version = data.get("version")
    if not isinstance(version, str) or not version:
        raise ConfigurationError(f"catalogue {path} : champ 'version' manquant ou invalide")

    raw_payloads = data.get("payloads")
    if not isinstance(raw_payloads, list):
        raise ConfigurationError(f"catalogue {path} : champ 'payloads' manquant ou invalide")

    entries: list[PayloadEntry] = []
    for raw_entry in raw_payloads:
        if not isinstance(raw_entry, dict) or "value" not in raw_entry:
            raise ConfigurationError(f"catalogue {path} : entree de payload invalide : {raw_entry!r}")
        entries.append(
            PayloadEntry(
                value=str(raw_entry["value"]),
                detection_pattern=raw_entry.get("detection_pattern"),
            )
        )

    return PayloadCatalog(category=category, version=version, payloads=tuple(entries))


def load_security_headers_catalog(path: Path) -> SecurityHeadersCatalog:
    data = _load_yaml_mapping(path)

    version = data.get("version")
    if not isinstance(version, str) or not version:
        raise ConfigurationError(f"catalogue {path} : champ 'version' manquant ou invalide")

    raw_headers = data.get("required_headers")
    if not isinstance(raw_headers, list):
        raise ConfigurationError(
            f"catalogue {path} : champ 'required_headers' manquant ou invalide"
        )

    headers: list[RequiredHeader] = []
    for raw_header in raw_headers:
        if not isinstance(raw_header, dict) or "name" not in raw_header:
            raise ConfigurationError(f"catalogue {path} : entree de header invalide : {raw_header!r}")
        headers.append(
            RequiredHeader(
                name=str(raw_header["name"]),
                expected_value=raw_header.get("expected_value"),
            )
        )

    return SecurityHeadersCatalog(version=version, required_headers=tuple(headers))
