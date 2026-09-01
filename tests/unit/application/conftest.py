# Copyright (c) 2026 kraynux - Licence MIT
"""Doubles de test partages pour la couche application. Pas
d'adaptateur `ScanRepository` reel (SQLite) avant la Phase 9 — voir le
plan Phase 3."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pytest

from omega_fuzz.domain.scans.scan import Scan
from omega_fuzz.domain.scans.scan_state import ScanState


class InMemoryScanRepository:
    """Implemente ports/scan_repository.py::ScanRepository."""

    def __init__(self) -> None:
        self._scans: dict[str, Scan] = {}
        self._states: dict[str, ScanState] = {}

    def save(self, scan: Scan) -> None:
        self._scans[scan.scan_id.value] = scan

    def get(self, scan_id: str) -> Scan | None:
        return self._scans.get(scan_id)

    def list_history(self) -> list[Scan]:
        return list(self._scans.values())

    def clear(self) -> None:
        self._scans.clear()
        self._states.clear()

    def save_state(self, state: ScanState) -> None:
        self._states[state.scan_id] = state

    def get_state(self, scan_id: str) -> ScanState | None:
        return self._states.get(scan_id)


class FakeClock:
    """Implemente ports/clock.py::Clock."""

    def __init__(self, *, fixed: datetime | None = None) -> None:
        self._fixed = fixed or datetime(2026, 1, 1, tzinfo=timezone.utc)

    def now(self) -> datetime:
        return self._fixed


class FakeLogger:
    """Implemente ports/logger.py::Logger."""

    def __init__(self) -> None:
        self.events: list[tuple[str, str, dict[str, Any]]] = []

    def info(self, event: str, **fields: Any) -> None:
        self.events.append(("info", event, fields))

    def warning(self, event: str, **fields: Any) -> None:
        self.events.append(("warning", event, fields))

    def error(self, event: str, **fields: Any) -> None:
        self.events.append(("error", event, fields))


@pytest.fixture
def scan_repository() -> InMemoryScanRepository:
    return InMemoryScanRepository()


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock()


@pytest.fixture
def logger() -> FakeLogger:
    return FakeLogger()
