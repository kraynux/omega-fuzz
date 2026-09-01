# Copyright (c) 2026 kraynux - Licence MIT
"""Dispatch CLI (OMEGA-FUZZ_ARBORESCENCE.md §27) : parse les arguments
via `parser.py`, construit le `ScanRuntime` propre a la sous-commande
via `scan_runtime_factory` (injecte par `app/main.py` — les adaptateurs
qu'il construit vivent dans `infrastructure`/`interfaces.cli.prompts`,
que cette couche ne peut pas importer elle-meme, Dependency Rule),
delegue a `commands/scan_command.py`, presente les erreurs sans
traceback brute."""
from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from omega_fuzz.core.constants import CLI_EXIT_ERROR
from omega_fuzz.core.errors import OmegaFuzzError
from omega_fuzz.domain.targets.url import UrlNormalizationError
from omega_fuzz.interfaces.cli.parser import build_parser
from omega_fuzz.interfaces.cli.presenters.error_presenter import render_error

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from omega_fuzz.app.container import Container, ScanRuntime


def run(
    container: Container,
    argv: list[str] | None,
    *,
    scan_runtime_factory: Callable[[Path | None], ScanRuntime],
) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "scan":
        from omega_fuzz.interfaces.cli.commands.scan_command import run as run_scan_command

        try:
            scan_runtime = scan_runtime_factory(args.auth_config)
            return run_scan_command(container, args, scan_runtime)
        except (OmegaFuzzError, UrlNormalizationError) as error:
            message, exit_code = render_error(error)
            print(message, file=sys.stderr)
            return exit_code

    print(f"omega-fuzz : commande inconnue : {args.command}", file=sys.stderr)
    return CLI_EXIT_ERROR
