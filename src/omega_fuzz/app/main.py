# Copyright (c) 2026 kraynux - Licence MIT
"""Point d'entree du programme (OMEGA-FUZZ_ARBORESCENCE.md §4.3) :
choisit CLI ou TUI, transmet le controle a la composition. Un lancement
sans argument ouvre le TUI (Phase 10c) ; au moins un argument delegue a
la CLI, meme patron que le reste de la suite (omega-check `__main__.py`)."""
from __future__ import annotations

import sys


def install_language() -> None:
    """Langue de l'interface installee AVANT d'importer la TUI (plan i18n de la suite §5) :
    les textes traduits au chargement d'un module (raccourcis, titres) sont deja dans la
    bonne langue. Jamais pour la ligne de commande (R3 : elle reste en francais)."""
    import os

    from omega_lib.infrastructure.terminal.detector import SystemTerminalDetector

    from omega_fuzz.infrastructure.config import paths
    from omega_fuzz.infrastructure.storage.files.json_settings_store import JsonSettingsStore
    from omega_fuzz.shared.i18n import LANGUAGE

    LANGUAGE.install(
        settings_store=JsonSettingsStore(paths.default_settings_path(paths.resolve_var_dir())),
        environ=os.environ,
        terminal_family=SystemTerminalDetector().detect().family,
    )


def restart_for_language(code: str) -> None:  # pragma: no cover - remplace le processus
    """Meme Python, meme module : seule l'interface redemarre, dans la langue choisie."""
    import os

    from omega_fuzz.shared.i18n import LANGUAGE

    LANGUAGE.prepare_restart_environment(os.environ, code)
    os.execv(sys.executable, [sys.executable, "-m", "omega_fuzz"])


def main(argv: list[str] | None = None) -> int:
    effective_argv = sys.argv[1:] if argv is None else argv
    is_tui = not effective_argv
    if is_tui:
        install_language()

    from omega_fuzz.app.composition_root import (
        build_container,
        build_scan_runtime,
        build_tui_scan_runtime,
    )

    # console_logging=False sous le TUI : Textual controle l'ecran en mode
    # alternatif, une ecriture de log directe sur stderr corromprait son
    # rendu (voir infrastructure/logging.py::StdlibLogger).
    container = build_container(console_logging=not is_tui)

    if is_tui:
        from omega_fuzz.interfaces.tui.app import OmegaFuzzApp

        tui = OmegaFuzzApp(
            container,
            scan_runtime_factory=lambda auth_config_path: build_tui_scan_runtime(
                auth_config_path, container=container
            ),
        )
        tui.run()
        if tui.pending_language is not None:
            restart_for_language(tui.pending_language)
        return 0

    from omega_fuzz.interfaces.cli.main import run as run_cli

    return run_cli(
        container,
        effective_argv,
        scan_runtime_factory=lambda auth_config_path: build_scan_runtime(
            auth_config_path, container=container
        ),
    )
