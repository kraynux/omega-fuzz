# Copyright (c) 2026 kraynux - Licence MIT
"""Fait passer `lint-imports` (import-linter) par `pytest` seul — arbo
dediee `tests/architecture/` propre a omega-fuzz (OMEGA-FUZZ_ARBORESCENCE.md
§3), contrairement au reste de la suite ou `lint-imports` est lance en
ligne de commande separee."""
from __future__ import annotations

import shutil
import subprocess

import pytest


def test_dependency_rule_contracts_pass() -> None:
    lint_imports = shutil.which("lint-imports")
    if lint_imports is None:
        pytest.skip("lint-imports introuvable sur le PATH (dependance dev absente)")
    result = subprocess.run(
        [lint_imports],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
