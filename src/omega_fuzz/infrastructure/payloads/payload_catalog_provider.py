# Copyright (c) 2026 kraynux - Licence MIT
"""Implemente ports/payload_provider.py::PayloadProvider a partir des
catalogues YAML charges (`payload_loader.py`)."""
from __future__ import annotations

from collections.abc import Sequence

from omega_fuzz.domain.findings.payload_catalog import PayloadCatalog


class YamlPayloadProvider:
    def __init__(self, catalogs: dict[str, PayloadCatalog]) -> None:
        self._catalogs = catalogs

    def payloads_for(self, *, category: str) -> Sequence[str]:
        return tuple(entry.value for entry in self._catalogs[category].payloads)

    def catalog_version(self, *, category: str) -> str:
        return self._catalogs[category].version
