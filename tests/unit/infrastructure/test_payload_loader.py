# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from pathlib import Path

import pytest

from omega_fuzz.core.errors import ConfigurationError
from omega_fuzz.infrastructure.payloads.payload_loader import (
    load_payload_catalog,
    load_security_headers_catalog,
)

_CATALOGS_DIR = Path(__file__).parents[3] / "src/omega_fuzz/infrastructure/payloads/catalogs"


@pytest.mark.parametrize("filename,category", [("generic.yaml", "generic"), ("xss.yaml", "xss"), ("injection.yaml", "injection")])
def test_real_catalog_loads_with_version_and_payloads(filename: str, category: str) -> None:
    catalog = load_payload_catalog(_CATALOGS_DIR / filename, category=category)
    assert catalog.category == category
    assert catalog.version
    assert len(catalog.payloads) > 0
    for entry in catalog.payloads:
        assert entry.value


def test_xss_catalog_entries_have_detection_patterns() -> None:
    catalog = load_payload_catalog(_CATALOGS_DIR / "xss.yaml", category="xss")
    assert all(entry.detection_pattern for entry in catalog.payloads)


def test_headers_catalog_loads() -> None:
    catalog = load_security_headers_catalog(_CATALOGS_DIR / "headers.yaml")
    assert catalog.version
    names = [header.name for header in catalog.required_headers]
    assert "Content-Security-Policy" in names
    nosniff = next(h for h in catalog.required_headers if h.name == "X-Content-Type-Options")
    assert nosniff.expected_value == "nosniff"


def test_missing_version_raises(tmp_path: Path) -> None:
    path = tmp_path / "bad.yaml"
    path.write_text("payloads:\n  - value: x\n", encoding="utf-8")
    with pytest.raises(ConfigurationError):
        load_payload_catalog(path, category="generic")


def test_malformed_payload_entry_raises(tmp_path: Path) -> None:
    path = tmp_path / "bad.yaml"
    path.write_text("version: '1.0.0'\npayloads:\n  - not_a_value_key: x\n", encoding="utf-8")
    with pytest.raises(ConfigurationError):
        load_payload_catalog(path, category="generic")


def test_non_mapping_yaml_raises(tmp_path: Path) -> None:
    path = tmp_path / "bad.yaml"
    path.write_text("- just\n- a\n- list\n", encoding="utf-8")
    with pytest.raises(ConfigurationError):
        load_payload_catalog(path, category="generic")
