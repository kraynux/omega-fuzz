# Copyright (c) 2026 kraynux - Licence MIT
"""Ecran de progression : lance `start_scan()` dans un worker Textual, sans
bloquer l'UI (Phase 10d). Contrairement a omega-check (probers
synchrones enveloppes via `asyncio.to_thread`), `start_scan`/`run_scan`
sont deja des coroutines natives (httpx async) : `run_worker()` les
execute comme une Task sur la MEME boucle asyncio que l'UI — pas de
thread separe, donc pas besoin de `app.call_from_thread()` pour ecrire
dans un widget depuis le relais de logs (le callback s'execute deja sur
le thread UI).

Relais de logs : `container.logger` (StdlibLogger) ecrit sur
`logging.getLogger("omega_fuzz")` — un `logging.Handler` dedie y est
attache pour la duree du scan (detache dans un `finally`), meme
mecanisme que omega-check/interfaces/tui/screens/scan_progress.py.

Pas de "dashboard runtime" a compteurs ici (requetes/tests/findings en
temps reel) : `run_scan` ne remonte aujourd'hui aucun evenement de
progression incrementale exploitable pour ca (seuls les evenements de
decouverte sont logues, la phase de tests reste quasi silencieuse avant
la fin) — differe explicitement, chantier separe cote application/.

Phase 10g : bouton "Arreter" (demande explicite). `Worker.cancel()`
declenche un `asyncio.CancelledError` au prochain point d'attente
rencontre par `_run_scan()` (typiquement dans `HttpxHttpClient.send()`) —
propage normalement a travers toute la pile (`http_client` -> `run_scan`
-> `start_scan`), jamais avale : `CancelledError` derive de
`BaseException`, pas de `Exception`, donc ni le `except Exception` de ce
fichier ni celui de `httpx_http_client.py` ne l'interceptent."""
from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import Button

from omega_fuzz.application.commands.start_scan import start_scan
from omega_fuzz.interfaces.tui.screens.scan_results_screen import ScanResultsScreen
from omega_fuzz.interfaces.tui.widgets.progress_panel import ProgressPanel

if TYPE_CHECKING:
    from textual.worker import Worker

    from omega_fuzz.app.container import Container as AppContainer
    from omega_fuzz.app.container import ScanRuntime
    from omega_fuzz.application.commands.prepare_scan import PreparedScan


class _RelayHandler(logging.Handler):
    """Relaie chaque record du logger 'omega_fuzz' vers un callback — pas
    de formattage, juste le message (deja forme par StdlibLogger)."""

    def __init__(self, callback: Callable[[str], None]) -> None:
        super().__init__()
        self._callback = callback

    def emit(self, record: logging.LogRecord) -> None:
        self._callback(record.getMessage())


class ScanProgressScreen(Screen[None]):
    """Ecran transitoire : disparait des que le scan se termine (succes ->
    ScanResultsScreen remplace cet ecran ; echec/arret -> notification,
    retour a la revue)."""

    def __init__(
        self, *, prepared: PreparedScan, scan_runtime: ScanRuntime, container: AppContainer
    ) -> None:
        super().__init__()
        self._prepared = prepared
        self._scan_runtime = scan_runtime
        self._container = container
        self._worker: Worker[None] | None = None

    def compose(self) -> ComposeResult:
        stop_row = Horizontal(
            Container(Button("Arreter", id="stop", variant="error"), classes="omega-btn-frame"),
            classes="omega-actions",
        )
        yield ProgressPanel(
            message=f"Scan de {self._prepared.entry_url.to_str()} en cours...", extra=(stop_row,)
        )

    def on_mount(self) -> None:
        self._worker = self.run_worker(self._run_scan(), exclusive=True)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "stop" and self._worker is not None:
            self._worker.cancel()

    async def _run_scan(self) -> None:
        container = self._container
        logger = logging.getLogger("omega_fuzz")
        handler = _RelayHandler(self._on_log_record)
        logger.addHandler(handler)

        try:
            result = await start_scan(
                prepared=self._prepared,
                http_client=container.http_client,
                url_discoverer=container.url_discoverer,
                session_provider=self._scan_runtime.session_provider,
                response_analyzer=container.response_analyzer,
                security_headers_analyzer=container.security_headers_analyzer,
                test_plan_generator=container.test_plan_generator,
                scan_repository=container.scan_repository,
                finding_repository=container.finding_repository,
                confirmation_provider=self._scan_runtime.confirmation_provider,
                id_generator=container.id_generator,
                clock=container.clock,
                logger=container.logger,
            )
        except asyncio.CancelledError:
            self.app.notify("Scan arrete par l'utilisateur.", title="Scan interrompu")
            self.dismiss()
            return
        except Exception as exc:  # noqa: BLE001 - limite de worker, ne doit jamais planter l'UI
            self.app.notify(str(exc) or type(exc).__name__, title="Scan echoue", severity="error")
            self.dismiss()
            return
        finally:
            logger.removeHandler(handler)

        self.app.switch_screen(
            ScanResultsScreen(result=result, prepared=self._prepared, container=self._container)
        )

    def _on_log_record(self, message: str) -> None:
        if self.is_mounted:
            self.query_one(ProgressPanel).write_line(message)
