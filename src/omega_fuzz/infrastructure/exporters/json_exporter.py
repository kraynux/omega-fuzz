# Copyright (c) 2026 kraynux - Licence MIT
"""Implemente ports/report_exporter.py::ReportExporter pour le format
JSON (OMEGA-FUZZ_SPECIFICATIONS.md §27 : « integration et
automatisation »). Serialiseur recursif generique pour les dataclasses/
enums/datetime/mappings/tuples du modele de rapport — `Finding.severity`
est une propriete calculee (pas un champ de dataclass), traitee comme
cas particulier pour rester visible dans l'export (§27 : un export
destine a l'automatisation doit exposer la severite effective
directement)."""
from __future__ import annotations

import dataclasses
import json
import re
from collections.abc import Mapping
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from omega_fuzz.domain.findings.finding import Finding
from omega_fuzz.domain.reports.report_model import (
    ReportModel,
    count_tests_by_type,
    findings_by_severity,
    requests_by_module,
)


def _to_jsonable(value: Any) -> Any:
    if isinstance(value, Finding):
        data = {f.name: _to_jsonable(getattr(value, f.name)) for f in dataclasses.fields(value)}
        data["severity"] = value.severity.value
        return data
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return {f.name: _to_jsonable(getattr(value, f.name)) for f in dataclasses.fields(value)}
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, re.Pattern):
        return value.pattern
    if isinstance(value, Mapping):
        return {key: _to_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        items = [_to_jsonable(item) for item in value]
        if isinstance(value, (set, frozenset)):
            items.sort(key=str)  # ordre non garanti sinon, nuit a la reproductibilite
        return items
    return value


class JsonReportExporter:
    """Implemente ports/report_exporter.py::ReportExporter."""

    def export(
        self,
        *,
        report: ReportModel,
        format_name: str,
        output_path: Path,
        theme_name: str | None = None,
    ) -> None:
        if format_name != "json":
            raise ValueError(f"format non supporte par JsonReportExporter : {format_name!r}")

        data = _to_jsonable(report)
        data["requests_by_module"] = requests_by_module(report.tests)
        data["tests_by_type"] = count_tests_by_type(report.tests)
        data["findings_by_severity"] = findings_by_severity(report.findings)

        output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
