<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - MIT License (see LICENSE file) -->
<div align="center">
  <img src="docs/assets/omega-fuzz.png" alt="Omega-Fuzz" width="256">
</div>

# 🗱 OMEGA-FUZZ

**Vulnerability scanner**

> Developed by **kraynux** for **Omega-server**  
[https://kraynux.snake-mackarel.ts.net](https://kraynux.snake-mackarel.ts.net)

Official page: [OMEGA-FUZZ](https://kraynux.snake-mackarel.ts.net/omega-fuzz/) &nbsp; Preview: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-fuzz/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

**Languages:**  
[Français](README.md) · [English](README.en.md) · [Español](README.es.md) · [Русский](README.ru.md) · [中文](README.zh-CN.md)

**Omega-Fuzz** is a local terminal application (Textual TUI + scriptable CLI) that performs web discovery and security testing (HTTP fuzzing) for authorized environments (labs, personal mirrors, and explicitly authorized testing engagements).

The sixth tool in the `omega-` suite (after `omega-scan`, `omega-stress`, `omega-check`, `omega-deep`, and `omega-fold`), structured according to Clean Architecture — see `docs/ARCHITECTURE.md` for the complete technical details.

## 1. Vision and scope

### What Omega-Fuzz does

- Discovers the scope of a single target using BFS bounded by an explicit scope (scheme/subdomains/allowed-blocked paths/depth), never without safeguards.
- Performs generic fuzzing of query-string parameters, HTTP headers, and `GET` forms found on each discovered URL, and checks three signature families: non-destructive reflected XSS, generic injection (response error detection), and missing/misconfigured security headers — see [§5](#5-security-tests-performed).
- Scores each anomaly across three axes (impact/exploitability/scope) and derives a severity (`low`/`medium`/`high`/`critical`), deduplicated by `(type, endpoint, parameter)` while retaining the best evidence — see [§6](#6-scoring-and-severity).
- Supports authentication (cookie, bearer token, login form) through a dedicated YAML file; credentials are never placed in the command line.
- Presents results through the TUI (Textual) or a scriptable CLI, with three export formats (JSON, Markdown, and HTML with 5 themes).
- Keeps a persistent history of scans and their findings (SQLite), along with a reusable list of favorite targets.
- Requires explicit confirmation (a strict phrase for the most sensitive cases) before any aggressive or extended scan, or any scan with TLS verification disabled.

### What Omega-Fuzz does not do

- JSON body fuzzing — the code exists (`plugins/fuzzers/json_body_fuzzer.py`) but is not wired in (HTML/BFS discovery produces no JSON API schema and no usable template source).
- Fuzzing of `POST`/`PUT`/`DELETE` forms — excluded by design from the automatic pipeline (risk of unwanted writes on the target); only `GET` forms are tested.
- Business-logic tests (IDOR, authorization checks, workflow breaks) — the code exists (`plugins/logic_tests/`) but remains outside the automatic pipeline and can only be invoked separately; it is never triggered by a standard scan.
- Parallel multi-target scanning — one target per scan.
- Replay, comparison, or export from the History screen — only `Scan` and `Finding` are persisted (not the complete effective configuration or requests); replaying or exporting again from history would fabricate data, so the screen explains this instead of silently offering it.
- Client-side JavaScript rendering (the page is retrieved as served, not executed in a headless browser).
- Web dashboard.

## 2. Installation

### Prerequisites

- Python 3.10+
- Internet connection for dependencies
- For the TUI: a [Nerd Font](https://www.nerdfonts.com/) installed in the terminal for the header icon — without it, this character appears as an empty square (the same limitation as an emoji, but much more widely available among terminal users). Its absence has no effect on operation and is purely cosmetic.

### Installation

```bash
[ -d omega-fuzz ] && echo "ℹ️ Already extracted here, step skipped." || tar -xzf omega-fuzz.tar.gz
cd omega-fuzz/
chmod +x install.sh
./install.sh
```

`install.sh`:

1. Creates the `.venv` virtual environment if it does not already exist.
2. Installs the dependencies (`vendor/omega-lib/` followed by `pip install -e .`; `pyproject.toml` remains the single source of truth).
3. Makes `omega-fuzz.sh` and `install.sh` executable.
4. Adds the `fuzz` alias to `~/.bashrc` and `~/.zshrc` (without duplicates if it is already present).

### Dependencies

Declared in `pyproject.toml` (there is no `requirements.txt`):
- `omega-lib`: shared suite library (export themes, terminal detection, `ConfidenceLevel`) — vendored in `vendor/omega-lib/`
- `httpx`: asynchronous HTTP requests (discovery + fuzzing), response streaming (never a full in-memory buffer, even for a multi-GB file served by the target)
- `beautifulsoup4` + `lxml`: extraction of URLs and HTML forms
- `jinja2`: templating for HTML export
- `textual`: TUI, themes, and automatic terminal adaptation
- `pyyaml`: loading of the `--auth-config` file
- Development dependencies (`pip install -e ".[dev]"`): `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-httpserver`, `ruff`, `mypy`, `import-linter`

## 3. Usage

### Interactive mode (TUI)

Recommended for daily use — launched without arguments:

```bash
./omega-fuzz.sh
```
If you created the alias, simply type `fuzz` in the terminal:
```bash
fuzz
```

Flow: start screen (closes on a key press or click) → main menu (Scanner / Targets / Settings / History / Help) → target input (complete URL, `http://`/`https://` scheme required), preset or manual configuration (scope + aggressiveness), optional authentication, TLS verification, limit overrides → review screen (simple confirmation, or the strict phrase `OUI-J-AI-L-AUTORISATION` for sensitive cases) → scan (indeterminate gauge, **Stop** button available at any time) → results (findings, export) → history (details of a previous scan and associated findings) and favorite targets from the main menu. Terminal adaptation (colors, size, structural degradation) is automatic.

#### Keyboard shortcuts

| Key | Action |
|---|---|
| `↑` / `↓` | Move between screen elements |
| `Tab` / `Shift+Tab` | Move between form fields |
| `Esc` | Return to the previous screen (exit confirmation on the home screen) |
| `t` | Next theme (applied immediately, without confirmation) |
| `r` | Refresh terminal detection |
| `a` | Display help (including the preset table) |
| `q` | Quit (with confirmation) |
| `Ctrl+P` | Command palette (Theme, Quit, Screenshot) |

### Scriptable mode (CLI)

```bash
# Scan with a ready-to-use preset
./omega-fuzz.sh scan --target https://example.com --preset prod-safe

# Manual scope + aggressiveness combination (without a preset)
./omega-fuzz.sh scan --target https://example.com --scope-profile standard --aggressiveness standard

# With authentication (YAML file; never place credentials on the command line)
./omega-fuzz.sh scan --target https://example.com --preset staging-full --auth-config auth.yaml

# Dry run: effective configuration and estimated plan; no requests are sent
./omega-fuzz.sh scan --target https://example.com --preset prod-safe --dry-run

# Targeted export (directory, formats, HTML theme)
./omega-fuzz.sh scan --target https://example.com --preset prod-safe \
    --output-dir ./rapports --format html --export-theme omega-neon
```

`scan` options:

| Option | Default | Effect |
|---|---|---|
| `--target` | *(required)* | Target URL; `http://`/`https://` scheme required (never completed automatically) |
| `--preset` | — | Ready-to-use preset (see [§4](#4-scope-profiles-and-presets)) |
| `--scope-profile` | — | Scope profile, to be combined with `--aggressiveness`, without `--preset` |
| `--aggressiveness` | — | Aggressiveness level, to be combined with `--scope-profile`, without `--preset` |
| `--auth-config` | — | Authentication YAML file |
| `--insecure-tls` | disabled | Disables TLS verification (triggers enhanced confirmation) |
| `--max-duration` | *(from profile)* | Overrides the maximum duration (seconds) |
| `--max-requests` | *(from profile)* | Overrides the maximum number of requests |
| `--max-tests` | *(from profile)* | Overrides the maximum number of tests |
| `--max-concurrent` | *(from profile)* | Overrides the maximum concurrency |
| `--dry-run` | disabled | Displays the effective configuration and estimated plan; sends no requests |
| `--output-dir` | `var/exports/` | Exported report directory, named `<preset>-<timestamp>.<ext>` (overridable in Settings) |
| `--format` | `all` | `json`, `markdown`, `html`, or `all` |
| `--export-theme` | `omega-base` | Theme of the exported HTML report (no effect on json/markdown) |

There is no `history`/`show` subcommand on the CLI: history and favorite targets are available only from the TUI.

If the alias was created by `install.sh`, `fuzz scan ...` works from anywhere in the terminal, without the `./omega-fuzz.sh` prefix.

## 4. Scope profiles and presets

### Scope profiles

| Profile | Mode | Max depth | Restrictions |
|---|---|---|---|
| `strict` | exact target | 1 | Blocks `/health`, `/ready`, `/metrics`, `/favicon.ico`, `/robots.txt` |
| `standard` | + subdomains | 2 | Blocks common static subdomains, technical paths, and assets (images/css/js/fonts) |
| `large` | + subdomains | 4 | Blocks only technical paths and assets (including archives/PDFs) |
| `api` | exact target | 3 | Restricted to `/api`, `/v1`, `/v2`; blocks documentation and assets |
| `custom` | + subdomains | 3 | No restrictions by default — starting point for manual configuration |

Regardless of the selected profile, a list of binary/large extensions (`.iso`, `.zip`, `.exe`, `.mp4`...) is **always** excluded from crawling and fuzzing, even under `custom` — a link to such a file is never fetched through a real HTTP request, preventing a downloads directory from slowing a scan for many minutes.

### Aggressiveness levels

`doux` · `standard` · `agressif` · `violent` — each has its own base limits (duration, requests, tests, depth, concurrency), overridden by a preset where applicable.

### Ready-to-use presets

| Preset | Scope | Aggressiveness | Max duration | Max requests | Max tests | Max depth | Enhanced confirmation |
|---|---|---|---|---|---|---|---|
| `prod-safe` | strict | doux | 300 s | 1,000 | 500 | 1 | no |
| `staging-full` | standard | standard | 1,800 s | 20,000 | 10,000 | 2 | no |
| `lab-deep` | large | agressif | 3,600 s | 100,000 | 50,000 | 4 | no |
| `lab-extreme` | large | violent | 7,200 s | 500,000 | 250,000 | 5 | **yes** |
| `api-hardened` | api | agressif | 1,800 s | 50,000 | 25,000 | 3 | no |

A scan remains blocked until it is confirmed. **Enhanced** confirmation (the exact phrase `OUI-J-AI-L-AUTORISATION` must be entered) is required whenever one of these three factors is present: `violent` aggressiveness, the `lab-extreme` preset, or disabled TLS verification (`--insecure-tls`) — an unusual combination without any of these three factors requires simple yes/no confirmation.

## 5. Security tests performed

Automatic pipeline, on every URL discovered within the scope (and every `GET` form found there):

| Test | Trigger | What is checked |
|---|---|---|
| Generic parameter fuzzing | Every query-string parameter | Target behavior in response to boundary/malformed values |
| Header fuzzing | Once per URL, 4 fixed headers (`User-Agent`, `Referer`, `X-Forwarded-For`, `Accept-Language`) | Target behavior in response to boundary/malformed header values |
| Form fuzzing (`GET` only) | Every `GET` form field discovered within the scope | Target behavior in response to boundary/malformed form-field values |
| Reflected XSS | Every query-string parameter | Unfiltered reflection of a payload in the response (non-destructive) |
| Generic injection | Every query-string parameter | Server-error detection in response to an injection payload (no specific SQL/NoSQL fingerprinting) |
| Security headers | Once per URL | Missing or misconfigured security headers in the response |

The first three tests (generic parameter/header/form fuzzing) are a mutation engine **without detection** — they never directly produce a `Finding`; only encountered server errors (5xx) are counted on the corresponding `Test`. Only signatures (XSS, injection, security headers) generate findings.

## 6. Scoring and severity

Each detected anomaly is scored on three axes (`impact`, `exploitability`, `scope`, 1 to 5 each), according to the nature of the observation — deliberately **conservative** mapping (lower end of the range, with no human confirmation at this automatic stage):

| Raw score (sum of the 3 axes) | Severity |
|---|---|
| ≥ 13 | `critical` |
| ≥ 10 | `high` |
| ≥ 7 | `medium` |
| < 7 | `low` |

A manual adjustment (`severity_override`) remains possible but always requires an explicit justification. Equivalent findings (same type, same endpoint, same parameter) are deduplicated while retaining the best available evidence (confidence level `omega_lib.core.confidence.ConfidenceLevel`, then raw score in case of a tie).

## 7. Authentication

Dedicated YAML file (`--auth-config`); credentials are never placed on the command line:

| Mode | Effect |
|---|---|
| `none` | No authentication (default) |
| `cookie` | Session cookie provided directly |
| `bearer_token` | `Authorization: Bearer ...` token |
| `login_form` | Form authentication (login URL, username/password fields) |

## 8. Architecture

Omega-Fuzz follows **Clean Architecture** (domain / application / infrastructure / interfaces / ports / core / app / plugins), aligned with the `omega-` suite template (see `omega-check`/`omega-deep`/`omega-fold`) and checked by `import-linter` after every change. Full details are in **`docs/ARCHITECTURE.md`**.

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
- `plugins/fuzzers/` and `plugins/signatures/`: pure functions that build test plans (`Test` + `ScanRequest`); they never access `HttpClient`.
- `infrastructure/network/`: performs networking (`httpx`, memory-bounded streaming); it never makes judgments.
- `infrastructure/analyzers/`: reads an already received response and produces structured `Observation` objects; it never recalculates a score.
- `interfaces/`: displays information and contains no business logic.

## 9. Exports

Reports are generated in `var/exports/` by default (runtime path anchored to the project directory, `$OMEGA_FUZZ_VAR_DIR` to override it, also overridable in Settings), or at the path specified by `--output-dir`. Flat filename, without subdirectories: `<preset>-<timestamp>.<ext>` (for example, `prod-safe-2026-09-01_14-30-22.html`).

### JSON, source of truth

Complete report structure (effective configuration, statistics, tests, findings), strictly JSON-serializable.

### Markdown, compact human-readable report

Readable outside the terminal, without ANSI codes.

### HTML, standalone web report

5 themes available (`--export-theme` in the CLI, selector in the TUI): `omega-base`, `omega-burn`, `omega-neon`, `light-basic`, `light-alt`.

## 10. History and favorite targets

Each scan is persisted (SQLite, `var/db/omega-fuzz.db`) with its findings and can be viewed from the TUI History screen. Only `Scan` and `Finding` are stored — not the effective configuration or detailed requests — so replay, comparison, and new export are not available from this screen (the screen explains this instead of fabricating data).

The **Targets** screen keeps a list of favorites (normalized URLs, `var/targets.json`) that can be reused to prefill the Target field of a new scan directly.

## 11. Screenshots

The **Screenshot** command in the palette (`Ctrl+P`) saves an SVG of the current TUI screen to `var/screenshots/` by default; this can be overridden in Settings (like the export directory). A dedicated purge is available in Settings.

## 12. Terminal compatibility

The Textual TUI automatically detects terminal capabilities (emulator, size) and adapts its structural stylesheet accordingly (`complete`/`standard`/`reduced`/`mono`), without a manual flag. CLI mode always remains plain text and independent of the terminal. This policy is shared by the entire `omega-` suite (`omega-lib`, `terminal/policies.py`).

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

The final profile is **the more restrictive of the two** (emulator and size) — it can be refreshed live with the `r` key.

## 13. Tests

```bash
source .venv/bin/activate
lint-imports        # checks the Dependency Rule (6 contracts)
pytest -q           # 317 tests
ruff check src tests
mypy -p omega_fuzz
```

Structure: `tests/unit/` (domain and application, without real I/O), `tests/integration/` (real filesystem through `tmp_path`, fake HTTP server via `pytest-httpserver`, real SQLite database, end-to-end CLI), `tests/tui/` (navigation through `Pilot`, structural — no claimed automated visual verification).

## 14. Out of scope

- JSON body fuzzing (code present, not wired in — no API schema discovery)
- Fuzzing of `POST`/`PUT`/`DELETE` forms (excluded by design, write risk)
- Business-logic tests (IDOR, authorization, workflow), outside manual invocation
- Simultaneous multi-target scanning
- Replay, comparison, or export from history
- Client-side JavaScript rendering
- Web dashboard

---

> Omega-Fuzz — Discover a scope, test it with explicit safeguards, and never guess what has not been confirmed.
