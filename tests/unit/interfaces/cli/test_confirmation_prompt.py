# Copyright (c) 2026 kraynux - Licence MIT
"""Verifie `CliConfirmationPrompt` (Phase 10b) : phrase exacte
acceptee/refusee (sensible a la casse, OMEGA-FUZZ_SPECIFICATIONS.md
§16.1), confirmation simple oui/non."""
from __future__ import annotations

import pytest

from omega_fuzz.interfaces.cli.prompts.confirmation_prompt import CliConfirmationPrompt


def test_exact_phrase_accepted(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("builtins.input", lambda _prompt: "OUI-J-AI-L-AUTORISATION")
    assert CliConfirmationPrompt().confirm(
        message="risque", required_phrase="OUI-J-AI-L-AUTORISATION"
    )


def test_phrase_is_case_sensitive(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("builtins.input", lambda _prompt: "oui-j-ai-l-autorisation")
    assert not CliConfirmationPrompt().confirm(
        message="risque", required_phrase="OUI-J-AI-L-AUTORISATION"
    )


def test_wrong_phrase_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("builtins.input", lambda _prompt: "non merci")
    assert not CliConfirmationPrompt().confirm(
        message="risque", required_phrase="OUI-J-AI-L-AUTORISATION"
    )


@pytest.mark.parametrize("answer", ["oui", "o", "Oui", "YES"])
def test_simple_confirmation_accepts_common_positive_answers(
    monkeypatch: pytest.MonkeyPatch, answer: str
) -> None:
    monkeypatch.setattr("builtins.input", lambda _prompt: answer)
    assert CliConfirmationPrompt().confirm(message="confirmer ?")


def test_simple_confirmation_refuses_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("builtins.input", lambda _prompt: "non")
    assert not CliConfirmationPrompt().confirm(message="confirmer ?")
