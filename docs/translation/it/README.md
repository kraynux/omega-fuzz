<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - Licenza MIT (vedi file LICENSE) -->
<div align="center">
  <img src="../../assets/omega-fuzz.png" alt="Omega-Fuzz" width="384">
</div>

# 🗱 OMEGA-FUZZ

**Scanner di vulnerabilità**

> Realizzato da [kraynux](https://github.com/kraynux) per [Omega-Server](https://kraynux.snake-mackarel.ts.net)   

Pagina ufficiale: [OMEGA-FUZZ](https://kraynux.snake-mackarel.ts.net/omega-fuzz/) &nbsp; Anteprima: [Screenshot](https://kraynux.snake-mackarel.ts.net/omega-fuzz/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

🌐 Interfaccia e report esportati disponibili in **17 lingue** — vedi [Lingue dell'interfaccia](#lingue-dellinterfaccia).  
**Lingue:**  
<img src="https://flagcdn.com/w20/fr.png" alt="Français" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)

**Omega-Fuzz** è un'applicazione locale da terminale (TUI [Textual](https://github.com/Textualize/textual) + CLI scriptabile) che guida la scoperta e i test di sicurezza web (fuzzing HTTP) per ambienti autorizzati (laboratori, mirror personali, incarichi di test con consenso esplicito).

Strumento della suite `omega-`, strutturato in Clean Architecture — vedi `docs/ARCHITECTURE.md` per il dettaglio tecnico completo.

## 1. Visione e perimetro

### Cosa fa Omega-Fuzz

- Scopre il perimetro di un singolo obiettivo con un BFS limitato da uno scope esplicito (schema/sottodomini/percorsi consentiti-bloccati/profondità), mai senza salvaguardie.
- Fuzzing generico dei parametri della query string, delle intestazioni HTTP e dei moduli `GET` trovati su ogni URL scoperto, e verifica tre famiglie di firme: XSS riflesso non distruttivo, iniezione generica (rilevamento di errori nella risposta), intestazioni di sicurezza mancanti o mal configurate — vedi [§5](#5-test-di-sicurezza-eseguiti).
- Assegna un punteggio a ogni anomalia su 3 assi (impatto/sfruttabilità/portata) e ne ricava una severità (`low`/`medium`/`high`/`critical`), deduplicata per `(tipo, endpoint, parametro)` conservando la prova migliore — vedi [§6](#6-punteggio-e-severità).
- Supporta l'autenticazione (cookie, bearer token, modulo di login) tramite un file YAML dedicato, mai con credenziali in chiaro sulla riga di comando.
- Presenta il risultato nella TUI (Textual) o nella CLI scriptabile, con tre esportazioni (JSON, Markdown, HTML con 5 temi).
- Conserva una cronologia persistente delle scansioni e dei relativi findings (SQLite), e un elenco di obiettivi preferiti riutilizzabili.
- Richiede una conferma esplicita (frase rigorosa per i casi più sensibili) prima di qualsiasi scansione aggressiva, estesa o con la verifica TLS disattivata.

### Cosa Omega-Fuzz non fa

- Fuzzing dei corpi JSON — il codice esiste (`plugins/fuzzers/json_body_fuzzer.py`) ma non è collegato (la scoperta HTML/BFS non produce alcuno schema di API JSON né alcuna sorgente di template utilizzabile).
- Fuzzing dei moduli `POST`/`PUT`/`DELETE` — esclusi per scelta dalla pipeline automatica (rischio di scritture indesiderate sull'obiettivo); vengono testati solo i moduli `GET`.
- Test di logica applicativa (IDOR, controllo delle autorizzazioni, rottura del flusso di lavoro) — il codice esiste (`plugins/logic_tests/`) ma resta fuori dalla pipeline automatica, invocabile solo separatamente, mai attivato da una scansione standard.
- Scansione parallela di più obiettivi — un solo obiettivo per scansione.
- Riesecuzione, confronto o esportazione dalla schermata Cronologia — vengono salvati solo `Scan` e `Finding` (né la configurazione effettiva completa né le richieste), quindi rieseguire o esportare di nuovo dalla cronologia significherebbe inventare dati; la schermata lo spiega invece di proporlo in silenzio.
- Rendering JavaScript lato client (la pagina viene recuperata così come servita, non eseguita in un browser headless).
- Dashboard web.

## 2. Installazione

### Prerequisiti

- Python 3.10+
- Connessione Internet, per le dipendenze
- Per la TUI: un font [Nerd Font](https://www.nerdfonts.com/) installato nel terminale, per l'icona dell'intestazione — senza di esso, quel carattere appare come un quadrato vuoto (stesso limite di un'emoji, ma molto più diffuso tra gli utenti del terminale). La sua assenza non ha conseguenze sul funzionamento, è puramente estetica.

### Installazione

```bash
[ -d omega-fuzz ] && echo "ℹ️ Già estratto qui, passaggio saltato." || tar -xzf omega-fuzz.tar.gz
cd omega-fuzz/
chmod +x install.sh
./install.sh
```

`install.sh`:

1. Crea l'ambiente virtuale `.venv` se non esiste già.
2. Installa le dipendenze (`vendor/omega-lib/` poi `pip install -e .`, `pyproject.toml` resta l'unica fonte di verità).
3. Rende eseguibili `omega-fuzz.sh` e `install.sh`.
4. Aggiunge l'alias `fuzz` a `~/.bashrc` e `~/.zshrc` (senza duplicati se già presente).

### Dipendenze

Dichiarate in `pyproject.toml` (nessun `requirements.txt`):
- `omega-lib`: libreria condivisa della suite (temi di esportazione, rilevamento del terminale, `ConfidenceLevel`) — inclusa in `vendor/omega-lib/`
- `httpx`: richieste HTTP asincrone (scoperta + fuzzing), lettura della risposta in streaming (mai un buffer completo in memoria, nemmeno con un file di diversi GB servito dall'obiettivo)
- `beautifulsoup4` + `lxml`: estrazione degli URL e dei moduli HTML
- `jinja2`: template per l'esportazione HTML
- `textual`: interfaccia TUI, temi, adattamento automatico al terminale
- `pyyaml`: caricamento del file `--auth-config`
- Dipendenze di sviluppo (`pip install -e ".[dev]"`): `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-httpserver`, `ruff`, `mypy`, `import-linter`

## 3. Utilizzo

### Modalità interattiva (TUI)

Consigliata per l'uso quotidiano — avviata senza argomenti:

```bash
./omega-fuzz.sh
```
se hai creato l'alias, digita semplicemente `fuzz` nel terminale:
```bash
fuzz
```

Percorso: schermata iniziale (si chiude con un tasto o un clic) → menu principale (Scansiona / Obiettivi / Impostazioni / Cronologia / Aiuto) → inserimento dell'obiettivo (URL completo, schema `http://`/`https://` obbligatorio), preset o configurazione manuale (scope + aggressività), autenticazione facoltativa, verifica TLS, modifica dei limiti → schermata di revisione (conferma semplice, oppure frase rigorosa `OUI-J-AI-L-AUTORISATION` per i casi sensibili) → scansione (indicatore indeterminato, pulsante **Arresta** in qualsiasi momento) → risultati (findings, esportazione) → cronologia (dettaglio di una scansione passata, findings associati) e obiettivi preferiti dal menu principale. L'adattamento al terminale (colori, dimensioni, degradazione strutturale) è automatico.

#### Scorciatoie da tastiera

| Tasto | Azione |
|---|---|
| `↑` / `↓` | Spostarsi tra gli elementi di una schermata |
| `Tab` / `Maiusc+Tab` | Spostarsi tra i campi di un modulo |
| `Esc` | Tornare alla schermata precedente (conferma di uscita nella schermata iniziale) |
| `t` | Tema successivo (applicato subito, senza conferma) |
| `r` | Aggiornare il rilevamento del terminale |
| `a` | Mostrare l'aiuto (tabella dei preset inclusa) |
| `q` | Uscire (con conferma) |
| `Ctrl+P` | Tavolozza dei comandi (Theme, Esci, Screenshot) |

### Lingue dell'interfaccia

L'interfaccia è disponibile in 17 lingue: francese, inglese, spagnolo, portoghese (Brasile), italiano, tedesco, olandese, polacco, russo, cinese semplificato, vietnamita, thailandese, indonesiano, giapponese, coreano, hindi e arabo. La scelta si fa nelle Impostazioni («Langue / Language») e si applica dopo il riavvio dell'interfaccia; la variabile `OMEGA_FUZZ_LANG` (per esempio `OMEGA_FUZZ_LANG=en ./omega-fuzz.sh`) impone una lingua per la durata di una sessione. Avviato da omega-suite, omega-fuzz adotta la lingua della suite. Su una console di testo Linux (TTY), le lingue con scrittura non latina vengono mostrate in inglese per la sessione. La riga di comando resta in francese.

### Modalità scriptabile (CLI)

```bash
# Scansione con un preset pronto all'uso
./omega-fuzz.sh scan --target https://example.com --preset prod-safe

# Combinazione manuale scope + aggressività (senza preset)
./omega-fuzz.sh scan --target https://example.com --scope-profile standard --aggressiveness standard

# Con autenticazione (file YAML, mai credenziali in chiaro sulla riga di comando)
./omega-fuzz.sh scan --target https://example.com --preset staging-full --auth-config auth.yaml

# Dry-run: configurazione effettiva e piano stimato, nessuna richiesta inviata
./omega-fuzz.sh scan --target https://example.com --preset prod-safe --dry-run

# Esportazione mirata (cartella, formati, tema HTML)
./omega-fuzz.sh scan --target https://example.com --preset prod-safe \
    --output-dir ./rapports --format html --export-theme omega-neon
```

Opzioni di `scan`:

| Opzione | Predefinito | Effetto |
|---|---|---|
| `--target` | *(obbligatorio)* | URL dell'obiettivo, schema `http://`/`https://` obbligatorio (mai completato automaticamente) |
| `--preset` | — | Preset pronto all'uso (vedi [§4](#4-profili-di-scope-e-preset)) |
| `--scope-profile` | — | Profilo di scope, da combinare con `--aggressiveness`, senza `--preset` |
| `--aggressiveness` | — | Livello di aggressività, da combinare con `--scope-profile`, senza `--preset` |
| `--auth-config` | — | File YAML di autenticazione |
| `--insecure-tls` | disattivato | Disattiva la verifica TLS (attiva la conferma rafforzata) |
| `--max-duration` | *(dal profilo)* | Sostituisce la durata massima (secondi) |
| `--max-requests` | *(dal profilo)* | Sostituisce il numero massimo di richieste |
| `--max-tests` | *(dal profilo)* | Sostituisce il numero massimo di test |
| `--max-concurrent` | *(dal profilo)* | Sostituisce la concorrenza massima |
| `--dry-run` | disattivato | Mostra la configurazione effettiva e il piano stimato, non invia alcuna richiesta |
| `--output-dir` | `var/exports/` | Cartella dei report esportati, denominati `<preset>-<marca_temporale>.<ext>` (modificabile nelle Impostazioni) |
| `--format` | `all` | `json`, `markdown`, `html` o `all` |
| `--export-theme` | `omega-base` | Tema del report HTML esportato (nessun effetto su json/markdown) |

Non esiste un sottocomando `history`/`show` nella CLI: la cronologia e gli obiettivi preferiti si consultano solo dalla TUI.

Se l'alias è stato creato da `install.sh`, `fuzz scan ...` funziona da qualsiasi punto del terminale, senza il prefisso `./omega-fuzz.sh`.

## 4. Profili di scope e preset

### Profili di scope

| Profilo | Modalità | Profondità max | Restrizioni |
|---|---|---|---|
| `strict` | obiettivo esatto | 1 | Blocca `/health`, `/ready`, `/metrics`, `/favicon.ico`, `/robots.txt` |
| `standard` | + sottodomini | 2 | Blocca i sottodomini statici comuni, i percorsi tecnici, le risorse (immagini/css/js/font) |
| `large` | + sottodomini | 4 | Blocca solo i percorsi tecnici e le risorse (inclusi archivi/PDF) |
| `api` | obiettivo esatto | 3 | Limitato a `/api`, `/v1`, `/v2`; blocca documentazione e risorse |
| `custom` | + sottodomini | 3 | Nessuna restrizione predefinita — base di partenza per una configurazione manuale |

Qualunque sia il profilo scelto, un elenco di estensioni binarie o voluminose (`.iso`, `.zip`, `.exe`, `.mp4`...) è **sempre** escluso dal crawl e dal fuzzing, anche con `custom` — un link verso un file di questo tipo non viene mai scaricato con una vera richiesta HTTP, per evitare che una cartella di download rallenti una scansione per lunghi minuti.

### Livelli di aggressività

`doux` · `standard` · `agressif` · `violent` — ciascuno ha i propri limiti di base (durata, richieste, test, profondità, concorrenza), sostituiti da un preset quando presente.

### Preset pronti all'uso

| Preset | Scope | Aggressività | Durata max | Richieste max | Test max | Profondità max | Conferma rafforzata |
|---|---|---|---|---|---|---|---|
| `prod-safe` | strict | doux | 300 s | 1.000 | 500 | 1 | no |
| `staging-full` | standard | standard | 1.800 s | 20.000 | 10.000 | 2 | no |
| `lab-deep` | large | agressif | 3.600 s | 100.000 | 50.000 | 4 | no |
| `lab-extreme` | large | violent | 7.200 s | 500.000 | 250.000 | 5 | **sì** |
| `api-hardened` | api | agressif | 1.800 s | 50.000 | 25.000 | 3 | no |

Una scansione resta bloccata finché non viene confermata. È richiesta una conferma **rafforzata** (digitare la frase esatta `OUI-J-AI-L-AUTORISATION`) non appena è presente uno di questi tre fattori: aggressività `violent`, preset `lab-extreme` o verifica TLS disattivata (`--insecure-tls`) — per una combinazione insolita senza nessuno di questi tre fattori, conferma semplice sì/no.

## 5. Test di sicurezza eseguiti

Pipeline automatica, su ogni URL scoperto all'interno dello scope (e su ogni modulo `GET` trovato al suo interno):

| Test | Attivazione | Cosa viene verificato |
|---|---|---|
| Fuzzing generico dei parametri | qualsiasi parametro della query string | Comportamento dell'obiettivo di fronte a valori limite/malformati |
| Fuzzing delle intestazioni | una volta per URL, 4 intestazioni fisse (`User-Agent`, `Referer`, `X-Forwarded-For`, `Accept-Language`) | Comportamento dell'obiettivo di fronte a valori limite/malformati in un'intestazione |
| Fuzzing dei moduli (solo `GET`) | qualsiasi campo di modulo `GET` scoperto nello scope | Comportamento dell'obiettivo di fronte a valori limite/malformati in un campo di modulo |
| XSS riflesso | qualsiasi parametro della query string | Riflessione non filtrata di un payload nella risposta (non distruttivo) |
| Iniezione generica | qualsiasi parametro della query string | Rilevamento di un errore del server in risposta a un payload di iniezione (nessuna impronta SQL/NoSQL specifica) |
| Intestazioni di sicurezza | una volta per URL | Intestazioni di sicurezza mancanti o mal configurate nella risposta |

I primi tre test (fuzzing generico di parametri/intestazioni/moduli) sono un motore di mutazione **senza rilevamento** — non producono mai direttamente un `Finding`; vengono conteggiati sul `Test` corrispondente solo gli errori del server (5xx) incontrati. Solo le firme (XSS, iniezione, intestazioni di sicurezza) generano findings.

## 6. Punteggio e severità

Ogni anomalia rilevata viene valutata su 3 assi (`impatto`, `sfruttabilità`, `portata`, da 1 a 5 ciascuno) secondo la natura dell'osservazione — corrispondenza volutamente **prudente** (parte bassa dell'intervallo, nessuna conferma umana in questa fase automatica):

| Punteggio grezzo (somma dei 3 assi) | Severità |
|---|---|
| ≥ 13 | `critical` |
| ≥ 10 | `high` |
| ≥ 7 | `medium` |
| < 7 | `low` |

Una correzione manuale (`severity_override`) resta possibile ma richiede sempre una giustificazione esplicita. I findings equivalenti (stesso tipo, stesso endpoint, stesso parametro) vengono deduplicati, conservando la prova migliore disponibile (livello di confidenza `omega_lib.core.confidence.ConfidenceLevel`, poi punteggio grezzo in caso di parità).

## 7. Autenticazione

File YAML dedicato (`--auth-config`), mai credenziali in chiaro sulla riga di comando:

| Modalità | Effetto |
|---|---|
| `none` | Nessuna autenticazione (predefinito) |
| `cookie` | Cookie di sessione fornito direttamente |
| `bearer_token` | Token `Authorization: Bearer ...` |
| `login_form` | Autenticazione tramite modulo (URL di login, campi utente/password) |

## 8. Architettura

Omega-Fuzz è strutturato in **Clean Architecture** (domain / application / infrastructure / interfaces / ports / core / app / plugins), allineato al modello della suite `omega-` (vedi `omega-check`/`omega-deep`/`omega-fold`) e verificato da `import-linter` a ogni modifica. Il dettaglio completo si trova in **`docs/ARCHITECTURE.md`**.

Panoramica molto breve:

```text
src/omega_fuzz/
├── domain/          Logica applicativa pura (obiettivi/scope, richieste, test, findings, profili, report...)
├── application/     Casi d'uso (commands/queries) e orchestratori (scoperta, scansione, report, limiti)
├── ports/           Contratti attesi dall'applicazione (http_client, repositories, exporters...)
├── infrastructure/  Implementazioni concrete (httpx, BeautifulSoup, SQLite, esportatori Jinja2 — Textual NON è qui)
├── interfaces/      tui/ (Textual) e cli/ (scriptabile), con rigorosa parità funzionale
├── plugins/         Fuzzer e firme (funzioni pure, mai accesso diretto alla rete)
├── app/             Assemblaggio (Container, composition root, ciclo di vita)
└── core/            Vocabolario trasversale, errori, costanti
```

Regole di progettazione:
- `plugins/fuzzers/` e `plugins/signatures/`: funzioni pure che costruiscono piani di test (`Test` + `ScanRequest`), non toccano mai `HttpClient`.
- `infrastructure/network/`: gestisce la rete (`httpx`, streaming limitato in memoria), non giudica mai.
- `infrastructure/analyzers/`: legge una risposta già ricevuta, produce `Observation` strutturate, non ricalcola mai un punteggio.
- `interfaces/`: visualizza, non contiene alcuna logica applicativa.

## 9. Esportazioni

I report Markdown e HTML vengono scritti nella lingua scelta nelle Impostazioni («Lingua delle esportazioni», per impostazione predefinita quella dell'interfaccia); il JSON resta un dato, non tradotto. I report vengono generati in `var/exports/` per impostazione predefinita (percorso di runtime ancorato alla cartella del progetto, `$OMEGA_FUZZ_VAR_DIR` per sostituirlo, modificabile anche nella schermata Impostazioni), oppure nel percorso indicato (`--output-dir`). Nome di file piatto, senza sottocartella: `<preset>-<marca_temporale>.<ext>` (es. `prod-safe-2026-09-01_14-30-22.html`).

### JSON, fonte di verità

Struttura completa del report (configurazione effettiva, statistiche, test, findings), rigorosamente serializzabile in JSON.

### Markdown, report umano compatto

Leggibile fuori dal terminale, senza codici ANSI.

### HTML, report web autonomo

5 temi a scelta (`--export-theme` nella CLI, selettore nella TUI): `omega-base`, `omega-burn`, `omega-neon`, `light-basic`, `light-alt`.

## 10. Cronologia e obiettivi preferiti

Ogni scansione viene salvata (SQLite, `var/db/omega-fuzz.db`) con i suoi findings e si può consultare dalla schermata Cronologia della TUI. Vengono memorizzati solo `Scan` e `Finding` — né la configurazione effettiva né le richieste dettagliate — quindi nessuna riesecuzione, nessun confronto e nessuna nuova esportazione da questa schermata (la schermata lo spiega invece di inventare dati).

La schermata **Obiettivi** conserva un elenco di preferiti (URL normalizzati, `var/targets.json`), riutilizzabile per precompilare direttamente il campo Obiettivo di una nuova scansione.

## 11. Screenshot

Comando **Screenshot** della tavolozza (`Ctrl+P`): salva un SVG della schermata TUI corrente in `var/screenshots/` per impostazione predefinita, modificabile nella schermata Impostazioni (come la cartella di esportazione). Pulizia dedicata disponibile nelle Impostazioni.

## 12. Compatibilità dei terminali

La TUI (Textual) rileva automaticamente le capacità del terminale (emulatore, dimensioni) e adatta di conseguenza il proprio foglio di stile strutturale (`complete`/`standard`/`reduced`/`mono`), senza opzione manuale. La modalità CLI resta sempre in testo semplice, indipendente dal terminale. Politica condivisa da tutta la suite `omega-` (`omega-lib`, `terminal/policies.py`).

### Profilo in base all'emulatore rilevato

| Emulatore | Profilo iniziale |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | `complete` |
| Konsole, GNOME Terminal, Terminator, Xfce4 Terminal | `standard` |
| xterm, urxvt, SSH moderno | `reduced` |
| TTY Linux, SSH datato | `mono` |
| Emulatore non riconosciuto | `reduced` (ripiego predefinito) |

### Profilo in base alle dimensioni del terminale

| Dimensione minima (colonne × righe) | Tetto del profilo |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| al di sotto | `mono` |

Il profilo finale adottato è **il più restrittivo dei due** (emulatore e dimensioni) — aggiornabile in diretta con il tasto `r`.

## 13. Test

```bash
source .venv/bin/activate
lint-imports        # verifica la Dependency Rule (6 contratti)
pytest -q           # 344 test
ruff check src tests
mypy -p omega_fuzz
```

Struttura: `tests/unit/` (dominio e applicazione, senza I/O reale), `tests/integration/` (vero filesystem tramite `tmp_path`, server HTTP fittizio `pytest-httpserver`, vero database SQLite, CLI end-to-end), `tests/tui/` (navigazione tramite `Pilot`, strutturale — nessuna verifica visiva autoproclamata).

## 14. Fuori perimetro

- Fuzzing dei corpi JSON (codice presente, non collegato — nessuna scoperta di schemi di API)
- Fuzzing dei moduli `POST`/`PUT`/`DELETE` (esclusi per scelta, rischio di scrittura)
- Test di logica applicativa (IDOR, autorizzazioni, flusso di lavoro) al di fuori dell'invocazione manuale
- Scansione simultanea di più obiettivi
- Riesecuzione, confronto o esportazione dalla cronologia
- Rendering JavaScript lato client
- Dashboard web

---

> Omega-Fuzz — Scoprire un perimetro, testarlo con salvaguardie esplicite, non indovinare mai ciò che non è stato confermato.
