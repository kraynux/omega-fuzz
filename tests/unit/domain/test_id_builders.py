# Copyright (c) 2026 kraynux - Licence MIT
"""Formats exacts d'OMEGA-FUZZ_SPECIFICATIONS.md §12.2-12.4."""
from __future__ import annotations

from omega_fuzz.domain.requests.request_id import build_request_id
from omega_fuzz.domain.targets.target_id import build_target_id
from omega_fuzz.domain.tests.test_id import build_test_id


def test_build_target_id_matches_spec_examples() -> None:
    assert build_target_id(host="example.com") == "example_root"
    assert build_target_id(host="intranet.local", context="root") == "intranet_root"


def test_build_test_id_matches_spec_example() -> None:
    assert (
        build_test_id(module="fuzzhttp", target_short="example_root", sequence=1)
        == "test_fuzzhttp_example_root_000001"
    )
    assert (
        build_test_id(module="sigxss", target_short="example_root", sequence=120)
        == "test_sigxss_example_root_000120"
    )


def test_build_request_id_matches_spec_example() -> None:
    assert (
        build_request_id(
            module="fuzzhttp", target_short="example_root", test_sequence=1, request_sequence=1
        )
        == "req_fuzzhttp_example_root_000001_0001"
    )
    assert (
        build_request_id(
            module="fuzzhttp", target_short="example_root", test_sequence=1, request_sequence=100
        )
        == "req_fuzzhttp_example_root_000001_0100"
    )
