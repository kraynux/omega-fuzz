# Copyright (c) 2026 kraynux - Licence MIT
"""Construction du parseur CLI (OMEGA-FUZZ_ARBORESCENCE.md §27). N'importe
que `core`/`domain` (enums de profils) et la bibliotheque standard —
aucune dependance a `infrastructure`, conforme a la Dependency Rule
(`interfaces ne dependent jamais directement de infrastructure`).

Options exposees limitees a celles qui ont un effet reel dans le
backend actuel (Phase 10b) : pas de `--max-depth` (non surchargeable
individuellement depuis la resolution de profils, Phase 5) ni de
`--respect-rate-limit-signals` (`rate_limit_backoff_service` existe
mais n'est cable dans aucun orchestrateur — gap preexistant, hors
scope de cette tranche)."""
from __future__ import annotations

import argparse
from pathlib import Path

from omega_lib.theme.policies import DEFAULT_EXPORT_THEME, EXPORT_PALETTES

from omega_fuzz.core.version import __version__
from omega_fuzz.domain.profiles.aggressiveness_level import AggressivenessLevel
from omega_fuzz.domain.profiles.preset import PresetName
from omega_fuzz.domain.profiles.scope_profile import ScopeProfileName


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="omega-fuzz",
        description="Decouverte et tests de securite web (fuzzing HTTP).",
    )
    parser.add_argument("--version", action="version", version=f"omega-fuzz {__version__}")

    subparsers = parser.add_subparsers(dest="command", required=True)
    _add_scan_subcommand(subparsers)

    return parser


def _add_scan_subcommand(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    scan_parser = subparsers.add_parser(
        "scan", help="Lance une decouverte + des tests de securite sur une cible."
    )
    scan_parser.add_argument("--target", required=True, metavar="URL", help="URL cible du scan.")
    scan_parser.add_argument(
        "--preset", choices=[preset.value for preset in PresetName], help="Preset pret a l'emploi."
    )
    scan_parser.add_argument(
        "--scope-profile",
        choices=[profile.value for profile in ScopeProfileName],
        help="Profil de scope (a combiner avec --aggressiveness, sans --preset).",
    )
    scan_parser.add_argument(
        "--aggressiveness",
        choices=[level.value for level in AggressivenessLevel],
        help="Niveau d'agressivite (a combiner avec --scope-profile, sans --preset).",
    )
    scan_parser.add_argument(
        "--auth-config",
        type=Path,
        metavar="CHEMIN",
        help="Fichier YAML d'authentification (jamais d'identifiants en clair sur la ligne "
        "de commande).",
    )
    scan_parser.add_argument(
        "--insecure-tls",
        action="store_true",
        help="Desactive la verification TLS (declenche une confirmation renforcee).",
    )
    scan_parser.add_argument("--max-duration", type=int, metavar="SECONDES")
    scan_parser.add_argument("--max-requests", type=int, metavar="N")
    scan_parser.add_argument("--max-tests", type=int, metavar="N")
    scan_parser.add_argument("--max-concurrent", type=int, metavar="N")
    scan_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Affiche la configuration effective et le plan estime, n'emet aucune requete.",
    )
    scan_parser.add_argument(
        "--output-dir",
        type=Path,
        metavar="DOSSIER",
        help="Dossier des rapports exportes, nommes <preset>-<horodatage>.<ext> "
        "(defaut : ./var/exports/, surchargeable dans Reglages).",
    )
    scan_parser.add_argument(
        "--format",
        choices=["json", "markdown", "html", "all"],
        default="all",
        help="Format(s) de rapport exporte(s) (defaut : all).",
    )
    scan_parser.add_argument(
        "--export-theme",
        choices=sorted(EXPORT_PALETTES),
        default=DEFAULT_EXPORT_THEME,
        help=f"Theme du rapport HTML exporte (sans effet sur json/markdown, defaut : "
        f"{DEFAULT_EXPORT_THEME}).",
    )
