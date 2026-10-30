# Copyright (c) 2026 kraynux - Licence MIT
"""Purge des exports / captures (correctif 2026-10-27, commun a la suite omega-*) : dossier
CONFIGURE vide (et relu par l'export), contenu seul supprime, liens non suivis, dossiers
dangereux refuses, elements non supprimables signales."""
from __future__ import annotations

import os
from pathlib import Path

import pytest
from textual.widgets import Button

from omega_fuzz.app.composition_root import build_container
from omega_fuzz.application.commands.clear_directory import (
    UnsafeDirectoryError,
    check_clearable,
    clear_directory,
)
from omega_fuzz.application.services.report_orchestrator import resolve_exports_dir

EXPORTS_DIR_KEY = "exports_dir_override"
SCREENSHOTS_DIR_KEY = "screenshots_dir_override"
from omega_fuzz.interfaces.tui.app import OmegaFuzzApp
from omega_fuzz.interfaces.tui.screens.confirm_screen import ConfirmScreen
from omega_fuzz.interfaces.tui.screens.settings_screen import SettingsScreen


def test_clears_content_keeps_folder_and_link_targets(tmp_path: Path) -> None:
    target = tmp_path / "exports"
    (target / "sub").mkdir(parents=True)
    (target / "a.html").write_text("x")
    (target / "sub" / "b.txt").write_text("y")
    outside = tmp_path / "garder.txt"
    outside.write_text("z")
    (target / "lien").symlink_to(outside)
    result = clear_directory(target, tmp_path / "app")
    assert (result.removed, result.failed) == (3, ())
    assert target.is_dir() and list(target.iterdir()) == []
    assert outside.exists()


@pytest.mark.parametrize("path", ["/", "/etc", "/home", "/home/quelquun", "/usr", "/root"])
def test_system_and_home_folders_refused(tmp_path: Path, path: str) -> None:
    with pytest.raises(UnsafeDirectoryError):
        check_clearable(Path(path), tmp_path / "app")


def test_application_root_and_parents_refused(tmp_path: Path) -> None:
    app_root = tmp_path / "app"
    for path in (app_root, tmp_path):
        with pytest.raises(UnsafeDirectoryError):
            check_clearable(path, app_root)


@pytest.mark.skipif(os.geteuid() == 0, reason="root ignore les droits")
def test_undeletable_entry_reported_others_removed(tmp_path: Path) -> None:
    target = tmp_path / "exports"
    locked = target / "verrou"
    locked.mkdir(parents=True)
    (locked / "f").write_text("x")
    (target / "libre.txt").write_text("x")
    locked.chmod(0o500)
    try:
        result = clear_directory(target, tmp_path / "app")
    finally:
        locked.chmod(0o700)
    assert result.removed == 1 and len(result.failed) == 1 and "verrou" in result.failed[0]


def test_purge_uses_same_folder_as_exports(tmp_path: Path) -> None:
    container = build_container(var_dir=tmp_path / "var", console_logging=False)
    store = container.settings_store
    assert resolve_exports_dir(settings_store=store, default_exports_dir=container.default_exports_dir) \
        == container.default_exports_dir
    store.set(EXPORTS_DIR_KEY, str(tmp_path / "ailleurs"))
    assert resolve_exports_dir(settings_store=store, default_exports_dir=container.default_exports_dir) \
        == tmp_path / "ailleurs"


async def _purge(tmp_path: Path, key: str, button: str, configured: Path | None, confirm: bool):
    container = build_container(var_dir=tmp_path / "var", console_logging=False)
    if configured is not None:
        container.settings_store.set(key, str(configured))
    app = OmegaFuzzApp(container, scan_runtime_factory=lambda _path: None)  # type: ignore[arg-type,return-value]
    async with app.run_test(size=(120, 45)) as pilot:
        await pilot.pause()
        app.push_screen(SettingsScreen(container=container))
        await pilot.pause()
        app.screen.query_one(f"#{button}", Button).press()
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        message = str(app.screen._message)
        app.screen.query_one("#confirm" if confirm else "#cancel", Button).press()
        await pilot.pause()
        await app.workers.wait_for_complete()
        await pilot.pause()
        notes = [n.message for n in app._notifications]
    return container, message, notes


async def test_clear_exports_empties_configured_folder_not_default(tmp_path: Path) -> None:
    custom = tmp_path / "mes-exports"
    custom.mkdir()
    (custom / "vieux.html").write_text("x")
    default = tmp_path / "var" / "exports"
    default.mkdir(parents=True)
    (default / "garder.html").write_text("x")
    _container, message, _notes = await _purge(tmp_path, EXPORTS_DIR_KEY, "clear-exports", custom, True)
    assert str(custom) in message
    assert list(custom.iterdir()) == []
    assert (default / "garder.html").exists()


async def test_clear_screenshots_cancelled_keeps_files(tmp_path: Path) -> None:
    shots = tmp_path / "var" / "screenshots"
    shots.mkdir(parents=True)
    (shots / "shot.svg").write_text("<svg/>")
    await _purge(tmp_path, SCREENSHOTS_DIR_KEY, "clear-screenshots", None, False)
    assert (shots / "shot.svg").exists()


async def test_clear_refuses_system_folder(tmp_path: Path) -> None:
    _container, _message, notes = await _purge(tmp_path, EXPORTS_DIR_KEY, "clear-exports", Path("/etc"), True)
    assert any("Dossier refusé" in n for n in notes), notes
