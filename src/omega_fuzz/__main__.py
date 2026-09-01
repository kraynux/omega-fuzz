# Copyright (c) 2026 kraynux - Licence MIT
"""Support `python -m omega_fuzz` — delegue a app/main.py (point
d'entree logique, voir OMEGA-FUZZ_ARBORESCENCE.md §4.3). Le script
console `omega-fuzz` (pyproject.toml) pointe directement sur
`omega_fuzz.app.main:main`, ce fichier n'est utile que pour `-m`."""
from __future__ import annotations

from omega_fuzz.app.main import main

if __name__ == "__main__":
    raise SystemExit(main())
