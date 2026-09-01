# Copyright (c) 2026 kraynux - Licence MIT
"""Point d'entree du programme (OMEGA-FUZZ_ARBORESCENCE.md §4.3) :
choisit CLI ou TUI, transmet le controle a la composition. Un lancement
sans argument ouvre le TUI (Phase 10c) ; au moins un argument delegue a
la CLI, meme patron que le reste de la suite (omega-check `__main__.py`)."""
from __future__ import annotations

import sys


def main(argv: list[str] | None = None) -> int:
    from omega_fuzz.app.composition_root import (
        build_container,
        build_scan_runtime,
        build_tui_scan_runtime,
    )

    effective_argv = sys.argv[1:] if argv is None else argv
    is_tui = not effective_argv

    # console_logging=False sous le TUI : Textual controle l'ecran en mode
    # alternatif, une ecriture de log directe sur stderr corromprait son
    # rendu (voir infrastructure/logging.py::StdlibLogger).
    container = build_container(console_logging=not is_tui)

    if is_tui:
        from omega_fuzz.interfaces.tui.app import OmegaFuzzApp

        OmegaFuzzApp(
            container,
            scan_runtime_factory=lambda auth_config_path: build_tui_scan_runtime(
                auth_config_path, container=container
            ),
        ).run()
        return 0

    from omega_fuzz.interfaces.cli.main import run as run_cli

    return run_cli(
        container,
        effective_argv,
        scan_runtime_factory=lambda auth_config_path: build_scan_runtime(
            auth_config_path, container=container
        ),
    )
