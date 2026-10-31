<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - MIT License (see LICENSE file) -->
<div align="center">
  <img src="../../assets/omega-fuzz.png" alt="Omega-Fuzz" width="384">
</div>

# 🗱 OMEGA-FUZZ

**Vulnerability scanner**

> Built by [kraynux](https://github.com/kraynux) for [Omega-Server](https://kraynux.snake-mackarel.ts.net)   

Official page: [OMEGA-FUZZ](https://kraynux.snake-mackarel.ts.net/omega-fuzz/) &nbsp; Preview: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-fuzz/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

🌐 Interface and exported reports available in **17 languages** — see [Interface languages](#interface-languages).  
**Languages:**  
<img src="https://flagcdn.com/w20/fr.png" alt="Français" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)

**Omega-Fuzz** is a local terminal application ([Textual](https://github.com/Textualize/textual) TUI + scriptable CLI) that drives web discovery and security testing (HTTP fuzzing) for authorized environments (labs, personal mirrors, explicitly consented test engagements).

A tool of the `omega-` suite, built on Clean Architecture — see `docs/ARCHITECTURE.md` for the full technical details.

## 1. Vision and scope

### What Omega-Fuzz does

- Discovers the perimeter of a single target with a BFS bounded by an explicit scope (scheme/subdomains/allowed-blocked paths/depth), never without safeguards.
- Generic fuzzing of the query string parameters, HTTP headers and `GET` forms found on each discovered URL, and checks three families of signatures: non-destructive reflected XSS, generic injection (error detection in the response), missing/misconfigured security headers — see [§5](#5-security-tests-performed).
- Scores each anomaly on 3 axes (impact/exploitability/reach) and derives a severity from it (`low`/`medium`/`high`/`critical`), deduplicated by `(type, endpoint, parameter)` while keeping the best evidence — see [§6](#6-score-and-severity).
- Supports authentication (cookie, bearer token, login form) through a dedicated YAML file, never with plain-text credentials on the command line.
- Presents the result in the TUI (Textual) or in the scriptable CLI, with three exports (JSON, Markdown, HTML with 5 themes).
- Keeps a persistent history of scans and their findings (SQLite), and a list of reusable favorite targets.
- Requires an explicit confirmation (a strict phrase for the most sensitive cases) before any aggressive or extended scan, or any scan with TLS verification disabled.

### What Omega-Fuzz does not do

- Fuzzing of JSON bodies — the code exists (`plugins/fuzzers/json_body_fuzzer.py`) but is not wired in (HTML/BFS discovery produces no JSON API schema and no usable template source).
- Fuzzing of `POST`/`PUT`/`DELETE` forms — excluded from the automatic pipeline by choice (risk of unwanted writes on the target); only `GET` forms are tested.
- Business logic tests (IDOR, authorization checks, workflow breaking) — the code exists (`plugins/logic_tests/`) but stays outside the automatic pipeline, can only be invoked separately, and is never triggered by a standard scan.
- Parallel multi-target scanning — a single target per scan.
- Replay, comparison or export from the History screen — only `Scan` and `Finding` are persisted (not the full effective configuration nor the requests), so replaying or exporting again from the history would make up data; the screen explains this instead of silently offering it.
- Client-side JavaScript rendering (the page is fetched as served, not executed in a headless browser).
- Web dashboard.

## 2. Installation

### Requirements

- Python 3.10+
- Internet connection, for the dependencies
- For the TUI: a [Nerd Font](https://www.nerdfonts.com/) installed in the terminal, for the header icon — without it, this character renders as an empty box (same limitation as an emoji, but far more widely available among terminal users). Its absence has no effect on how the tool works, it is purely cosmetic.

### Installation

```bash
[ -d omega-fuzz ] && echo "ℹ️ Already extracted here, step skipped." || tar -xzf omega-fuzz.tar.gz
cd omega-fuzz/
chmod +x install.sh
./install.sh
```

`install.sh`:

1. Creates the `.venv` virtual environment if it does not already exist.
2. Installs the dependencies (`vendor/omega-lib/` then `pip install -e .`, `pyproject.toml` remains the single source of truth).
3. Makes `omega-fuzz.sh` and `install.sh` executable.
4. Adds the `fuzz` alias to `~/.bashrc` and `~/.zshrc` (no duplicate if already present).

### Dependencies

Declared in `pyproject.toml` (no `requirements.txt`):
- `omega-lib`: shared library of the suite (export themes, terminal detection, `ConfidenceLevel`) — vendored in `vendor/omega-lib/`
- `httpx`: asynchronous HTTP requests (discovery + fuzzing), streaming of the response (never a full buffer in memory, even for a multi-GB file served by the target)
- `beautifulsoup4` + `lxml`: extraction of HTML URLs and forms
- `jinja2`: templating for the HTML export
- `textual`: TUI interface, themes, automatic adaptation to the terminal
- `pyyaml`: loading of the `--auth-config` file
- Development dependencies (`pip install -e ".[dev]"`): `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-httpserver`, `ruff`, `mypy`, `import-linter`

## 3. Usage

### Interactive mode (TUI)

Recommended for daily use — launched without arguments:

```bash
./omega-fuzz.sh
```
if you created the alias, just type `fuzz` in the terminal:
```bash
fuzz
```

Flow: splash screen (closes on a key press or a click) → main menu (Scan / Targets / Settings / History / Help) → target input (full URL, `http://`/`https://` scheme required), preset or manual configuration (scope + aggressiveness), optional authentication, TLS verification, limit overrides → review screen (simple confirmation, or the strict phrase `OUI-J-AI-L-AUTORISATION` for sensitive cases) → scan (indeterminate gauge, **Stop** button at any time) → results (findings, export) → history (details of a past scan, associated findings) and favorite targets from the main menu. Adaptation to the terminal (colors, size, structural degradation) is automatic.

#### Keyboard shortcuts

| Key | Action |
|---|---|
| `↑` / `↓` | Move between the items of a screen |
| `Tab` / `Shift+Tab` | Move between the fields of a form |
| `Esc` | Back to the previous screen (exit confirmation on the home screen) |
| `t` | Next theme (applied immediately, without confirmation) |
| `r` | Refresh terminal detection |
| `a` | Show the help (presets table included) |
| `q` | Quit (with confirmation) |
| `Ctrl+P` | Command palette (Theme, Quit, Screenshot) |

### Interface languages

The interface is available in 17 languages: French, English, Spanish, Portuguese (Brazil), Italian, German, Dutch, Polish, Russian, Simplified Chinese, Vietnamese, Thai, Indonesian, Japanese, Korean, Hindi and Arabic. The choice is made in Settings ("Langue / Language") and applies after the interface restarts; the `OMEGA_FUZZ_LANG` variable (for example `OMEGA_FUZZ_LANG=en ./omega-fuzz.sh`) forces a language for one session. When launched from omega-suite, omega-fuzz uses the suite's language. On a Linux text console (TTY), languages with a non-Latin script are displayed in English for the session. The command line stays in French.

### Scriptable mode (CLI)

```bash
# Scan with a ready-to-use preset
./omega-fuzz.sh scan --target https://example.com --preset prod-safe

# Manual scope + aggressiveness combination (without a preset)
./omega-fuzz.sh scan --target https://example.com --scope-profile standard --aggressiveness standard

# With authentication (YAML file, never plain-text credentials on the command line)
./omega-fuzz.sh scan --target https://example.com --preset staging-full --auth-config auth.yaml

# Dry-run: effective configuration and estimated plan, no request sent
./omega-fuzz.sh scan --target https://example.com --preset prod-safe --dry-run

# Targeted export (folder, formats, HTML theme)
./omega-fuzz.sh scan --target https://example.com --preset prod-safe \
    --output-dir ./rapports --format html --export-theme omega-neon
```

`scan` options:

| Option | Default | Effect |
|---|---|---|
| `--target` | *(required)* | Target URL, `http://`/`https://` scheme required (never completed automatically) |
| `--preset` | — | Ready-to-use preset (see [§4](#4-scope-profiles-and-presets)) |
| `--scope-profile` | — | Scope profile, to combine with `--aggressiveness`, without `--preset` |
| `--aggressiveness` | — | Aggressiveness level, to combine with `--scope-profile`, without `--preset` |
| `--auth-config` | — | Authentication YAML file |
| `--insecure-tls` | disabled | Disables TLS verification (triggers the reinforced confirmation) |
| `--max-duration` | *(from the profile)* | Overrides the maximum duration (seconds) |
| `--max-requests` | *(from the profile)* | Overrides the maximum number of requests |
| `--max-tests` | *(from the profile)* | Overrides the maximum number of tests |
| `--max-concurrent` | *(from the profile)* | Overrides the maximum concurrency |
| `--dry-run` | disabled | Shows the effective configuration and the estimated plan, sends no request |
| `--output-dir` | `var/exports/` | Folder of the exported reports, named `<preset>-<timestamp>.<ext>` (can be overridden in Settings) |
| `--format` | `all` | `json`, `markdown`, `html` or `all` |
| `--export-theme` | `omega-base` | Theme of the exported HTML report (no effect on json/markdown) |

There is no `history`/`show` subcommand in the CLI: the history and the favorite targets can only be viewed from the TUI.

If the alias was created by `install.sh`, `fuzz scan ...` works from anywhere in the terminal, without the `./omega-fuzz.sh` prefix.

## 4. Scope profiles and presets

### Scope profiles

| Profile | Mode | Max depth | Restrictions |
|---|---|---|---|
| `strict` | exact target | 1 | Blocks `/health`, `/ready`, `/metrics`, `/favicon.ico`, `/robots.txt` |
| `standard` | + subdomains | 2 | Blocks common static subdomains, technical paths, assets (images/css/js/fonts) |
| `large` | + subdomains | 4 | Blocks only technical paths and assets (including archives/PDF) |
| `api` | exact target | 3 | Restricted to `/api`, `/v1`, `/v2`; blocks documentation and assets |
| `custom` | + subdomains | 3 | No restriction by default — starting point for a manual configuration |

Whatever the chosen profile, a list of binary/large file extensions (`.iso`, `.zip`, `.exe`, `.mp4`...) is **always** excluded from crawling and fuzzing, even under `custom` — a link to a file of this kind is never fetched by a real HTTP request, so that a downloads folder does not slow a scan down for long minutes.

### Aggressiveness levels

`doux` · `standard` · `agressif` · `violent` — each one carries its own base limits (duration, requests, tests, depth, concurrency), overridden by a preset when there is one.

### Ready-to-use presets

| Preset | Scope | Aggressiveness | Max duration | Max requests | Max tests | Max depth | Reinforced confirmation |
|---|---|---|---|---|---|---|---|
| `prod-safe` | strict | doux | 300 s | 1,000 | 500 | 1 | no |
| `staging-full` | standard | standard | 1,800 s | 20,000 | 10,000 | 2 | no |
| `lab-deep` | large | agressif | 3,600 s | 100,000 | 50,000 | 4 | no |
| `lab-extreme` | large | violent | 7,200 s | 500,000 | 250,000 | 5 | **yes** |
| `api-hardened` | api | agressif | 1,800 s | 50,000 | 25,000 | 3 | no |

A scan stays blocked until it is confirmed. A **reinforced** confirmation (the exact phrase `OUI-J-AI-L-AUTORISATION` to type) is required as soon as one of these three factors is present: `violent` aggressiveness, the `lab-extreme` preset, or TLS verification disabled (`--insecure-tls`) — for an unusual combination without any of these three factors, a simple yes/no confirmation.

## 5. Security tests performed

Automatic pipeline, on each URL discovered within the scope (and each `GET` form found there):

| Test | Trigger | What is checked |
|---|---|---|
| Generic parameter fuzzing | any query string parameter | Behavior of the target facing boundary/malformed values |
| Header fuzzing | once per URL, 4 fixed headers (`User-Agent`, `Referer`, `X-Forwarded-For`, `Accept-Language`) | Behavior of the target facing boundary/malformed values in a header |
| Form fuzzing (`GET` only) | any `GET` form field discovered within the scope | Behavior of the target facing boundary/malformed values in a form field |
| Reflected XSS | any query string parameter | Unfiltered reflection of a payload in the response (non-destructive) |
| Generic injection | any query string parameter | Detection of a server error in response to an injection payload (no specific SQL/NoSQL fingerprint) |
| Security headers | once per URL | Missing or misconfigured security headers in the response |

The first three tests (generic parameter/header/form fuzzing) are a mutation engine **without detection** — they never produce a `Finding` directly, only the server errors (5xx) encountered are counted on the corresponding `Test`. Only the signatures (XSS, injection, security headers) generate findings.

## 6. Score and severity

Each detected anomaly is rated on 3 axes (`impact`, `exploitability`, `reach`, 1 to 5 each) according to the nature of the observation — a deliberately **conservative** mapping (low end of the range, no human confirmation at this automatic stage):

| Raw score (sum of the 3 axes) | Severity |
|---|---|
| ≥ 13 | `critical` |
| ≥ 10 | `high` |
| ≥ 7 | `medium` |
| < 7 | `low` |

A manual adjustment (`severity_override`) remains possible but always requires an explicit justification. Equivalent findings (same type, same endpoint, same parameter) are deduplicated, keeping the best available evidence (confidence level `omega_lib.core.confidence.ConfidenceLevel`, then raw score in case of a tie).

## 7. Authentication

Dedicated YAML file (`--auth-config`), never plain-text credentials on the command line:

| Mode | Effect |
|---|---|
| `none` | No authentication (default) |
| `cookie` | Session cookie provided directly |
| `bearer_token` | `Authorization: Bearer ...` token |
| `login_form` | Form-based authentication (login URL, user/password fields) |

## 8. Architecture

Omega-Fuzz is built on **Clean Architecture** (domain / application / infrastructure / interfaces / ports / core / app / plugins), aligned with the template of the `omega-` suite (see `omega-check`/`omega-deep`/`omega-fold`) and checked by `import-linter` on every change. The full details live in **`docs/ARCHITECTURE.md`**.

Very short overview:

```text
src/omega_fuzz/
├── domain/          Pure business logic (targets/scope, requests, tests, findings, profiles, reports...)
├── application/     Use cases (commands/queries) and orchestrators (discovery, scan, report, limits)
├── ports/           Contracts expected by the application (http_client, repositories, exporters...)
├── infrastructure/  Concrete implementations (httpx, BeautifulSoup, SQLite, Jinja2 exporters — Textual is NOT here)
├── interfaces/      tui/ (Textual) and cli/ (scriptable), with strict functional parity
├── plugins/         Fuzzers and signatures (pure functions, never direct network access)
├── app/             Assembly (Container, composition root, lifecycle)
└── core/            Cross-cutting vocabulary, errors, constants
```

Design rules:
- `plugins/fuzzers/` and `plugins/signatures/`: pure functions that build test plans (`Test` + `ScanRequest`), never touch `HttpClient`.
- `infrastructure/network/`: does the networking (`httpx`, memory-bounded streaming), never judges.
- `infrastructure/analyzers/`: reads an already received response, produces structured `Observation` objects, never recomputes a score.
- `interfaces/`: displays, contains no business logic.

## 9. Exports

Markdown and HTML reports are written in the language chosen in Settings ("Export language", by default the interface language); JSON stays data and is not translated. Reports are generated in `var/exports/` by default (runtime path anchored on the project folder, `$OMEGA_FUZZ_VAR_DIR` to override it, can also be overridden in the Settings screen), or at the given path (`--output-dir`). Flat file name, without a subfolder: `<preset>-<timestamp>.<ext>` (e.g. `prod-safe-2026-09-01_14-30-22.html`).

### JSON, source of truth

Full structure of the report (effective configuration, statistics, tests, findings), strictly JSON-serializable.

### Markdown, compact human report

Readable outside the terminal, without ANSI codes.

### HTML, standalone web report

5 themes to choose from (`--export-theme` in the CLI, selector in the TUI): `omega-base`, `omega-burn`, `omega-neon`, `light-basic`, `light-alt`.

## 10. History and favorite targets

Each scan is persisted (SQLite, `var/db/omega-fuzz.db`) with its findings and can be viewed from the History screen of the TUI. Only `Scan` and `Finding` are stored — not the effective configuration nor the detailed requests — so there is no replay, comparison or new export from this screen (the screen explains this instead of making up data).

The **Targets** screen keeps a list of favorites (normalized URLs, `var/targets.json`), reusable to prefill the Target field of a new scan directly.

## 11. Screenshots

**Screenshot** command of the palette (`Ctrl+P`): saves an SVG of the current TUI screen in `var/screenshots/` by default, can be overridden in the Settings screen (like the export folder). A dedicated purge is available in Settings.

## 12. Terminal compatibility

The TUI (Textual) automatically detects the terminal's capabilities (emulator, size) and adapts its structural stylesheet accordingly (`complete`/`standard`/`reduced`/`mono`), without a manual flag. CLI mode always stays plain text, independent of the terminal. Policy shared by the whole `omega-` suite (`omega-lib`, `terminal/policies.py`).

### Profile by detected emulator

| Emulator | Initial profile |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | `complete` |
| Konsole, GNOME Terminal, Terminator, Xfce4 Terminal | `standard` |
| xterm, urxvt, modern SSH | `reduced` |
| Linux TTY, legacy SSH | `mono` |
| Unrecognized emulator | `reduced` (default fallback) |

### Profile by terminal size

| Minimum size (columns × rows) | Profile ceiling |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| below | `mono` |

The final profile retained is **the more restrictive of the two** (emulator and size) — can be refreshed live with the `r` key.

## 13. Tests

```bash
source .venv/bin/activate
lint-imports        # checks the Dependency Rule (6 contracts)
pytest -q           # 344 tests
ruff check src tests
mypy -p omega_fuzz
```

Structure: `tests/unit/` (domain and application, no real I/O), `tests/integration/` (real filesystem via `tmp_path`, fake HTTP server `pytest-httpserver`, real SQLite database, end-to-end CLI), `tests/tui/` (navigation via `Pilot`, structural — no self-claimed visual verification).

## 14. Out of scope

- Fuzzing of JSON bodies (code present, not wired in — no API schema discovery)
- Fuzzing of `POST`/`PUT`/`DELETE` forms (excluded by choice, risk of writes)
- Business logic tests (IDOR, authorization, workflow) outside manual invocation
- Simultaneous multi-target scanning
- Replay, comparison or export from the history
- Client-side JavaScript rendering
- Web dashboard

---

> Omega-Fuzz — Discover a perimeter, test it with explicit safeguards, never guess what has not been confirmed.
