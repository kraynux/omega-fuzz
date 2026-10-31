<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - Licencja MIT (zobacz plik LICENSE) -->
<div align="center">
  <img src="../../assets/omega-fuzz.png" alt="Omega-Fuzz" width="384">
</div>

# 🗱 OMEGA-FUZZ

**Skaner podatności**

> Opracowany przez [kraynux](https://github.com/kraynux) dla [Omega-Server](https://kraynux.snake-mackarel.ts.net)   

Oficjalna strona: [OMEGA-FUZZ](https://kraynux.snake-mackarel.ts.net/omega-fuzz/) &nbsp; Zrzuty ekranu: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-fuzz/screenshots/)  

[![Licencja: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platforma](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interfejs](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

🌐 Interfejs i eksportowane raporty są dostępne w **17 językach** — zobacz [Języki interfejsu](#języki-interfejsu).  
**Języki:**  
<img src="https://flagcdn.com/w20/fr.png" alt="Français" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)

**Omega-Fuzz** to lokalna aplikacja terminalowa (TUI [Textual](https://github.com/Textualize/textual) + skryptowalny CLI), która prowadzi odkrywanie i testy bezpieczeństwa aplikacji webowych (fuzzing HTTP) w środowiskach autoryzowanych: laboratoriach, osobistych kopiach lub testach, na które wyraźnie wyrażono zgodę.

Narzędzie należy do rodziny `omega-` i jest zbudowane w architekturze Clean Architecture — pełne szczegóły techniczne znajdują się w `docs/ARCHITECTURE.md`.

## 1. Cel i zakres

### Co robi Omega-Fuzz

- Odkrywa obszar pojedynczego celu metodą BFS ograniczoną przez jawny zakres (schemat, subdomeny, dozwolone i zablokowane ścieżki, głębokość), nigdy bez zabezpieczeń.
- Wykonuje ogólny fuzzing parametrów query string, nagłówków HTTP oraz formularzy `GET` znalezionych na każdym odkrytym adresie URL i sprawdza trzy rodzaje sygnatur: niezniszczający refleksyjny XSS, ogólne wstrzyknięcie (wykrywanie błędu w odpowiedzi) oraz brakujące lub błędnie skonfigurowane nagłówki bezpieczeństwa — zobacz [§5](#5-wykonywane-testy-bezpieczeństwa).
- Ocenia każdą anomalię w trzech wymiarach (wpływ, podatność na wykorzystanie, zasięg) i na tej podstawie określa severity (`low`, `medium`, `high`, `critical`), usuwając duplikaty według `(typ, endpoint, parametr)` i zachowując najlepszy dowód — zobacz [§6](#6-ocena-i-severity).
- Obsługuje uwierzytelnianie (cookie, token bearer, formularz logowania) przez dedykowany plik YAML; dane uwierzytelniające nigdy nie są podawane jawnie w wierszu poleceń.
- Prezentuje wyniki w TUI (Textual) lub skryptowalnym CLI, z trzema formatami eksportu (JSON, Markdown, HTML w 5 motywach).
- Przechowuje trwałą historię skanów i ich findings w SQLite oraz listę wielokrotnego użytku ulubionych celów.
- Wymaga jawnego potwierdzenia (dokładnej frazy w najbardziej wrażliwych przypadkach) przed każdym skanem agresywnym, rozszerzonym lub przeprowadzanym z wyłączoną weryfikacją TLS.

### Czego Omega-Fuzz nie robi

- Fuzzingu treści JSON — kod istnieje (`plugins/fuzzers/json_body_fuzzer.py`), ale nie jest podłączony (odkrywanie HTML/BFS nie produkuje żadnego schematu API JSON ani użytecznego źródła szablonu).
- Fuzzingu formularzy `POST`/`PUT`/`DELETE` — wykluczony z wyboru w automatycznym pipeline (ryzyko niezamierzonego zapisu na celu); testowane są wyłącznie formularze `GET`.
- Testów logiki biznesowej (IDOR, kontrola autoryzacji, przerwanie workflow) — kod istnieje (`plugins/logic_tests/`), ale pozostaje poza automatycznym pipeline; można go wywołać wyłącznie osobno i nigdy nie jest uruchamiany przez standardowy skan.
- Równoległego skanowania wielu celów — jeden cel na skan.
- Ponownego uruchamiania, porównywania ani eksportowania z ekranu Historia — persistowane są wyłącznie `Scan` i `Finding` (nie pełna efektywna konfiguracja ani żądania); ponowne uruchomienie lub eksport z historii tworzyłoby dane. Ekran to wyjaśnia, zamiast oferować tę funkcję po cichu.
- Renderowania JavaScript po stronie klienta (strona jest pobierana tak, jak została serwowana, a nie wykonywana w przeglądarce headless).
- Panelu webowego.

## 2. Instalacja

### Wymagania

- Python 3.10+
- Połączenie z Internetem, aby pobrać zależności
- Dla TUI: czcionka [Nerd Font](https://www.nerdfonts.com/) zainstalowana w terminalu, aby wyświetlić ikonę nagłówka — bez niej znak wyświetla się jako pusty kwadrat (to samo ograniczenie co emoji, ale znacznie częściej dostępne wśród użytkowników terminala). Brak czcionki nie wpływa na działanie; jest wyłącznie kwestią wyglądu.

### Instalacja

```bash
[ -d omega-fuzz ] && echo "ℹ️ Już rozpakowano tutaj, pomijam ten krok." || tar -xzf omega-fuzz.tar.gz
cd omega-fuzz/
chmod +x install.sh
./install.sh
```

Skrypt `install.sh`:

1. Tworzy środowisko wirtualne `.venv`, jeśli jeszcze nie istnieje.
2. Instaluje zależności (`vendor/omega-lib/`, a następnie `pip install -e .`; `pyproject.toml` pozostaje jedynym źródłem prawdy).
3. Nadaje uprawnienia wykonywania plikom `omega-fuzz.sh` i `install.sh`.
4. Dodaje alias `fuzz` do `~/.bashrc` i `~/.zshrc` (bez duplikatu, jeśli już istnieje).

### Zależności

Zadeklarowane w `pyproject.toml` (brak `requirements.txt`):

- `omega-lib` — wspólna biblioteka rodziny narzędzi (motywy eksportu, wykrywanie terminala, `ConfidenceLevel`) — dostarczana w `vendor/omega-lib/`
- `httpx` — asynchroniczne żądania HTTP (odkrywanie + fuzzing) oraz strumieniowanie odpowiedzi (nigdy pełny bufor w pamięci, nawet przy pliku o rozmiarze kilku GB serwowanym przez cel)
- `beautifulsoup4` + `lxml` — ekstrakcja adresów URL i formularzy HTML
- `jinja2` — szablony eksportu HTML
- `textual` — interfejs TUI, motywy, automatyczne dopasowanie do terminala
- `pyyaml` — wczytywanie pliku `--auth-config`
- Zależności deweloperskie (`pip install -e ".[dev]"`): `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-httpserver`, `ruff`, `mypy`, `import-linter`

## 3. Użycie

### Tryb interaktywny (TUI)

Zalecany do codziennego użytku — uruchamiany bez argumentów:

```bash
./omega-fuzz.sh
```

jeśli utworzono alias, wystarczy wpisać w terminalu `fuzz`:

```bash
fuzz
```

Przebieg: ekran startowy (zamyka się po naciśnięciu klawisza lub kliknięciu) → menu główne (Skanuj / Cele / Ustawienia / Historia / Pomoc) → wprowadzenie celu (pełny adres URL, wymagany schemat `http://`/`https://`), preset lub konfiguracja ręczna (zakres + agresywność), opcjonalne uwierzytelnianie, weryfikacja TLS, nadpisania limitów → ekran przeglądu (proste potwierdzenie albo dokładna fraza `OUI-J-AI-L-AUTORISATION` w przypadkach wrażliwych) → skan (nieokreślony wskaźnik postępu, przycisk **Zatrzymaj** dostępny w każdej chwili) → wyniki (findings, eksport) → historia (szczegóły przeszłego skanu i powiązane findings) oraz ulubione cele dostępne z menu głównego. Dopasowanie do terminala (kolory, rozmiar, degradacja struktury) odbywa się automatycznie.

#### Skróty klawiszowe

| Klawisz | Działanie |
|---|---|
| `↑` / `↓` | Nawigacja między elementami ekranu |
| `Tab` / `Shift+Tab` | Nawigacja między polami formularza |
| `Esc` | Powrót do poprzedniego ekranu (potwierdzenie wyjścia na ekranie startowym) |
| `t` | Następny motyw ( stosowany natychmiast, bez potwierdzenia) |
| `r` | Odświeżenie wykrywania terminala |
| `a` | Wyświetlenie pomocy (tabela dołączonych presetów) |
| `q` | Wyjście (z potwierdzeniem) |
| `Ctrl+P` | Paleta poleceń (Theme, Wyjdź, Zrzut ekranu) |

### Języki interfejsu

Interfejs jest dostępny w 17 językach: francuskim, angielskim, hiszpańskim, portugalskim (Brazylia), włoskim, niemieckim, niderlandzkim, polskim, rosyjskim, chińskim uproszczonym, wietnamskim, tajskim, indonezyjskim, japońskim, koreańskim, hindi i arabskim. Język wybiera się w Ustawieniach („Język / Language”) i stosuje po ponownym uruchomieniu interfejsu; zmienna `OMEGA_FUZZ_LANG` (np. `OMEGA_FUZZ_LANG=en ./omega-fuzz.sh`) wymusza język na czas jednej sesji. Uruchomiony z omega-suite, omega-fuzz przyjmuje język całego zestawu. W tekstowej konsoli Linuksa (TTY) języki z pismem nielacińskim wyświetlają się w języku angielskim na czas sesji. Interfejs wiersza poleceń pozostaje w języku francuskim.

### Tryb skryptowy (CLI)

```bash
# Skan z gotowym presetem
./omega-fuzz.sh scan --target https://example.com --preset prod-safe

# Ręczna kombinacja zakresu i agresywności (bez presetu)
./omega-fuzz.sh scan --target https://example.com --scope-profile standard --aggressiveness standard

# Z uwierzytelnianiem (plik YAML, nigdy jawne dane w wierszu poleceń)
./omega-fuzz.sh scan --target https://example.com --preset staging-full --auth-config auth.yaml

# Dry-run: efektywna konfiguracja i szacowany plan, żadne żądanie nie jest wysyłane
./omega-fuzz.sh scan --target https://example.com --preset prod-safe --dry-run

# Eksport docelowy (katalog, formaty, motyw HTML)
./omega-fuzz.sh scan --target https://example.com --preset prod-safe \
    --output-dir ./rapports --format html --export-theme omega-neon
```

Opcje polecenia `scan`:

| Opcja | Domyślnie | Działanie |
|---|---|---|
| `--target` | *(wymagane)* | Docelowy adres URL, wymagany schemat `http://`/`https://` (nigdy nie jest uzupełniany automatycznie) |
| `--preset` | — | Gotowy preset (zobacz [§4](#4-profile-zakresu-i-presety)) |
| `--scope-profile` | — | Profil zakresu, do połączenia z `--aggressiveness`, bez `--preset` |
| `--aggressiveness` | — | Poziom agresywności, do połączenia z `--scope-profile`, bez `--preset` |
| `--auth-config` | — | Plik YAML uwierzytelniania |
| `--insecure-tls` | wyłączone | Wyłącza weryfikację TLS (wyzwala wzmocnione potwierdzenie) |
| `--max-duration` | *(z profilu)* | Nadpisuje maksymalny czas trwania (sekundy) |
| `--max-requests` | *(z profilu)* | Nadpisuje maksymalną liczbę żądań |
| `--max-tests` | *(z profilu)* | Nadpisuje maksymalną liczbę testów |
| `--max-concurrent` | *(z profilu)* | Nadpisuje maksymalną współbieżność |
| `--dry-run` | wyłączone | Wyświetla efektywną konfigurację i szacowany plan, nie wysyła żadnego żądania |
| `--output-dir` | `var/exports/` | Katalog eksportowanych raportów, nazywanych `<preset>-<znacznik czasu>.<rozszerzenie>` (można nadpisać w Ustawieniach) |
| `--format` | `all` | `json`, `markdown`, `html` lub `all` |
| `--export-theme` | `omega-base` | Motyw eksportowanego raportu HTML (bez wpływu na json/markdown) |

Nie istnieje podpolecenie `history`/`show` w CLI: historia i ulubione cele są dostępne wyłącznie w TUI.

Jeśli alias został utworzony przez `install.sh`, polecenie `fuzz scan ...` działa z dowolnego miejsca w terminalu, bez prefiksu `./omega-fuzz.sh`.

## 4. Profile zakresu i presety

### Profile zakresu

| Profil | Tryb | Maks. głębokość | Ograniczenia |
|---|---|---|---|
| `strict` | dokładny cel | 1 | Blokuje `/health`, `/ready`, `/metrics`, `/favicon.ico`, `/robots.txt` |
| `standard` | + subdomeny | 2 | Blokuje typowe statyczne subdomeny, ścieżki techniczne i zasoby (obrazy/css/js/fonty) |
| `large` | + subdomeny | 4 | Blokuje wyłącznie ścieżki techniczne i zasoby (w tym archiwa/PDF) |
| `api` | dokładny cel | 3 | Ogranicza do `/api`, `/v1`, `/v2`; blokuje dokumentację i zasoby |
| `custom` | + subdomeny | 3 | Brak domyślnych ograniczeń — punkt wyjścia dla konfiguracji ręcznej |

Niezależnie od wybranego profilu lista rozszerzeń binarnych/dużych plików (`.iso`, `.zip`, `.exe`, `.mp4`...) jest **zawsze** wykluczana z crawlowania i fuzzingu, nawet w trybie `custom` — link do pliku tego typu nigdy nie jest pobierany rzeczywistym żądaniem HTTP, aby katalog pobieranych plików nie spowalniał skanu przez wiele minut.

### Poziomy agresywności

`doux` · `standard` · `agressif` · `violent` — każdy poziom ma własne podstawowe limity (czas, żądania, testy, głębokość, współbieżność), nadpisywane przez preset, jeśli jest on określony.

### Gotowe presety

| Preset | Zakres | Agresywność | Maks. czas | Maks. żądania | Maks. testy | Maks. głębokość | Wzmocnione potwierdzenie |
|---|---|---|---|---|---|---|---|
| `prod-safe` | strict | doux | 300 s | 1 000 | 500 | 1 | nie |
| `staging-full` | standard | standard | 1 800 s | 20 000 | 10 000 | 2 | nie |
| `lab-deep` | large | agressif | 3 600 s | 100 000 | 50 000 | 4 | nie |
| `lab-extreme` | large | violent | 7 200 s | 500 000 | 250 000 | 5 | **tak** |
| `api-hardened` | api | agressif | 1 800 s | 50 000 | 25 000 | 3 | nie |

Skan jest blokowany do momentu potwierdzenia. **Wzmocnione** potwierdzenie (wpisanie dokładnej frazy `OUI-J-AI-L-AUTORISATION`) jest wymagane, gdy występuje dowolny z tych trzech czynników: agresywność `violent`, preset `lab-extreme` lub wyłączona weryfikacja TLS (`--insecure-tls`) — w nietypowej kombinacji bez żadnego z tych czynników wymagane jest zwykłe potwierdzenie tak/nie.

## 5. Wykonywane testy bezpieczeństwa

Automatyczny pipeline, dla każdego adresu URL odkrytego w zakresie (oraz każdego znalezionego tam formularza `GET`):

| Test | Uruchomienie | Co jest sprawdzane |
|---|---|---|
| Ogólny fuzzing parametrów | każdy parametr query string | Zachowanie celu wobec wartości granicznych lub nieprawidłowych |
| Fuzzing nagłówków | raz na URL, 4 stałe nagłówki (`User-Agent`, `Referer`, `X-Forwarded-For`, `Accept-Language`) | Zachowanie celu wobec wartości granicznych lub nieprawidłowych w nagłówku |
| Fuzzing formularza (wyłącznie `GET`) | każde pole formularza `GET` odkryte w zakresie | Zachowanie celu wobec wartości granicznych lub nieprawidłowych w polu formularza |
| Refleksyjny XSS | każdy parametr query string | Niefiltrowane odbicie payloadu w odpowiedzi (niezniszczające) |
| Ogólne wstrzyknięcie | każdy parametr query string | Wykrywanie błędu serwera po payloadzie iniekcji (bez specyficznego fingerprintingu SQL/NoSQL) |
| Nagłówki bezpieczeństwa | raz na URL | Brakujące lub błędnie skonfigurowane nagłówki bezpieczeństwa w odpowiedzi |

Pierwsze trzy testy (ogólny fuzzing parametrów/nagłówków/formularza) to silnik mutacji **bez detekcji** — nigdy nie tworzą bezpośrednio `Finding`; jedynie napotkane błędy serwera (5xx) są zliczane w odpowiednim `Test`. Findings generują wyłącznie sygnatury (XSS, iniekcja, nagłówki bezpieczeństwa).

## 6. Ocena i severity

Każda wykryta anomalia jest oceniana w trzech wymiarach (`impact`, `exploitability`, `scope`, po 1–5 punktów) zgodnie z charakterem obserwacji — mapowanie jest celowo **konserwatywne** (dolna granica zakresu, brak ludzkiego potwierdzenia na tym automatycznym etapie):

| Wynik surowy (suma 3 wymiarów) | Severity |
|---|---|
| ≥ 13 | `critical` |
| ≥ 10 | `high` |
| ≥ 7 | `medium` |
| < 7 | `low` |

Ręczne dostosowanie (`severity_override`) pozostaje możliwe, ale zawsze wymaga jawnego uzasadnienia. Równoważne findings (ten sam typ, ten sam endpoint, ten sam parametr) są deduplikowane, a zachowywany jest najlepszy dostępny dowód (poziom pewności `omega_lib.core.confidence.ConfidenceLevel`, następnie wynik surowy w przypadku remisu).

## 7. Uwierzytelnianie

Dedykowany plik YAML (`--auth-config`), nigdy jawne dane uwierzytelniające w wierszu poleceń:

| Tryb | Działanie |
|---|---|
| `none` | Brak uwierzytelniania (domyślnie) |
| `cookie` | Bezpośrednio dostarczony cookie sesji |
| `bearer_token` | Token `Authorization: Bearer ...` |
| `login_form` | Uwierzytelnianie przez formularz (adres URL logowania, pola użytkownika/hasła) |

## 8. Architektura

Omega-Fuzz jest zorganizowany w **Clean Architecture** (domain / application / infrastructure / interfaces / ports / core / app / plugins), zgodnie ze wzorcem rodziny `omega-` (zobacz `omega-check`/`omega-deep`/`omega-fold`) i weryfikowany przez `import-linter` przy każdej modyfikacji. Pełne szczegóły znajdują się w **`docs/ARCHITECTURE.md`**.

Bardzo krótki przegląd:

```text
src/omega_fuzz/
├── domain/          Czysta logika domenowa (cele/zakres, żądania, testy, findings, profile, raporty...)
├── application/     Przypadki użycia (commands/queries) i orkiestratory (odkrywanie, skan, raport, limity)
├── ports/           Kontrakty oczekiwane przez aplikację (http_client, repositories, exporters...)
├── infrastructure/  Konkretne implementacje (httpx, BeautifulSoup, SQLite, eksporterzy Jinja2 — Textual NIE jest tutaj)
├── interfaces/      tui/ (Textual) i cli/ (skryptowalny), przy ścisłej parzystości funkcjonalnej
├── plugins/         Fuzzery i sygnatury (funkcje czyste, nigdy bezpośredni dostęp do sieci)
├── app/             Składanie (Container, composition root, cykl życia)
└── core/            Wspólne słownictwo, błędy, stałe
```

Zasady projektowe:

- `plugins/fuzzers/` i `plugins/signatures/`: funkcje czyste budujące plany testów (`Test` + `ScanRequest`), nigdy nie używają `HttpClient`.
- `infrastructure/network/`: wykonuje operacje sieciowe (`httpx`, strumieniowanie z ograniczeniem pamięci), nigdy nie ocenia.
- `infrastructure/analyzers/`: czyta już otrzymaną odpowiedź, produkuje ustrukturyzowane `Observation`, nigdy nie przelicza oceny.
- `interfaces/`: wyświetla, nie zawiera logiki biznesowej.

## 9. Eksporty

Raporty Markdown i HTML są zapisywane w języku wybranym w Ustawieniach („Język eksportów”, domyślnie język interfejsu); JSON pozostaje danymi i nie jest tłumaczony. Raporty są domyślnie generowane w `var/exports/` (ścieżka runtime zakotwiczona w katalogu projektu, `$OMEGA_FUZZ_VAR_DIR` aby ją nadpisać, nadpisywana również w ekranie Ustawienia) albo pod wskazaną ścieżką (`--output-dir`). Płaska nazwa pliku, bez podkatalogu: `<preset>-<znacznik czasu>.<rozszerzenie>` (np. `prod-safe-2026-09-01_14-30-22.html`).

### JSON, źródło prawdy

Pełna struktura raportu (efektywna konfiguracja, statystyki, testy, findings), ściśle serializowalna do JSON.

### Markdown, zwięzły raport dla człowieka

Czytelny poza terminalem, bez kodów ANSI.

### HTML, samodzielny raport webowy

5 motywów do wyboru (`--export-theme` w CLI, selektor w TUI): `omega-base`, `omega-burn`, `omega-neon`, `light-basic`, `light-alt`.

## 10. Historia i ulubione cele

Każdy skan jest persistowany (SQLite, `var/db/omega-fuzz.db`) wraz ze swoimi findings i dostępny z ekranu Historia w TUI. Persistowane są wyłącznie `Scan` i `Finding` — nie pełna efektywna konfiguracja ani szczegółowe żądania — więc z tego ekranu nie ma ponownego uruchomienia, porównania ani nowego eksportu (ekran to wyjaśnia, zamiast tworzyć dane).

Ekran **Cele** przechowuje listę ulubionych (znormalizowane adresy URL, `var/targets.json`), wielokrotnego użytku do bezpośredniego wypełniania pola Cel nowego skanu.

## 11. Zrzuty ekranu

Polecenie **Zrzut ekranu** z palety (`Ctrl+P`): zapisuje SVG bieżącego ekranu TUI domyślnie w `var/screenshots/`, z możliwością nadpisania w ekranie Ustawienia (tak jak katalog eksportu). W Ustawieniach dostępne jest dedykowane czyszczenie.

## 12. Kompatybilność terminali

TUI (Textual) automatycznie wykrywa możliwości terminala (emulator, rozmiar) i odpowiednio dostosowuje strukturę arkusza stylów (`complete`/`standard`/`reduced`/`mono`), bez ręcznej flagi. CLI zawsze pozostaje w zwykłym tekście, niezależnie od terminala. Polityka współdzielona przez całą rodzinę `omega-` (`omega-lib`, `terminal/policies.py`).

### Profil według wykrytego emulatora

| Emulator | Profil początkowy |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | `complete` |
| Konsole, GNOME Terminal, Terminator, Xfce4 Terminal | `standard` |
| xterm, urxvt, nowoczesny SSH | `reduced` |
| TTY Linux, starszy SSH | `mono` |
| Nierozpoznany emulator | `reduced` (domyślny fallback) |

### Profil według rozmiaru terminala

| Minimalny rozmiar (kolumny × wiersze) | Limit profilu |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| poniżej | `mono` |

Końcowy profil to **bardziej restrykcyjny z dwóch** (emulator i rozmiar) — można go odświeżyć na żywo klawiszem `r`.

## 13. Testy

```bash
source .venv/bin/activate
lint-imports        # weryfikuje Dependency Rule (6 kontraktów)
pytest -q           # 344 testy
ruff check src tests
mypy -p omega_fuzz
```

Struktura: `tests/unit/` (domena i aplikacja, bez rzeczywistego I/O), `tests/integration/` (prawdziwy system plików przez `tmp_path`, fałszywy serwer HTTP `pytest-httpserver`, prawdziwa baza SQLite, CLI end-to-end), `tests/tui/` (nawigacja przez `Pilot`, testy strukturalne — bez samozwańczej automatycznej weryfikacji wizualnej).

## 14. Poza zakresem

- Fuzzing treści JSON (kod obecny, niepodłączony — brak odkrywania schematu API)
- Fuzzing formularzy `POST`/`PUT`/`DELETE` (wykluczony z wyboru, ryzyko zapisu)
- Testy logiki biznesowej (IDOR, autoryzacja, workflow) poza ręcznym wywołaniem
- Równoległe skanowanie wielu celów
- Ponowne uruchamianie, porównywanie lub eksportowanie z historii
- Renderowanie JavaScript po stronie klienta
- Panel webowy

---

> Omega-Fuzz — odkryj zakres, przetestuj go z jawnymi zabezpieczeniami i nigdy nie zgaduj tego, czego nie potwierdzono.
