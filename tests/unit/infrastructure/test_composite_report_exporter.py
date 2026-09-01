# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from omega_fuzz.infrastructure.exporters.report_exporter import CompositeReportExporter


class _FakeExporter:
    def __init__(self) -> None:
        self.calls: list[tuple[Any, str, Path]] = []

    def export(
        self,
        *,
        report: Any,
        format_name: str,
        output_path: Path,
        theme_name: str | None = None,
    ) -> None:
        self.calls.append((report, format_name, output_path))


def test_dispatches_to_the_matching_exporter(tmp_path: Path) -> None:
    json_exporter, markdown_exporter, html_exporter = _FakeExporter(), _FakeExporter(), _FakeExporter()
    composite = CompositeReportExporter(
        json_exporter=json_exporter, markdown_exporter=markdown_exporter, html_exporter=html_exporter
    )

    composite.export(report="r", format_name="html", output_path=tmp_path / "x.html")

    assert len(html_exporter.calls) == 1
    assert json_exporter.calls == []
    assert markdown_exporter.calls == []


def test_unknown_format_raises(tmp_path: Path) -> None:
    composite = CompositeReportExporter(
        json_exporter=_FakeExporter(), markdown_exporter=_FakeExporter(), html_exporter=_FakeExporter()
    )
    with pytest.raises(ValueError, match="yaml"):
        composite.export(report="r", format_name="yaml", output_path=tmp_path / "x")
