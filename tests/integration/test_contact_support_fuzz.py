# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Aide -> Contact et support (ecrans partages d'omega-lib, D-016, 2026-11-09). Jamais de vrai envoi
ni de vrai navigateur : faux expediteur, fausse source, faux ouvreur."""
from __future__ import annotations

import asyncio
import re
from pathlib import Path
from types import SimpleNamespace

from omega_lib.infrastructure.declaration.json_store import JsonDeclarationStore
from omega_lib.ports.declaration import ContactSupportServices, SendOutcome
from textual.app import App
from textual.widgets import Button, Select, Static

from omega_fuzz.app.composition_root import build_container
from omega_fuzz.interfaces.tui.screens.help_screen import HelpScreen

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class _Sender:
    def __init__(self) -> None:
        self.sent: list[dict] = []

    def send(self, payload: dict) -> SendOutcome:
        self.sent.append(payload)
        return SendOutcome(True)


class _Source:
    def fetch_sha_list(self) -> str | None:
        return None


def _close(container: object) -> None:
    """Le conteneur d'omega-fuzz n'expose ni close() ni connexion : rien a fermer ici."""
    close = getattr(container, "close", None)
    if callable(close):
        close()


def test_container_prepares_contact_support_under_var(tmp_path: Path) -> None:
    container = build_container(var_dir=tmp_path, console_logging=False)
    try:
        services = container.contact_support
        assert services is not None
        assert services.software == "omega-fuzz"
        version = re.search(r'^version = "([^"]+)"$', (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8"),
                            re.MULTILINE)
        assert version is not None and services.version == version.group(1)
        assert isinstance(services.store, JsonDeclarationStore)
        assert services.store.path == tmp_path / "declaration.json"
        assert not services.store.path.exists()  # rien n'est ecrit avant l'accord
    finally:
        _close(container)


def test_help_without_container_hides_the_button() -> None:
    class _Host(App[None]):
        def on_mount(self) -> None:
            self.push_screen(HelpScreen())

    async def scenario() -> None:
        app = _Host()
        async with app.run_test(size=(120, 50)) as pilot:
            await pilot.pause()
            assert not app.screen.query("#contact-support")

    asyncio.run(scenario())


def test_help_opens_contact_support_and_declares_once(tmp_path: Path) -> None:
    sender = _Sender()
    services = ContactSupportServices(
        software="omega-fuzz", version="1.0.0", store=JsonDeclarationStore(tmp_path / "declaration.json"),
        sender=sender, release_source=_Source(), open_url=lambda url: False,
    )

    class _Host(App[None]):
        def on_mount(self) -> None:
            self.push_screen(HelpScreen(container=SimpleNamespace(contact_support=services)))

    async def settle(pilot) -> None:
        await pilot.pause()
        await asyncio.sleep(0.2)
        await pilot.pause()

    async def scenario() -> None:
        app = _Host()
        async with app.run_test(size=(120, 50)) as pilot:
            await pilot.pause()
            app.screen.query_one("#contact-support", Button).press()
            await pilot.pause()
            contact = app.screen
            assert type(contact).__name__ == "ContactSupportScreen"
            texts = " ".join(str(widget.render()) for widget in contact.query(Static))
            assert "omega-fuzz" in texts and "https://paypal.me/kraynux" in texts
            contact.query_one("#declare", Button).press()
            await pilot.pause()
            app.screen.query_one("#declaration-country", Select).value = "FR"
            await pilot.pause()
            app.screen.query_one("#send", Button).press()
            await settle(pilot)
            assert app.screen is contact
            assert not contact.query_one("#withdraw", Button).disabled

    asyncio.run(scenario())
    assert sender.sent == [{"cle": sender.sent[0]["cle"], "logiciel": "omega-fuzz", "version": "1.0.0",
                            "envoi": "unique", "pays": "FR"}]
