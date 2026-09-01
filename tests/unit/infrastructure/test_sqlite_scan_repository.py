# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from omega_fuzz.domain.reports.termination import TerminationReason, TerminationTrigger
from omega_fuzz.domain.scans.scan import Scan
from omega_fuzz.domain.scans.scan_id import ScanId
from omega_fuzz.domain.scans.scan_state import ScanState
from omega_fuzz.domain.scans.scan_status import ScanStatus
from omega_fuzz.infrastructure.storage.sqlite.connection import open_connection
from omega_fuzz.infrastructure.storage.sqlite.scan_repository import SqliteScanRepository

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def _repository(tmp_path: Path) -> SqliteScanRepository:
    connection = open_connection(tmp_path / "test.db")
    return SqliteScanRepository(connection)


def test_save_and_get_round_trip_without_termination(tmp_path: Path) -> None:
    repo = _repository(tmp_path)
    scan = Scan(
        scan_id=ScanId("a1b2c3d4e5f64a7b8c9d0e1f2a3b4c5d"),
        target_id="example_root",
        status=ScanStatus.RUNNING,
        created_at=NOW,
        started_at=NOW,
    )
    repo.save(scan)

    loaded = repo.get(scan.scan_id.value)
    assert loaded is not None
    assert loaded.scan_id.value == scan.scan_id.value
    assert loaded.target_id == "example_root"
    assert loaded.status is ScanStatus.RUNNING
    assert loaded.created_at == NOW
    assert loaded.started_at == NOW
    assert loaded.completed_at is None
    assert loaded.termination_reason is None


def test_save_and_get_round_trip_with_termination(tmp_path: Path) -> None:
    repo = _repository(tmp_path)
    scan = Scan(
        scan_id=ScanId("b1b2c3d4e5f64a7b8c9d0e1f2a3b4c5d"),
        target_id="example_root",
        status=ScanStatus.COMPLETED_TRUNCATED,
        created_at=NOW,
        completed_at=NOW,
        termination_reason=TerminationReason(
            trigger=TerminationTrigger.LIMIT_REACHED,
            limit_name="max_total_requests",
            configured_value=1000,
            observed_value=1000,
        ),
    )
    repo.save(scan)

    loaded = repo.get(scan.scan_id.value)
    assert loaded is not None
    assert loaded.termination_reason is not None
    assert loaded.termination_reason.trigger is TerminationTrigger.LIMIT_REACHED
    assert loaded.termination_reason.limit_name == "max_total_requests"
    assert loaded.termination_reason.configured_value == 1000


def test_get_unknown_scan_returns_none(tmp_path: Path) -> None:
    repo = _repository(tmp_path)
    assert repo.get("unknown") is None


def test_list_history_orders_by_created_at_descending(tmp_path: Path) -> None:
    repo = _repository(tmp_path)
    older = Scan(
        scan_id=ScanId("c1b2c3d4e5f64a7b8c9d0e1f2a3b4c5d"),
        target_id="example_root",
        status=ScanStatus.COMPLETED,
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    newer = Scan(
        scan_id=ScanId("d1b2c3d4e5f64a7b8c9d0e1f2a3b4c5d"),
        target_id="example_root",
        status=ScanStatus.COMPLETED,
        created_at=datetime(2026, 1, 2, tzinfo=timezone.utc),
    )
    repo.save(older)
    repo.save(newer)

    history = repo.list_history()
    assert [scan.scan_id.value for scan in history] == [newer.scan_id.value, older.scan_id.value]


def test_save_state_and_get_state_round_trip(tmp_path: Path) -> None:
    repo = _repository(tmp_path)
    scan = Scan(
        scan_id=ScanId("e1b2c3d4e5f64a7b8c9d0e1f2a3b4c5d"),
        target_id="example_root",
        status=ScanStatus.PAUSED,
        created_at=NOW,
    )
    repo.save(scan)
    state = ScanState(
        scan_id=scan.scan_id.value,
        status=ScanStatus.PAUSED,
        pending_discovery_urls=("https://example.com/a", "https://example.com/b"),
        completed_test_ids=frozenset({"test_fuzzhttp_example_root_000001"}),
    )
    repo.save_state(state)

    loaded = repo.get_state(scan.scan_id.value)
    assert loaded is not None
    assert loaded.pending_discovery_urls == ("https://example.com/a", "https://example.com/b")
    assert loaded.completed_test_ids == frozenset({"test_fuzzhttp_example_root_000001"})


def test_get_state_unknown_scan_returns_none(tmp_path: Path) -> None:
    repo = _repository(tmp_path)
    assert repo.get_state("unknown") is None


def test_clear_removes_all_scans_and_states(tmp_path: Path) -> None:
    repo = _repository(tmp_path)
    scan = Scan(
        scan_id=ScanId("f1b2c3d4e5f64a7b8c9d0e1f2a3b4c5d"),
        target_id="example_root",
        status=ScanStatus.PAUSED,
        created_at=NOW,
    )
    repo.save(scan)
    repo.save_state(
        ScanState(scan_id=scan.scan_id.value, status=ScanStatus.PAUSED)
    )

    repo.clear()

    assert repo.get(scan.scan_id.value) is None
    assert repo.get_state(scan.scan_id.value) is None
    assert repo.list_history() == []
