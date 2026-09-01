# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import parse_qsl, urlsplit

from omega_fuzz.domain.requests.request_phase import RequestPhase
from omega_fuzz.plugins.fuzzers.common.mutation_context import GENERIC_MUTATIONS
from omega_fuzz.plugins.fuzzers.query_parameter_fuzzer import build_plan

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def test_one_request_per_mutation() -> None:
    test, requests = build_plan(
        target_short="example_root",
        sequence=1,
        url="https://example.com/search?q=hello",
        parameter_name="q",
        now=NOW,
    )
    assert len(requests) == len(GENERIC_MUTATIONS)
    assert test.requests_count == 0  # pas encore execute


def test_every_request_has_test_phase_and_test_id() -> None:
    test, requests = build_plan(
        target_short="example_root",
        sequence=1,
        url="https://example.com/search?q=hello",
        parameter_name="q",
        now=NOW,
    )
    for request in requests:
        assert request.context.phase is RequestPhase.TEST
        assert request.test_id == test.test_id
        assert request.test_id


def test_mutations_are_applied_to_the_target_parameter() -> None:
    _test, requests = build_plan(
        target_short="example_root",
        sequence=1,
        url="https://example.com/search?q=hello&page=2",
        parameter_name="q",
        now=NOW,
    )
    applied = []
    for request in requests:
        query = dict(parse_qsl(urlsplit(request.url).query, keep_blank_values=True))
        applied.append(query["q"])
        assert query["page"] == "2"  # les autres parametres restent inchanges
    assert applied == list(GENERIC_MUTATIONS)


def test_no_mutation_payload_appears_in_ids() -> None:
    """Exclut les mutations numeriques courtes ("0", "-1", "9"*20) qui
    peuvent coincider trivialement avec le remplissage zero-pad d'un ID
    (ex. "0" dans "000001") sans que ce soit une vraie fuite de
    payload — ne teste que les mutations non-numeriques/distinctives."""
    test, requests = build_plan(
        target_short="example_root",
        sequence=1,
        url="https://example.com/search?q=hello",
        parameter_name="q",
        now=NOW,
    )
    distinctive_mutations = [m for m in GENERIC_MUTATIONS if m and not m.lstrip("-").isdigit()]
    assert distinctive_mutations  # sanity : la liste n'est pas vide
    for mutation in distinctive_mutations:
        assert mutation not in test.test_id
        for request in requests:
            assert mutation not in request.request_id
