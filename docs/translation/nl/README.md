<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - MIT-licentie (zie bestand LICENSE) -->
<div align="center">
  <img src="../../assets/omega-fuzz.png" alt="Omega-Fuzz" width="384">
</div>

# 🗱 OMEGA-FUZZ

**Kwetsbaarheidsscanner**

> Ontwikkeld door [kraynux](https://github.com/kraynux) voor [Omega-Server](https://kraynux.snake-mackarel.ts.net)   

Officiële pagina: [OMEGA-FUZZ](https://kraynux.snake-mackarel.ts.net/omega-fuzz/) &nbsp; Voorbeeld: [Schermafbeeldingen](https://kraynux.snake-mackarel.ts.net/omega-fuzz/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

🌐 Interface en geëxporteerde rapporten beschikbaar in **17 talen** — zie [Talen van de interface](#talen-van-de-interface).  
**Talen:**  
<img src="https://flagcdn.com/w20/fr.png" alt="Français" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)

**Omega-Fuzz** is een lokale terminaltoepassing ([Textual](https://github.com/Textualize/textual)-TUI + scriptbare CLI) die webverkenning en beveiligingstests (HTTP-fuzzing) aanstuurt voor geautoriseerde omgevingen (labs, persoonlijke mirrors, testopdrachten met uitdrukkelijke toestemming).

Tool van de `omega-`-suite, opgebouwd volgens Clean Architecture — zie `docs/ARCHITECTURE.md` voor alle technische details.

## 1. Visie en reikwijdte

### Wat Omega-Fuzz doet

- Verkent de omtrek van één doel met een BFS die begrensd wordt door een expliciete scope (schema/subdomeinen/toegestane-geblokkeerde paden/diepte), nooit zonder waarborgen.
- Generieke fuzzing van de query-stringparameters, de HTTP-headers en de `GET`-formulieren die op elke ontdekte URL gevonden worden, en controleert drie families van signaturen: niet-destructieve gereflecteerde XSS, generieke injectie (foutdetectie in het antwoord), ontbrekende of verkeerd geconfigureerde beveiligingsheaders — zie [§5](#5-uitgevoerde-beveiligingstests).
- Scoort elke afwijking op 3 assen (impact/exploiteerbaarheid/bereik) en leidt daaruit een ernst af (`low`/`medium`/`high`/`critical`), ontdubbeld op `(type, endpoint, parameter)` met behoud van het beste bewijs — zie [§6](#6-score-en-ernst).
- Ondersteunt authenticatie (cookie, bearer token, inlogformulier) via een eigen YAML-bestand, nooit met inloggegevens in platte tekst op de opdrachtregel.
- Toont het resultaat in de TUI (Textual) of in de scriptbare CLI, met drie exports (JSON, Markdown, HTML met 5 thema's).
- Bewaart een blijvende geschiedenis van de scans en hun findings (SQLite), en een lijst met herbruikbare favoriete doelen.
- Vraagt een uitdrukkelijke bevestiging (strikte zin voor de gevoeligste gevallen) vóór elke agressieve of uitgebreide scan, of een scan met uitgeschakelde TLS-verificatie.

### Wat Omega-Fuzz niet doet

- Fuzzing van JSON-bodies — de code bestaat (`plugins/fuzzers/json_body_fuzzer.py`) maar is niet aangesloten (de HTML/BFS-verkenning levert geen JSON-API-schema en geen bruikbare sjabloonbron op).
- Fuzzing van `POST`/`PUT`/`DELETE`-formulieren — bewust uitgesloten van de automatische pipeline (risico op ongewenste schrijfacties op het doel); alleen `GET`-formulieren worden getest.
- Tests van bedrijfslogica (IDOR, autorisatiecontrole, verstoring van werkstromen) — de code bestaat (`plugins/logic_tests/`) maar blijft buiten de automatische pipeline, kan alleen apart worden aangeroepen en wordt nooit door een standaardscan gestart.
- Parallel scannen van meerdere doelen — één doel per scan.
- Herhalen, vergelijken of exporteren vanuit het scherm Geschiedenis — alleen `Scan` en `Finding` worden opgeslagen (niet de volledige effectieve configuratie en niet de verzoeken), dus herhalen of opnieuw exporteren vanuit de geschiedenis zou gegevens verzinnen; het scherm legt dat uit in plaats van het stilzwijgend aan te bieden.
- JavaScript-rendering aan de clientzijde (de pagina wordt opgehaald zoals ze geserveerd wordt, niet uitgevoerd in een headless browser).
- Webdashboard.

## 2. Installatie

### Vereisten

- Python 3.10+
- Internetverbinding, voor de afhankelijkheden
- Voor de TUI: een [Nerd Font](https://www.nerdfonts.com/) geïnstalleerd in de terminal, voor het pictogram in de header — zonder dit lettertype verschijnt dat teken als een leeg vakje (dezelfde beperking als een emoji, maar veel breder beschikbaar bij terminalgebruikers). Het ontbreken ervan heeft geen gevolgen voor de werking, het is puur cosmetisch.

### Installatie

```bash
[ -d omega-fuzz ] && echo "ℹ️ Hier al uitgepakt, stap overgeslagen." || tar -xzf omega-fuzz.tar.gz
cd omega-fuzz/
chmod +x install.sh
./install.sh
```

`install.sh`:

1. Maakt de virtuele omgeving `.venv` aan als die nog niet bestaat.
2. Installeert de afhankelijkheden (`vendor/omega-lib/` en daarna `pip install -e .`, `pyproject.toml` blijft de enige bron van waarheid).
3. Maakt `omega-fuzz.sh` en `install.sh` uitvoerbaar.
4. Voegt de alias `fuzz` toe aan `~/.bashrc` en `~/.zshrc` (zonder dubbel item als die er al staat).

### Afhankelijkheden

Gedeclareerd in `pyproject.toml` (geen `requirements.txt`):
- `omega-lib`: gedeelde bibliotheek van de suite (exportthema's, terminaldetectie, `ConfidenceLevel`) — meegeleverd in `vendor/omega-lib/`
- `httpx`: asynchrone HTTP-verzoeken (verkenning + fuzzing), streaming van het antwoord (nooit een volledige buffer in het geheugen, zelfs niet bij een bestand van meerdere GB dat het doel serveert)
- `beautifulsoup4` + `lxml`: extractie van HTML-URL's en -formulieren
- `jinja2`: templating voor de HTML-export
- `textual`: TUI-interface, thema's, automatische aanpassing aan de terminal
- `pyyaml`: laden van het bestand `--auth-config`
- Ontwikkelafhankelijkheden (`pip install -e ".[dev]"`): `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-httpserver`, `ruff`, `mypy`, `import-linter`

## 3. Gebruik

### Interactieve modus (TUI)

Aanbevolen voor dagelijks gebruik — gestart zonder argumenten:

```bash
./omega-fuzz.sh
```
als je de alias hebt aangemaakt, typ dan gewoon `fuzz` in de terminal:
```bash
fuzz
```

Verloop: startscherm (sluit met een toets of een klik) → hoofdmenu (Scannen / Doelen / Instellingen / Geschiedenis / Help) → invoer van het doel (volledige URL, schema `http://`/`https://` verplicht), preset of handmatige configuratie (scope + agressiviteit), optionele authenticatie, TLS-verificatie, aanpassing van limieten → controlescherm (eenvoudige bevestiging, of de strikte zin `OUI-J-AI-L-AUTORISATION` voor gevoelige gevallen) → scan (onbepaalde voortgangsbalk, knop **Stoppen** op elk moment) → resultaten (findings, export) → geschiedenis (details van een eerdere scan, bijbehorende findings) en favoriete doelen vanuit het hoofdmenu. De aanpassing aan de terminal (kleuren, grootte, structurele vereenvoudiging) gebeurt automatisch.

#### Sneltoetsen

| Toets | Actie |
|---|---|
| `↑` / `↓` | Tussen de elementen van een scherm navigeren |
| `Tab` / `Shift+Tab` | Tussen de velden van een formulier navigeren |
| `Esc` | Terug naar het vorige scherm (bevestiging van afsluiten op het startscherm) |
| `t` | Volgend thema (meteen toegepast, zonder bevestiging) |
| `r` | Terminaldetectie vernieuwen |
| `a` | Help tonen (inclusief tabel met presets) |
| `q` | Afsluiten (met bevestiging) |
| `Ctrl+P` | Opdrachtenpalet (Theme, Afsluiten, Schermafbeelding) |

### Talen van de interface

De interface is beschikbaar in 17 talen: Frans, Engels, Spaans, Portugees (Brazilië), Italiaans, Duits, Nederlands, Pools, Russisch, vereenvoudigd Chinees, Vietnamees, Thai, Indonesisch, Japans, Koreaans, Hindi en Arabisch. De keuze maak je in Instellingen („Langue / Language”) en geldt na een herstart van de interface; de variabele `OMEGA_FUZZ_LANG` (bijvoorbeeld `OMEGA_FUZZ_LANG=en ./omega-fuzz.sh`) dwingt een taal af voor één sessie. Gestart vanuit omega-suite neemt omega-fuzz de taal van de suite over. Op een Linux-tekstconsole (TTY) worden talen met een niet-Latijns schrift voor die sessie in het Engels getoond. De opdrachtregel blijft in het Frans.

### Contact en ondersteuning

De hulp (toets `a`) biedt een scherm **Contact en ondersteuning**: *Trakteer op een koffie* (PayPal-pagina van de ontwikkelaar), *Contact opnemen met ondersteuning* (e-mailadres en contactformulier van de site, leesbaar weergegeven), *Mij aanmelden als gebruiker (anoniem)* en *Updates controleren*. De aanmelding is vrijwillig, standaard uitgeschakeld en wordt maar één keer verzonden: ze dient alleen om de gebruikers te tellen en, als u dat wilt, hun continent of land (gesloten lijsten, nooit vrije tekst). Ze verzendt een willekeurig gekozen sleutel, de naam van de software (`omega-fuzz`) en de versie; nooit een naam, een machinenaam, een instelling, een doel of een resultaat. Het IP-adres wordt niet opgeslagen in de aanmeldingen, maar gaat, zoals bij elk bezoek, door de beveiligingscontroles en het logboek van de ontvangende server. Intrekken kan op elk moment vanuit hetzelfde scherm (*Mij niet meer aanmelden*). De updatecontrole leest alleen de lijst van versies die op de site gepubliceerd zijn, en nooit zonder klik.

### Scriptbare modus (CLI)

```bash
# Scan met een kant-en-klare preset
./omega-fuzz.sh scan --target https://example.com --preset prod-safe

# Handmatige combinatie scope + agressiviteit (zonder preset)
./omega-fuzz.sh scan --target https://example.com --scope-profile standard --aggressiveness standard

# Met authenticatie (YAML-bestand, nooit inloggegevens in platte tekst op de opdrachtregel)
./omega-fuzz.sh scan --target https://example.com --preset staging-full --auth-config auth.yaml

# Dry-run: effectieve configuratie en geschat plan, geen verzoek verzonden
./omega-fuzz.sh scan --target https://example.com --preset prod-safe --dry-run

# Gerichte export (map, formaten, HTML-thema)
./omega-fuzz.sh scan --target https://example.com --preset prod-safe \
    --output-dir ./rapports --format html --export-theme omega-neon
```

Opties van `scan`:

| Optie | Standaard | Effect |
|---|---|---|
| `--target` | *(verplicht)* | Doel-URL, schema `http://`/`https://` verplicht (nooit automatisch aangevuld) |
| `--preset` | — | Kant-en-klare preset (zie [§4](#4-scopeprofielen-en-presets)) |
| `--scope-profile` | — | Scopeprofiel, te combineren met `--aggressiveness`, zonder `--preset` |
| `--aggressiveness` | — | Agressiviteitsniveau, te combineren met `--scope-profile`, zonder `--preset` |
| `--auth-config` | — | YAML-bestand voor authenticatie |
| `--insecure-tls` | uitgeschakeld | Schakelt TLS-verificatie uit (activeert de versterkte bevestiging) |
| `--max-duration` | *(uit het profiel)* | Overschrijft de maximale duur (seconden) |
| `--max-requests` | *(uit het profiel)* | Overschrijft het maximale aantal verzoeken |
| `--max-tests` | *(uit het profiel)* | Overschrijft het maximale aantal tests |
| `--max-concurrent` | *(uit het profiel)* | Overschrijft de maximale gelijktijdigheid |
| `--dry-run` | uitgeschakeld | Toont de effectieve configuratie en het geschatte plan, verzendt geen verzoek |
| `--output-dir` | `var/exports/` | Map van de geëxporteerde rapporten, met de naam `<preset>-<tijdstempel>.<ext>` (aan te passen in Instellingen) |
| `--format` | `all` | `json`, `markdown`, `html` of `all` |
| `--export-theme` | `omega-base` | Thema van het geëxporteerde HTML-rapport (geen effect op json/markdown) |

De CLI heeft geen subopdracht `history`/`show`: de geschiedenis en de favoriete doelen zijn alleen in de TUI te bekijken.

Als de alias door `install.sh` is aangemaakt, werkt `fuzz scan ...` overal in de terminal, zonder het voorvoegsel `./omega-fuzz.sh`.

## 4. Scopeprofielen en presets

### Scopeprofielen

| Profiel | Modus | Max. diepte | Beperkingen |
|---|---|---|---|
| `strict` | exact doel | 1 | Blokkeert `/health`, `/ready`, `/metrics`, `/favicon.ico`, `/robots.txt` |
| `standard` | + subdomeinen | 2 | Blokkeert gangbare statische subdomeinen, technische paden, assets (afbeeldingen/css/js/lettertypen) |
| `large` | + subdomeinen | 4 | Blokkeert alleen technische paden en assets (inclusief archieven/PDF) |
| `api` | exact doel | 3 | Beperkt tot `/api`, `/v1`, `/v2`; blokkeert documentatie en assets |
| `custom` | + subdomeinen | 3 | Standaard geen beperking — uitgangspunt voor een handmatige configuratie |

Welk profiel je ook kiest, een lijst met binaire of omvangrijke extensies (`.iso`, `.zip`, `.exe`, `.mp4`...) wordt **altijd** uitgesloten van crawlen en fuzzing, ook onder `custom` — een link naar zo'n bestand wordt nooit met een echt HTTP-verzoek opgehaald, zodat een downloadmap een scan niet minutenlang vertraagt.

### Agressiviteitsniveaus

`doux` · `standard` · `agressif` · `violent` — elk heeft zijn eigen basislimieten (duur, verzoeken, tests, diepte, gelijktijdigheid), die zo nodig door een preset worden overschreven.

### Kant-en-klare presets

| Preset | Scope | Agressiviteit | Max. duur | Max. verzoeken | Max. tests | Max. diepte | Versterkte bevestiging |
|---|---|---|---|---|---|---|---|
| `prod-safe` | strict | doux | 300 s | 1.000 | 500 | 1 | nee |
| `staging-full` | standard | standard | 1.800 s | 20.000 | 10.000 | 2 | nee |
| `lab-deep` | large | agressif | 3.600 s | 100.000 | 50.000 | 4 | nee |
| `lab-extreme` | large | violent | 7.200 s | 500.000 | 250.000 | 5 | **ja** |
| `api-hardened` | api | agressif | 1.800 s | 50.000 | 25.000 | 3 | nee |

Een scan blijft geblokkeerd zolang hij niet bevestigd is. Een **versterkte** bevestiging (de exacte zin `OUI-J-AI-L-AUTORISATION` intypen) is vereist zodra een van deze drie factoren aanwezig is: agressiviteit `violent`, preset `lab-extreme` of uitgeschakelde TLS-verificatie (`--insecure-tls`) — voor een ongebruikelijke combinatie zonder een van deze drie factoren volstaat een eenvoudige ja/nee-bevestiging.

## 5. Uitgevoerde beveiligingstests

Automatische pipeline, op elke binnen de scope ontdekte URL (en elk `GET`-formulier dat daar gevonden wordt):

| Test | Aanleiding | Wat wordt gecontroleerd |
|---|---|---|
| Generieke parameterfuzzing | elke query-stringparameter | Gedrag van het doel bij grens- of misvormde waarden |
| Headerfuzzing | één keer per URL, 4 vaste headers (`User-Agent`, `Referer`, `X-Forwarded-For`, `Accept-Language`) | Gedrag van het doel bij grens- of misvormde waarden in een header |
| Formulierfuzzing (alleen `GET`) | elk veld van een `GET`-formulier dat binnen de scope ontdekt is | Gedrag van het doel bij grens- of misvormde waarden in een formulierveld |
| Gereflecteerde XSS | elke query-stringparameter | Ongefilterde reflectie van een payload in het antwoord (niet-destructief) |
| Generieke injectie | elke query-stringparameter | Detectie van een serverfout als antwoord op een injectiepayload (geen specifieke SQL/NoSQL-vingerafdruk) |
| Beveiligingsheaders | één keer per URL | Ontbrekende of verkeerd geconfigureerde beveiligingsheaders in het antwoord |

De eerste drie tests (generieke fuzzing van parameters/headers/formulieren) zijn een mutatie-engine **zonder detectie** — ze leveren nooit rechtstreeks een `Finding` op; alleen de aangetroffen serverfouten (5xx) worden bij de bijbehorende `Test` geteld. Alleen de signaturen (XSS, injectie, beveiligingsheaders) leveren findings op.

## 6. Score en ernst

Elke gedetecteerde afwijking krijgt een score op 3 assen (`impact`, `exploiteerbaarheid`, `bereik`, elk van 1 tot 5), afhankelijk van de aard van de waarneming — een bewust **voorzichtige** toewijzing (onderkant van de bandbreedte, geen menselijke bevestiging in deze automatische fase):

| Ruwe score (som van de 3 assen) | Ernst |
|---|---|
| ≥ 13 | `critical` |
| ≥ 10 | `high` |
| ≥ 7 | `medium` |
| < 7 | `low` |

Een handmatige aanpassing (`severity_override`) blijft mogelijk, maar vereist altijd een uitdrukkelijke motivering. Gelijkwaardige findings (zelfde type, zelfde endpoint, zelfde parameter) worden ontdubbeld, met behoud van het beste beschikbare bewijs (betrouwbaarheidsniveau `omega_lib.core.confidence.ConfidenceLevel`, bij gelijke stand daarna de ruwe score).

## 7. Authenticatie

Eigen YAML-bestand (`--auth-config`), nooit inloggegevens in platte tekst op de opdrachtregel:

| Modus | Effect |
|---|---|
| `none` | Geen authenticatie (standaard) |
| `cookie` | Rechtstreeks aangeleverde sessiecookie |
| `bearer_token` | Token `Authorization: Bearer ...` |
| `login_form` | Authenticatie via formulier (inlog-URL, velden gebruiker/wachtwoord) |

## 8. Architectuur

Omega-Fuzz is opgebouwd volgens **Clean Architecture** (domain / application / infrastructure / interfaces / ports / core / app / plugins), afgestemd op het sjabloon van de `omega-`-suite (zie `omega-check`/`omega-deep`/`omega-fold`) en bij elke wijziging gecontroleerd door `import-linter`. Alle details staan in **`docs/ARCHITECTURE.md`**.

Zeer kort overzicht:

```text
src/omega_fuzz/
├── domain/          Pure bedrijfslogica (doelen/scope, verzoeken, tests, findings, profielen, rapporten...)
├── application/     Use cases (commands/queries) en orchestrators (verkenning, scan, rapport, limieten)
├── ports/           Contracten die de applicatie verwacht (http_client, repositories, exporters...)
├── infrastructure/  Concrete implementaties (httpx, BeautifulSoup, SQLite, Jinja2-exporters — Textual staat hier NIET)
├── interfaces/      tui/ (Textual) en cli/ (scriptbaar), met strikte functionele gelijkwaardigheid
├── plugins/         Fuzzers en signaturen (pure functies, nooit directe netwerktoegang)
├── app/             Samenstelling (Container, composition root, levenscyclus)
└── core/            Gedeelde woordenschat, fouten, constanten
```

Ontwerpregels:
- `plugins/fuzzers/` en `plugins/signatures/`: pure functies die testplannen opbouwen (`Test` + `ScanRequest`), raken `HttpClient` nooit aan.
- `infrastructure/network/`: verzorgt het netwerk (`httpx`, streaming begrensd in het geheugen), oordeelt nooit.
- `infrastructure/analyzers/`: leest een al ontvangen antwoord, levert gestructureerde `Observation`-objecten, herberekent nooit een score.
- `interfaces/`: toont, bevat geen bedrijfslogica.

## 9. Exports

Markdown- en HTML-rapporten worden geschreven in de taal die in Instellingen gekozen is („Taal van de exports”, standaard die van de interface); JSON blijft gegevens en wordt niet vertaald. De rapporten worden standaard aangemaakt in `var/exports/` (runtimepad verankerd in de projectmap, `$OMEGA_FUZZ_VAR_DIR` om het te overschrijven, ook aan te passen in het scherm Instellingen), of op het opgegeven pad (`--output-dir`). Platte bestandsnaam, zonder submap: `<preset>-<tijdstempel>.<ext>` (bijv. `prod-safe-2026-09-01_14-30-22.html`).

### JSON, bron van waarheid

Volledige structuur van het rapport (effectieve configuratie, statistieken, tests, findings), strikt JSON-serialiseerbaar.

### Markdown, compact rapport voor mensen

Leesbaar buiten de terminal, zonder ANSI-codes.

### HTML, zelfstandig webrapport

5 thema's naar keuze (`--export-theme` in de CLI, keuzelijst in de TUI): `omega-base`, `omega-burn`, `omega-neon`, `light-basic`, `light-alt`.

## 10. Geschiedenis en favoriete doelen

Elke scan wordt met zijn findings opgeslagen (SQLite, `var/db/omega-fuzz.db`) en is te bekijken in het scherm Geschiedenis van de TUI. Alleen `Scan` en `Finding` worden bewaard — niet de effectieve configuratie en niet de afzonderlijke verzoeken — dus geen herhaling, vergelijking of nieuwe export vanuit dit scherm (het scherm legt dat uit in plaats van gegevens te verzinnen).

Het scherm **Doelen** bewaart een lijst met favorieten (genormaliseerde URL's, `var/targets.json`), waarmee je het veld Doel van een nieuwe scan direct kunt invullen.

## 11. Schermafbeeldingen

Opdracht **Schermafbeelding** van het palet (`Ctrl+P`): slaat een SVG van het huidige TUI-scherm standaard op in `var/screenshots/`, aan te passen in het scherm Instellingen (net als de exportmap). Een eigen opschoonfunctie is beschikbaar in Instellingen.

## 12. Terminalcompatibiliteit

De TUI (Textual) detecteert automatisch de mogelijkheden van de terminal (emulator, grootte) en past zijn structurele stylesheet daarop aan (`complete`/`standard`/`reduced`/`mono`), zonder handmatige optie. De CLI-modus blijft altijd platte tekst, onafhankelijk van de terminal. Dit beleid geldt voor de hele `omega-`-suite (`omega-lib`, `terminal/policies.py`).

### Profiel volgens de gedetecteerde emulator

| Emulator | Beginprofiel |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | `complete` |
| Konsole, GNOME Terminal, Terminator, Xfce4 Terminal | `standard` |
| xterm, urxvt, moderne SSH | `reduced` |
| Linux-TTY, oudere SSH | `mono` |
| Onbekende emulator | `reduced` (standaardterugval) |

### Profiel volgens de terminalgrootte

| Minimale grootte (kolommen × regels) | Profielplafond |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| kleiner | `mono` |

Het uiteindelijke profiel is **het strengste van de twee** (emulator en grootte) — live te vernieuwen met de toets `r`.

## 13. Tests

```bash
source .venv/bin/activate
lint-imports        # controleert de Dependency Rule (6 contracten)
pytest -q           # 344 tests
ruff check src tests
mypy -p omega_fuzz
```

Opbouw: `tests/unit/` (domein en applicatie, zonder echte I/O), `tests/integration/` (echt bestandssysteem via `tmp_path`, nep-HTTP-server `pytest-httpserver`, echte SQLite-database, CLI van begin tot eind), `tests/tui/` (navigatie via `Pilot`, structureel — geen zelfverklaarde visuele controle).

## 14. Buiten de reikwijdte

- Fuzzing van JSON-bodies (code aanwezig, niet aangesloten — geen ontdekking van API-schema's)
- Fuzzing van `POST`/`PUT`/`DELETE`-formulieren (bewust uitgesloten, risico op schrijfacties)
- Tests van bedrijfslogica (IDOR, autorisatie, werkstromen) buiten handmatige aanroep
- Gelijktijdig scannen van meerdere doelen
- Herhalen, vergelijken of exporteren vanuit de geschiedenis
- JavaScript-rendering aan de clientzijde
- Webdashboard

---

> Omega-Fuzz — Een omtrek verkennen, die met uitdrukkelijke waarborgen testen, nooit raden wat niet bevestigd is.

<p align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/nl/omega-fuzz/A.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/nl/omega-fuzz/B.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/nl/omega-fuzz/C.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/nl/omega-fuzz/D.png" width="24%" />
</p>
