# Architecture

Resume operationnel — la reference complete est
`~/DEV/FUZZ/OMEGA-FUZZ_ARBORESCENCE.md` (a la racine du depot de
planification, hors de ce package).

## Regle de dependance

```text
app
  -> infrastructure | interfaces | plugins
       -> application
            -> ports
                 -> domain
                      -> core
```

Une couche ne peut importer que les couches strictement interieures.
`domain`/`core` ne connaissent ni HTTP, ni SQLite, ni Jinja, ni Textual,
ni argparse.

## Contrats `import-linter` (6, `pyproject.toml`)

1. Dependency Rule (`type = "layers"`).
2. `interfaces` independant de `infrastructure` (`type = "independence"`).
3. `httpx` confine a `infrastructure.network`.
4. `sqlite3` confine a `infrastructure.storage.sqlite`.
5. `jinja2` confine a `infrastructure.exporters.html_exporter`.
6. `textual` confine a `interfaces.tui`.

Verification : `lint-imports` (voir README.md).

## Ports = `typing.Protocol`

Tous les contrats de `ports/` sont des `typing.Protocol`, jamais des
`abc.ABC` — typage structurel, adaptateurs independants, contrats
facilement remplacables dans les tests. Une implementation documente le
port qu'elle respecte en docstring (`"""Implemente ports/xxx.py::Xxx."""`)
sans en heriter explicitement.

## Identifiants (D-006, decision E de la passe de coherence)

- `scan_id` : UUID via `omega_lib.shared.ids.new_id()`, conforme D-006 —
  jamais un format lisible reconstruit depuis la cible/date.
- `target_id`/`test_id`/`request_id` : scan-scopes, sequentiels et
  lisibles — pas soumis a D-006 (ce ne sont pas des identifiants racine
  d'agregat, un scan peut en compter des dizaines de milliers).

## Etat actuel (Phase 0 + Phase 1)

Seuls `core/`, `domain/targets/`, `domain/services/` (scope/depth/
normalisation URL) et le socle `app/`/`interfaces/cli/` minimal existent
reellement. Les autres couches sont scaffoldees vides (paquet
importable) et se remplissent phase par phase — voir
`OMEGA-FUZZ_PLAN_DEV.md` §5 pour l'ordre.
