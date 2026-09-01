# Copyright (c) 2026 kraynux - Licence MIT
"""Verifie le cablage du fuzzing de headers (generate_for_url) et du
fuzzing de formulaires GET (generate_for_form) dans
CompositeTestPlanGenerator — comblement de trou de couverture,
post-Phase 10."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from urllib.parse import parse_qsl, urlsplit

from omega_fuzz.plugins.fuzzers.common.mutation_context import GENERIC_MUTATIONS
from omega_fuzz.plugins.fuzzers.header_fuzzer import FUZZABLE_HEADERS
from omega_fuzz.plugins.test_plan_generator import CompositeTestPlanGenerator

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


@dataclass(frozen=True, slots=True)
class _FakeForm:
    """Satisfait structurellement `ports.url_discoverer.DiscoveredForm`."""

    action_url: str
    method: str
    fields: dict[str, str] = field(default_factory=dict)


def test_generate_for_url_includes_one_fuzz_plan_per_fuzzable_header() -> None:
    generator = CompositeTestPlanGenerator()
    plans = generator.generate_for_url(
        target_short="example_root", url="https://example.com/", parameters=[], now=NOW
    )

    header_plans = [plan for plan in plans if plan[2] == "fuzz"]
    assert len(header_plans) == len(FUZZABLE_HEADERS)
    fuzzed_header_names = {plan[0].target.parameters[0] for plan in header_plans}
    assert fuzzed_header_names == set(FUZZABLE_HEADERS)


def test_generate_for_form_produces_one_plan_per_field() -> None:
    generator = CompositeTestPlanGenerator()
    form = _FakeForm(
        action_url="https://example.com/search",
        method="GET",
        fields={"q": "hello", "category": "all"},
    )

    plans = generator.generate_for_form(target_short="example_root", form=form, now=NOW)

    assert len(plans) == len(form.fields)
    assert all(kind == "fuzz" for _test, _requests, kind in plans)

    fuzzed_fields = {test.target.parameters[0] for test, _requests, _kind in plans}
    assert fuzzed_fields == set(form.fields)

    for test, requests, _kind in plans:
        target_field = test.target.parameters[0]
        assert len(requests) == len(GENERIC_MUTATIONS)
        applied = []
        for request in requests:
            assert request.method == "GET"
            assert request.body is None
            query_pairs = dict(parse_qsl(urlsplit(request.url).query, keep_blank_values=True))
            applied.append(query_pairs[target_field])
        assert applied == list(GENERIC_MUTATIONS)
