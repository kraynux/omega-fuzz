<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - MIT-Lizenz (siehe Datei LICENSE) -->
<div align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/assets/omega-fuzz.png" alt="Omega-Fuzz" width="512">
</div>

# 🗱 OMEGA-FUZZ

**Schwachstellenscanner**

> Entwickelt von [kraynux](https://github.com/kraynux) für [Omega-Server](https://kraynux.snake-mackarel.ts.net)   

Offizielle Seite: [OMEGA-FUZZ](https://kraynux.snake-mackarel.ts.net/omega-fuzz/) &nbsp; Vorschau: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-fuzz/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

🌐 Oberfläche und exportierte Berichte in **17 Sprachen** verfügbar — siehe [Sprachen der Oberfläche](#sprachen-der-oberfläche).  
**Sprachen:**  
<img src="https://flagcdn.com/w20/fr.png" alt="Français" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)

**Omega-Fuzz** ist eine lokale Terminalanwendung ([Textual](https://github.com/Textualize/textual)-TUI + skriptfähige CLI), die Erkundung und Sicherheitstests im Web (HTTP-Fuzzing) für autorisierte Umgebungen steuert (Labore, persönliche Spiegel, ausdrücklich genehmigte Testaufträge).

Werkzeug der `omega-`-Suite, nach Clean Architecture aufgebaut — siehe `docs/ARCHITECTURE.md` für alle technischen Details.

## 1. Vision und Umfang

### Was Omega-Fuzz tut

- Erkundet den Umfang eines einzelnen Ziels per BFS, begrenzt durch einen expliziten Scope (Schema/Subdomains/erlaubte-gesperrte Pfade/Tiefe), nie ohne Schutzmechanismen.
- Generisches Fuzzing der Query-String-Parameter, der HTTP-Header und der `GET`-Formulare, die auf jeder entdeckten URL gefunden werden, und Prüfung dreier Signaturfamilien: nicht destruktives reflektiertes XSS, generische Injection (Fehlererkennung in der Antwort), fehlende oder falsch konfigurierte Sicherheitsheader — siehe [§5](#5-ausgeführte-sicherheitstests).
- Bewertet jede Auffälligkeit auf 3 Achsen (Auswirkung/Ausnutzbarkeit/Reichweite) und leitet daraus einen Schweregrad ab (`low`/`medium`/`high`/`critical`), dedupliziert nach `(Typ, Endpunkt, Parameter)` unter Beibehaltung des besten Belegs — siehe [§6](#6-bewertung-und-schweregrad).
- Unterstützt Authentifizierung (Cookie, Bearer-Token, Anmeldeformular) über eine eigene YAML-Datei, nie mit Klartext-Zugangsdaten auf der Kommandozeile.
- Stellt das Ergebnis in der TUI (Textual) oder in der skriptfähigen CLI dar, mit drei Exporten (JSON, Markdown, HTML mit 5 Themes).
- Führt einen dauerhaften Verlauf der Scans und ihrer Findings (SQLite) sowie eine Liste wiederverwendbarer Lieblingsziele.
- Verlangt eine ausdrückliche Bestätigung (strikte Phrase für die sensibelsten Fälle) vor jedem aggressiven oder erweiterten Scan oder einem Scan mit deaktivierter TLS-Prüfung.

### Was Omega-Fuzz nicht tut

- Fuzzing von JSON-Bodys — der Code existiert (`plugins/fuzzers/json_body_fuzzer.py`), ist aber nicht angebunden (die HTML/BFS-Erkundung liefert kein JSON-API-Schema und keine verwertbare Vorlagenquelle).
- Fuzzing von `POST`/`PUT`/`DELETE`-Formularen — bewusst aus der automatischen Pipeline ausgeschlossen (Risiko ungewollter Schreibvorgänge auf dem Ziel); nur `GET`-Formulare werden getestet.
- Tests der Geschäftslogik (IDOR, Berechtigungsprüfung, Unterbrechung von Abläufen) — der Code existiert (`plugins/logic_tests/`), bleibt aber außerhalb der automatischen Pipeline, ist nur separat aufrufbar und wird nie durch einen Standardscan ausgelöst.
- Paralleler Scan mehrerer Ziele — ein einziges Ziel pro Scan.
- Wiederholung, Vergleich oder Export aus dem Bildschirm Verlauf — gespeichert werden nur `Scan` und `Finding` (weder die vollständige wirksame Konfiguration noch die Anfragen); eine Wiederholung oder ein erneuter Export aus dem Verlauf würde also Daten erfinden, und der Bildschirm erklärt das, statt es stillschweigend anzubieten.
- Clientseitiges JavaScript-Rendering (die Seite wird so abgerufen, wie sie ausgeliefert wird, nicht in einem Headless-Browser ausgeführt).
- Web-Dashboard.

## 2. Installation

### Voraussetzungen

- Python 3.10+
- Internetverbindung, für die Abhängigkeiten
- Für die TUI: eine im Terminal installierte [Nerd Font](https://www.nerdfonts.com/) für das Symbol im Header — ohne sie erscheint dieses Zeichen als leeres Kästchen (dieselbe Einschränkung wie bei einem Emoji, aber unter Terminalnutzern viel weiter verbreitet). Ihr Fehlen hat keine Auswirkung auf die Funktion, es ist rein kosmetisch.

### Installation

```bash
[ -d omega-fuzz ] && echo "ℹ️ Hier bereits entpackt, Schritt übersprungen." || tar -xzf omega-fuzz.tar.gz
cd omega-fuzz/
chmod +x install.sh
./install.sh
```

`install.sh`:

1. Legt die virtuelle Umgebung `.venv` an, falls sie noch nicht existiert.
2. Installiert die Abhängigkeiten (`vendor/omega-lib/` und dann `pip install -e .`, `pyproject.toml` bleibt die einzige Quelle der Wahrheit).
3. Macht `omega-fuzz.sh` und `install.sh` ausführbar.
4. Fügt den Alias `fuzz` zu `~/.bashrc` und `~/.zshrc` hinzu (ohne Duplikat, falls schon vorhanden).

### Abhängigkeiten

Deklariert in `pyproject.toml` (keine `requirements.txt`):
- `omega-lib`: gemeinsame Bibliothek der Suite (Export-Themes, Terminalerkennung, `ConfidenceLevel`) — mitgeliefert in `vendor/omega-lib/`
- `httpx`: asynchrone HTTP-Anfragen (Erkundung + Fuzzing), Streaming der Antwort (nie ein vollständiger Puffer im Speicher, selbst bei einer mehrere GB großen Datei, die das Ziel ausliefert)
- `beautifulsoup4` + `lxml`: Extraktion der HTML-URLs und -Formulare
- `jinja2`: Templating für den HTML-Export
- `textual`: TUI-Oberfläche, Themes, automatische Anpassung an das Terminal
- `pyyaml`: Laden der Datei `--auth-config`
- Entwicklungsabhängigkeiten (`pip install -e ".[dev]"`): `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-httpserver`, `ruff`, `mypy`, `import-linter`

## 3. Verwendung

### Interaktiver Modus (TUI)

Empfohlen für den täglichen Gebrauch — ohne Argumente gestartet:

```bash
./omega-fuzz.sh
```
wenn Sie den Alias angelegt haben, tippen Sie einfach `fuzz` im Terminal:
```bash
fuzz
```

Ablauf: Startbildschirm (schließt sich per Tastendruck oder Klick) → Hauptmenü (Scannen / Ziele / Einstellungen / Verlauf / Hilfe) → Eingabe des Ziels (vollständige URL, Schema `http://`/`https://` erforderlich), Preset oder manuelle Konfiguration (Scope + Aggressivität), optionale Authentifizierung, TLS-Prüfung, Überschreiben der Grenzen → Prüfbildschirm (einfache Bestätigung oder strikte Phrase `OUI-J-AI-L-AUTORISATION` für sensible Fälle) → Scan (unbestimmte Fortschrittsanzeige, Schaltfläche **Stoppen** jederzeit) → Ergebnisse (Findings, Export) → Verlauf (Details eines früheren Scans, zugehörige Findings) und Lieblingsziele aus dem Hauptmenü. Die Anpassung an das Terminal (Farben, Größe, strukturelle Reduktion) erfolgt automatisch.

#### Tastenkürzel

| Taste | Aktion |
|---|---|
| `↑` / `↓` | Zwischen den Elementen eines Bildschirms wechseln |
| `Tab` / `Umschalt+Tab` | Zwischen den Feldern eines Formulars wechseln |
| `Esc` | Zurück zum vorherigen Bildschirm (Beenden-Bestätigung auf dem Startbildschirm) |
| `t` | Nächstes Theme (sofort angewendet, ohne Bestätigung) |
| `r` | Terminalerkennung aktualisieren |
| `a` | Hilfe anzeigen (mit Preset-Tabelle) |
| `q` | Beenden (mit Bestätigung) |
| `Ctrl+P` | Befehlspalette (Theme, Beenden, Bildschirmfoto) |

### Sprachen der Oberfläche

Die Oberfläche ist in 17 Sprachen verfügbar: Französisch, Englisch, Spanisch, Portugiesisch (Brasilien), Italienisch, Deutsch, Niederländisch, Polnisch, Russisch, vereinfachtes Chinesisch, Vietnamesisch, Thailändisch, Indonesisch, Japanisch, Koreanisch, Hindi und Arabisch. Die Auswahl erfolgt in den Einstellungen („Langue / Language“) und gilt nach einem Neustart der Oberfläche; die Variable `OMEGA_FUZZ_LANG` (zum Beispiel `OMEGA_FUZZ_LANG=en ./omega-fuzz.sh`) erzwingt eine Sprache für die Dauer einer Sitzung. Aus omega-suite gestartet, übernimmt omega-fuzz die Sprache der Suite. Auf einer Linux-Textkonsole (TTY) werden Sprachen mit nicht lateinischer Schrift für die Sitzung auf Englisch angezeigt. Die Kommandozeile bleibt auf Französisch.

### Kontakt und Support

Die Hilfe (Taste `a`) bietet einen Bildschirm **Kontakt und Support**: *Einen Kaffee spendieren* (PayPal-Seite des Entwicklers), *Support kontaktieren* (E-Mail-Adresse und Kontaktformular der Website, im Klartext angezeigt), *Mich als Nutzer melden (anonym)* und *Updates prüfen*. Die Meldung ist freiwillig, standardmäßig deaktiviert und wird nur ein einziges Mal gesendet: Sie dient nur dazu, die Nutzer zu zählen und, wenn gewünscht, ihren Kontinent oder ihr Land (geschlossene Listen, nie Freitext). Gesendet werden ein zufällig gezogener Schlüssel, der Name der Software (`omega-fuzz`) und ihre Version; nie ein Name, ein Rechnername, eine Einstellung, ein Ziel oder ein Ergebnis. Die IP-Adresse wird in den Meldungen nicht gespeichert, durchläuft aber wie jeder Besuch die Sicherheitsprüfungen und das Protokoll des Empfangsservers. Rückzug jederzeit über denselben Bildschirm (*Mich nicht mehr melden*). Die Update-Prüfung liest nur die Liste der auf der Website veröffentlichten Versionen, und nie ohne Klick.

### Skriptfähiger Modus (CLI)

```bash
# Scan mit einem gebrauchsfertigen Preset
./omega-fuzz.sh scan --target https://example.com --preset prod-safe

# Manuelle Kombination Scope + Aggressivität (ohne Preset)
./omega-fuzz.sh scan --target https://example.com --scope-profile standard --aggressiveness standard

# Mit Authentifizierung (YAML-Datei, nie Klartext-Zugangsdaten auf der Kommandozeile)
./omega-fuzz.sh scan --target https://example.com --preset staging-full --auth-config auth.yaml

# Dry-Run: wirksame Konfiguration und geschätzter Plan, keine Anfrage gesendet
./omega-fuzz.sh scan --target https://example.com --preset prod-safe --dry-run

# Gezielter Export (Ordner, Formate, HTML-Theme)
./omega-fuzz.sh scan --target https://example.com --preset prod-safe \
    --output-dir ./rapports --format html --export-theme omega-neon
```

Optionen von `scan`:

| Option | Standard | Wirkung |
|---|---|---|
| `--target` | *(erforderlich)* | Ziel-URL, Schema `http://`/`https://` erforderlich (nie automatisch ergänzt) |
| `--preset` | — | Gebrauchsfertiges Preset (siehe [§4](#4-scope-profile-und-presets)) |
| `--scope-profile` | — | Scope-Profil, mit `--aggressiveness` zu kombinieren, ohne `--preset` |
| `--aggressiveness` | — | Aggressivitätsstufe, mit `--scope-profile` zu kombinieren, ohne `--preset` |
| `--auth-config` | — | YAML-Datei für die Authentifizierung |
| `--insecure-tls` | deaktiviert | Deaktiviert die TLS-Prüfung (löst die verstärkte Bestätigung aus) |
| `--max-duration` | *(aus dem Profil)* | Überschreibt die maximale Dauer (Sekunden) |
| `--max-requests` | *(aus dem Profil)* | Überschreibt die maximale Anzahl an Anfragen |
| `--max-tests` | *(aus dem Profil)* | Überschreibt die maximale Anzahl an Tests |
| `--max-concurrent` | *(aus dem Profil)* | Überschreibt die maximale Parallelität |
| `--dry-run` | deaktiviert | Zeigt die wirksame Konfiguration und den geschätzten Plan, sendet keine Anfrage |
| `--output-dir` | `var/exports/` | Ordner der exportierten Berichte, benannt `<preset>-<Zeitstempel>.<ext>` (in den Einstellungen überschreibbar) |
| `--format` | `all` | `json`, `markdown`, `html` oder `all` |
| `--export-theme` | `omega-base` | Theme des exportierten HTML-Berichts (ohne Wirkung auf json/markdown) |

In der CLI gibt es keinen Unterbefehl `history`/`show`: Verlauf und Lieblingsziele lassen sich nur in der TUI einsehen.

Wurde der Alias von `install.sh` angelegt, funktioniert `fuzz scan ...` überall im Terminal, ohne das Präfix `./omega-fuzz.sh`.

## 4. Scope-Profile und Presets

### Scope-Profile

| Profil | Modus | Max. Tiefe | Einschränkungen |
|---|---|---|---|
| `strict` | exaktes Ziel | 1 | Sperrt `/health`, `/ready`, `/metrics`, `/favicon.ico`, `/robots.txt` |
| `standard` | + Subdomains | 2 | Sperrt übliche statische Subdomains, technische Pfade, Assets (Bilder/css/js/Schriften) |
| `large` | + Subdomains | 4 | Sperrt nur technische Pfade und Assets (einschließlich Archiven/PDF) |
| `api` | exaktes Ziel | 3 | Beschränkt auf `/api`, `/v1`, `/v2`; sperrt Dokumentation und Assets |
| `custom` | + Subdomains | 3 | Standardmäßig keine Einschränkung — Ausgangsbasis für eine manuelle Konfiguration |

Unabhängig vom gewählten Profil ist eine Liste binärer oder großer Dateiendungen (`.iso`, `.zip`, `.exe`, `.mp4`...) **immer** vom Crawling und Fuzzing ausgeschlossen, selbst unter `custom` — ein Link auf eine solche Datei wird nie mit einer echten HTTP-Anfrage abgerufen, damit ein Download-Ordner einen Scan nicht minutenlang ausbremst.

### Aggressivitätsstufen

`doux` · `standard` · `agressif` · `violent` — jede hat ihre eigenen Grundgrenzen (Dauer, Anfragen, Tests, Tiefe, Parallelität), die gegebenenfalls von einem Preset überschrieben werden.

### Gebrauchsfertige Presets

| Preset | Scope | Aggressivität | Max. Dauer | Max. Anfragen | Max. Tests | Max. Tiefe | Verstärkte Bestätigung |
|---|---|---|---|---|---|---|---|
| `prod-safe` | strict | doux | 300 s | 1.000 | 500 | 1 | nein |
| `staging-full` | standard | standard | 1.800 s | 20.000 | 10.000 | 2 | nein |
| `lab-deep` | large | agressif | 3.600 s | 100.000 | 50.000 | 4 | nein |
| `lab-extreme` | large | violent | 7.200 s | 500.000 | 250.000 | 5 | **ja** |
| `api-hardened` | api | agressif | 1.800 s | 50.000 | 25.000 | 3 | nein |

Ein Scan bleibt blockiert, solange er nicht bestätigt ist. Eine **verstärkte** Bestätigung (Eingabe der exakten Phrase `OUI-J-AI-L-AUTORISATION`) ist erforderlich, sobald einer dieser drei Faktoren vorliegt: Aggressivität `violent`, Preset `lab-extreme` oder deaktivierte TLS-Prüfung (`--insecure-tls`) — bei einer ungewöhnlichen Kombination ohne einen dieser drei Faktoren genügt eine einfache Ja/Nein-Bestätigung.

## 5. Ausgeführte Sicherheitstests

Automatische Pipeline, auf jeder im Scope entdeckten URL (und jedem dort gefundenen `GET`-Formular):

| Test | Auslöser | Was geprüft wird |
|---|---|---|
| Generisches Parameter-Fuzzing | jeder Query-String-Parameter | Verhalten des Ziels bei Grenz- oder fehlerhaften Werten |
| Header-Fuzzing | einmal pro URL, 4 feste Header (`User-Agent`, `Referer`, `X-Forwarded-For`, `Accept-Language`) | Verhalten des Ziels bei Grenz- oder fehlerhaften Werten in einem Header |
| Formular-Fuzzing (nur `GET`) | jedes im Scope entdeckte Feld eines `GET`-Formulars | Verhalten des Ziels bei Grenz- oder fehlerhaften Werten in einem Formularfeld |
| Reflektiertes XSS | jeder Query-String-Parameter | Ungefilterte Reflexion eines Payloads in der Antwort (nicht destruktiv) |
| Generische Injection | jeder Query-String-Parameter | Erkennung eines Serverfehlers als Antwort auf einen Injection-Payload (kein spezifischer SQL/NoSQL-Fingerprint) |
| Sicherheitsheader | einmal pro URL | Fehlende oder falsch konfigurierte Sicherheitsheader in der Antwort |

Die ersten drei Tests (generisches Fuzzing von Parametern/Headern/Formularen) sind eine Mutations-Engine **ohne Erkennung** — sie erzeugen nie direkt ein `Finding`, nur die aufgetretenen Serverfehler (5xx) werden beim zugehörigen `Test` gezählt. Nur die Signaturen (XSS, Injection, Sicherheitsheader) erzeugen Findings.

## 6. Bewertung und Schweregrad

Jede erkannte Auffälligkeit wird je nach Art der Beobachtung auf 3 Achsen bewertet (`Auswirkung`, `Ausnutzbarkeit`, `Reichweite`, jeweils 1 bis 5) — eine bewusst **zurückhaltende** Zuordnung (unteres Ende der Spanne, keine menschliche Bestätigung in diesem automatischen Schritt):

| Rohwert (Summe der 3 Achsen) | Schweregrad |
|---|---|
| ≥ 13 | `critical` |
| ≥ 10 | `high` |
| ≥ 7 | `medium` |
| < 7 | `low` |

Eine manuelle Anpassung (`severity_override`) bleibt möglich, verlangt aber immer eine ausdrückliche Begründung. Gleichwertige Findings (gleicher Typ, gleicher Endpunkt, gleicher Parameter) werden dedupliziert, wobei der beste verfügbare Beleg erhalten bleibt (Vertrauensstufe `omega_lib.core.confidence.ConfidenceLevel`, bei Gleichstand dann der Rohwert).

## 7. Authentifizierung

Eigene YAML-Datei (`--auth-config`), nie Klartext-Zugangsdaten auf der Kommandozeile:

| Modus | Wirkung |
|---|---|
| `none` | Keine Authentifizierung (Standard) |
| `cookie` | Direkt bereitgestelltes Sitzungscookie |
| `bearer_token` | Token `Authorization: Bearer ...` |
| `login_form` | Authentifizierung per Formular (Anmelde-URL, Felder für Benutzer/Passwort) |

## 8. Architektur

Omega-Fuzz ist nach **Clean Architecture** aufgebaut (domain / application / infrastructure / interfaces / ports / core / app / plugins), am Gerüst der `omega-`-Suite ausgerichtet (siehe `omega-check`/`omega-deep`/`omega-fold`) und bei jeder Änderung von `import-linter` geprüft. Alle Details stehen in **`docs/ARCHITECTURE.md`**.

Sehr kurze Übersicht:

```text
src/omega_fuzz/
├── domain/          Reine Geschäftslogik (Ziele/Scope, Anfragen, Tests, Findings, Profile, Berichte...)
├── application/     Anwendungsfälle (commands/queries) und Orchestratoren (Erkundung, Scan, Bericht, Grenzen)
├── ports/           Von der Anwendung erwartete Verträge (http_client, repositories, exporters...)
├── infrastructure/  Konkrete Implementierungen (httpx, BeautifulSoup, SQLite, Jinja2-Exporter — Textual ist NICHT hier)
├── interfaces/      tui/ (Textual) und cli/ (skriptfähig), mit strikter Funktionsgleichheit
├── plugins/         Fuzzer und Signaturen (reine Funktionen, nie direkter Netzwerkzugriff)
├── app/             Zusammenbau (Container, Composition Root, Lebenszyklus)
└── core/            Übergreifendes Vokabular, Fehler, Konstanten
```

Entwurfsregeln:
- `plugins/fuzzers/` und `plugins/signatures/`: reine Funktionen, die Testpläne erstellen (`Test` + `ScanRequest`), berühren nie `HttpClient`.
- `infrastructure/network/`: übernimmt das Netzwerk (`httpx`, im Speicher begrenztes Streaming), urteilt nie.
- `infrastructure/analyzers/`: liest eine bereits empfangene Antwort, erzeugt strukturierte `Observation`-Objekte, berechnet nie einen Wert neu.
- `interfaces/`: zeigt an, enthält keine Geschäftslogik.

## 9. Exporte

Markdown- und HTML-Berichte werden in der in den Einstellungen gewählten Sprache geschrieben („Sprache der Exporte“, standardmäßig die der Oberfläche); JSON bleibt ein Datenformat und wird nicht übersetzt. Die Berichte werden standardmäßig in `var/exports/` erzeugt (Laufzeitpfad im Projektordner verankert, `$OMEGA_FUZZ_VAR_DIR` zum Überschreiben, auch im Bildschirm Einstellungen überschreibbar) oder unter dem angegebenen Pfad (`--output-dir`). Flacher Dateiname, ohne Unterordner: `<preset>-<Zeitstempel>.<ext>` (z. B. `prod-safe-2026-09-01_14-30-22.html`).

### JSON, Quelle der Wahrheit

Vollständige Struktur des Berichts (wirksame Konfiguration, Statistiken, Tests, Findings), streng JSON-serialisierbar.

### Markdown, kompakter Bericht für Menschen

Außerhalb des Terminals lesbar, ohne ANSI-Codes.

### HTML, eigenständiger Webbericht

5 Themes zur Auswahl (`--export-theme` in der CLI, Auswahlfeld in der TUI): `omega-base`, `omega-burn`, `omega-neon`, `light-basic`, `light-alt`.

## 10. Verlauf und Lieblingsziele

Jeder Scan wird mit seinen Findings gespeichert (SQLite, `var/db/omega-fuzz.db`) und ist im Bildschirm Verlauf der TUI einsehbar. Gespeichert werden nur `Scan` und `Finding` — weder die wirksame Konfiguration noch die einzelnen Anfragen — daher gibt es in diesem Bildschirm keine Wiederholung, keinen Vergleich und keinen erneuten Export (der Bildschirm erklärt das, statt Daten zu erfinden).

Der Bildschirm **Ziele** führt eine Favoritenliste (normalisierte URLs, `var/targets.json`), mit der sich das Feld Ziel eines neuen Scans direkt vorausfüllen lässt.

## 11. Bildschirmaufnahmen

Befehl **Bildschirmfoto** der Palette (`Ctrl+P`): speichert ein SVG des aktuellen TUI-Bildschirms standardmäßig in `var/screenshots/`, im Bildschirm Einstellungen überschreibbar (wie der Exportordner). Eine eigene Bereinigung ist in den Einstellungen verfügbar.

## 12. Terminal-Kompatibilität

Die TUI (Textual) erkennt automatisch die Fähigkeiten des Terminals (Emulator, Größe) und passt ihr strukturelles Stylesheet entsprechend an (`complete`/`standard`/`reduced`/`mono`), ohne manuelles Flag. Der CLI-Modus bleibt immer reiner Text, unabhängig vom Terminal. Diese Regel gilt für die ganze `omega-`-Suite (`omega-lib`, `terminal/policies.py`).

### Profil nach erkanntem Emulator

| Emulator | Anfangsprofil |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | `complete` |
| Konsole, GNOME Terminal, Terminator, Xfce4 Terminal | `standard` |
| xterm, urxvt, modernes SSH | `reduced` |
| Linux-TTY, älteres SSH | `mono` |
| Nicht erkannter Emulator | `reduced` (Standard-Rückfall) |

### Profil nach Terminalgröße

| Mindestgröße (Spalten × Zeilen) | Profil-Obergrenze |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| darunter | `mono` |

Das endgültige Profil ist **das restriktivere der beiden** (Emulator und Größe) — mit der Taste `r` live aktualisierbar.

## 13. Tests

```bash
source .venv/bin/activate
lint-imports        # prüft die Dependency Rule (6 Verträge)
pytest -q           # 344 Tests
ruff check src tests
mypy -p omega_fuzz
```

Aufbau: `tests/unit/` (Domäne und Anwendung, ohne echte E/A), `tests/integration/` (echtes Dateisystem über `tmp_path`, Fake-HTTP-Server `pytest-httpserver`, echte SQLite-Datenbank, CLI von Ende zu Ende), `tests/tui/` (Navigation über `Pilot`, strukturell — keine selbst behauptete visuelle Prüfung).

## 14. Außerhalb des Umfangs

- Fuzzing von JSON-Bodys (Code vorhanden, nicht angebunden — keine Erkennung von API-Schemata)
- Fuzzing von `POST`/`PUT`/`DELETE`-Formularen (bewusst ausgeschlossen, Schreibrisiko)
- Tests der Geschäftslogik (IDOR, Berechtigungen, Abläufe) außerhalb des manuellen Aufrufs
- Gleichzeitiger Scan mehrerer Ziele
- Wiederholung, Vergleich oder Export aus dem Verlauf
- Clientseitiges JavaScript-Rendering
- Web-Dashboard

---

> Omega-Fuzz — Einen Umfang erkunden, ihn mit ausdrücklichen Schutzmechanismen testen, nie erraten, was nicht bestätigt wurde.

<p align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/de/omega-fuzz/A.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/de/omega-fuzz/B.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/de/omega-fuzz/C.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/de/omega-fuzz/D.png" width="24%" />
</p>
