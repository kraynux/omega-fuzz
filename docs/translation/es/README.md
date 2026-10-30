<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - Licencia MIT (ver archivo LICENSE) -->
<div align="center">
  <img src="../../assets/omega-fuzz.png" alt="Omega-Fuzz" width="384">
</div>

# 🗱 OMEGA-FUZZ

**Escáner de vulnerabilidades**

> Desarrollado por **kraynux** para **Omega-server** 
[https://kraynux.snake-mackarel.ts.net](https://kraynux.snake-mackarel.ts.net)

Página oficial: [OMEGA-FUZZ](https://kraynux.snake-mackarel.ts.net/omega-fuzz/) &nbsp; Vista previa: [Capturas](https://kraynux.snake-mackarel.ts.net/omega-fuzz/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

🌐 Interfaz e informes exportados disponibles en **17 idiomas** — ver [Idiomas de la interfaz](#idiomas-de-la-interfaz).  
**Idiomas:**  
<img src="https://flagcdn.com/w20/fr.png" alt="Français" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)

**Omega-Fuzz** es una aplicación local de terminal (TUI [Textual](https://github.com/Textualize/textual) + CLI scriptable) que dirige el descubrimiento y las pruebas de seguridad web (fuzzing HTTP) para entornos autorizados (laboratorios, réplicas personales, encargos de prueba con consentimiento explícito).

Herramienta de la suite `omega-`, estructurada en Clean Architecture — ver `docs/ARCHITECTURE.md` para el detalle técnico completo.

## 1. Visión y alcance

### Lo que hace Omega-Fuzz

- Descubre el perímetro de un objetivo único mediante un BFS acotado por un alcance explícito (esquema/subdominios/rutas permitidas-bloqueadas/profundidad), nunca sin salvaguardas.
- Fuzzing genérico de los parámetros de query string, de las cabeceras HTTP y de los formularios `GET` encontrados en cada URL descubierta, y comprueba tres familias de firmas: XSS reflejado no destructivo, inyección genérica (detección de error en la respuesta), cabeceras de seguridad ausentes o mal configuradas — ver [§5](#5-pruebas-de-seguridad-ejecutadas).
- Puntúa cada anomalía en 3 ejes (impacto/explotabilidad/alcance) y deduce de ello una severidad (`low`/`medium`/`high`/`critical`), deduplicada por `(tipo, endpoint, parámetro)` conservando la mejor prueba — ver [§6](#6-puntuación-y-severidad).
- Admite autenticación (cookie, bearer token, formulario de inicio de sesión) mediante un archivo YAML dedicado, nunca con credenciales en claro en la línea de comandos.
- Presenta el resultado en la TUI (Textual) o en la CLI scriptable, con tres exportaciones (JSON, Markdown, HTML con 5 temas).
- Conserva un historial persistente de los escaneos y de sus findings (SQLite), y una lista de objetivos favoritos reutilizables.
- Exige una confirmación explícita (frase estricta para los casos más sensibles) antes de cualquier escaneo agresivo, extendido o con la verificación TLS desactivada.

### Lo que Omega-Fuzz no hace

- Fuzzing de cuerpos JSON — el código existe (`plugins/fuzzers/json_body_fuzzer.py`) pero no está conectado (el descubrimiento HTML/BFS no produce ningún esquema de API JSON ni ninguna fuente de plantilla aprovechable).
- Fuzzing de formularios `POST`/`PUT`/`DELETE` — excluidos por decisión del pipeline automático (riesgo de escritura no deseada en el objetivo); solo se prueban los formularios `GET`.
- Pruebas de lógica de negocio (IDOR, control de autorización, ruptura de flujo de trabajo) — el código existe (`plugins/logic_tests/`) pero queda fuera del pipeline automático, solo se puede invocar por separado y nunca lo desencadena un escaneo estándar.
- Escaneo multiobjetivo en paralelo — un único objetivo por escaneo.
- Repetición, comparación o exportación desde la pantalla Historial — solo se guardan `Scan` y `Finding` (ni la configuración efectiva completa ni las peticiones), así que repetir o volver a exportar desde el historial inventaría datos; la pantalla lo explica en lugar de proponerlo en silencio.
- Renderizado de JavaScript en el cliente (la página se obtiene tal como se sirve, no se ejecuta en un navegador headless).
- Panel web.

## 2. Instalación

### Requisitos previos

- Python 3.10+
- Conexión a Internet, para las dependencias
- Para la TUI: una fuente [Nerd Font](https://www.nerdfonts.com/) instalada en el terminal, para el icono de la cabecera — sin ella, ese carácter se muestra como un cuadrado vacío (la misma limitación que un emoji, pero mucho más disponible entre los usuarios de terminal). Su ausencia no afecta al funcionamiento, es puramente estética.

### Instalación

```bash
[ -d omega-fuzz ] && echo "ℹ️ Ya extraído aquí, paso omitido." || tar -xzf omega-fuzz.tar.gz
cd omega-fuzz/
chmod +x install.sh
./install.sh
```

`install.sh`:

1. Crea el entorno virtual `.venv` si todavía no existe.
2. Instala las dependencias (`vendor/omega-lib/` y luego `pip install -e .`, `pyproject.toml` sigue siendo la única fuente de verdad).
3. Hace ejecutables `omega-fuzz.sh` e `install.sh`.
4. Añade el alias `fuzz` a `~/.bashrc` y `~/.zshrc` (sin duplicado si ya está presente).

### Dependencias

Declaradas en `pyproject.toml` (sin `requirements.txt`):
- `omega-lib`: biblioteca compartida de la suite (temas de exportación, detección de terminal, `ConfidenceLevel`) — incluida en `vendor/omega-lib/`
- `httpx`: peticiones HTTP asíncronas (descubrimiento + fuzzing), lectura de la respuesta en streaming (nunca un búfer completo en memoria, ni siquiera con un archivo de varios GB servido por el objetivo)
- `beautifulsoup4` + `lxml`: extracción de las URL y formularios HTML
- `jinja2`: plantillas para la exportación HTML
- `textual`: interfaz TUI, temas, adaptación automática al terminal
- `pyyaml`: carga del archivo `--auth-config`
- Dependencias de desarrollo (`pip install -e ".[dev]"`): `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-httpserver`, `ruff`, `mypy`, `import-linter`

## 3. Uso

### Modo interactivo (TUI)

Recomendado para el uso diario — se lanza sin argumentos:

```bash
./omega-fuzz.sh
```
si has creado el alias, escribe simplemente `fuzz` en el terminal:
```bash
fuzz
```

Recorrido: pantalla de inicio (se cierra con una tecla o un clic) → menú principal (Escanear / Objetivos / Ajustes / Historial / Ayuda) → introducción del objetivo (URL completa, esquema `http://`/`https://` obligatorio), preset o configuración manual (alcance + agresividad), autenticación opcional, verificación TLS, ajustes de límites → pantalla de revisión (confirmación simple, o frase estricta `OUI-J-AI-L-AUTORISATION` para los casos sensibles) → escaneo (indicador indeterminado, botón **Detener** en cualquier momento) → resultados (findings, exportación) → historial (detalle de un escaneo pasado, findings asociados) y objetivos favoritos desde el menú principal. La adaptación al terminal (colores, tamaño, degradación estructural) es automática.

#### Atajos de teclado

| Tecla | Acción |
|---|---|
| `↑` / `↓` | Navegar entre los elementos de una pantalla |
| `Tab` / `Mayús+Tab` | Navegar entre los campos de un formulario |
| `Esc` | Volver a la pantalla anterior (confirmación de salida en la pantalla de inicio) |
| `t` | Tema siguiente (aplicado de inmediato, sin confirmación) |
| `r` | Refrescar la detección del terminal |
| `a` | Mostrar la ayuda (tabla de presets incluida) |
| `q` | Salir (con confirmación) |
| `Ctrl+P` | Paleta de comandos (Theme, Salir, Captura de pantalla) |

### Idiomas de la interfaz

La interfaz está disponible en 17 idiomas: francés, inglés, español, portugués (Brasil), italiano, alemán, neerlandés, polaco, ruso, chino simplificado, vietnamita, tailandés, indonesio, japonés, coreano, hindi y árabe. La elección se hace en Ajustes («Langue / Language») y se aplica tras reiniciar la interfaz; la variable `OMEGA_FUZZ_LANG` (por ejemplo `OMEGA_FUZZ_LANG=en ./omega-fuzz.sh`) fuerza un idioma durante una sesión. Lanzado desde omega-suite, omega-fuzz toma el idioma de la suite. En una consola de texto Linux (TTY), los idiomas con escritura no latina se muestran en inglés durante la sesión. La línea de comandos sigue en francés.

### Modo scriptable (CLI)

```bash
# Escaneo con un preset listo para usar
./omega-fuzz.sh scan --target https://example.com --preset prod-safe

# Combinación manual alcance + agresividad (sin preset)
./omega-fuzz.sh scan --target https://example.com --scope-profile standard --aggressiveness standard

# Con autenticación (archivo YAML, nunca credenciales en claro en la línea de comandos)
./omega-fuzz.sh scan --target https://example.com --preset staging-full --auth-config auth.yaml

# Dry-run: configuración efectiva y plan estimado, no se envía ninguna petición
./omega-fuzz.sh scan --target https://example.com --preset prod-safe --dry-run

# Exportación dirigida (carpeta, formatos, tema HTML)
./omega-fuzz.sh scan --target https://example.com --preset prod-safe \
    --output-dir ./rapports --format html --export-theme omega-neon
```

Opciones de `scan`:

| Opción | Por defecto | Efecto |
|---|---|---|
| `--target` | *(obligatorio)* | URL objetivo, esquema `http://`/`https://` obligatorio (nunca se completa automáticamente) |
| `--preset` | — | Preset listo para usar (ver [§4](#4-perfiles-de-alcance-y-presets)) |
| `--scope-profile` | — | Perfil de alcance, a combinar con `--aggressiveness`, sin `--preset` |
| `--aggressiveness` | — | Nivel de agresividad, a combinar con `--scope-profile`, sin `--preset` |
| `--auth-config` | — | Archivo YAML de autenticación |
| `--insecure-tls` | desactivado | Desactiva la verificación TLS (activa la confirmación reforzada) |
| `--max-duration` | *(del perfil)* | Sustituye la duración máxima (segundos) |
| `--max-requests` | *(del perfil)* | Sustituye el número máximo de peticiones |
| `--max-tests` | *(del perfil)* | Sustituye el número máximo de pruebas |
| `--max-concurrent` | *(del perfil)* | Sustituye la concurrencia máxima |
| `--dry-run` | desactivado | Muestra la configuración efectiva y el plan estimado, no envía ninguna petición |
| `--output-dir` | `var/exports/` | Carpeta de los informes exportados, llamados `<preset>-<marca_temporal>.<ext>` (modificable en Ajustes) |
| `--format` | `all` | `json`, `markdown`, `html` o `all` |
| `--export-theme` | `omega-base` | Tema del informe HTML exportado (sin efecto en json/markdown) |

No existe ningún subcomando `history`/`show` en la CLI: el historial y los objetivos favoritos solo se pueden consultar desde la TUI.

Si `install.sh` creó el alias, `fuzz scan ...` funciona desde cualquier lugar del terminal, sin el prefijo `./omega-fuzz.sh`.

## 4. Perfiles de alcance y presets

### Perfiles de alcance

| Perfil | Modo | Profundidad máx. | Restricciones |
|---|---|---|---|
| `strict` | objetivo exacto | 1 | Bloquea `/health`, `/ready`, `/metrics`, `/favicon.ico`, `/robots.txt` |
| `standard` | + subdominios | 2 | Bloquea subdominios estáticos habituales, rutas técnicas, recursos (imágenes/css/js/fuentes) |
| `large` | + subdominios | 4 | Bloquea solo las rutas técnicas y los recursos (incluidos archivos comprimidos/PDF) |
| `api` | objetivo exacto | 3 | Restringido a `/api`, `/v1`, `/v2`; bloquea documentación y recursos |
| `custom` | + subdominios | 3 | Ninguna restricción por defecto — base de partida para una configuración manual |

Sea cual sea el perfil elegido, una lista de extensiones binarias o voluminosas (`.iso`, `.zip`, `.exe`, `.mp4`...) queda **siempre** excluida del rastreo y del fuzzing, incluso con `custom` — un enlace a un archivo de este tipo nunca se descarga con una petición HTTP real, para evitar que una carpeta de descargas ralentice un escaneo durante largos minutos.

### Niveles de agresividad

`doux` · `standard` · `agressif` · `violent` — cada uno tiene sus propios límites base (duración, peticiones, pruebas, profundidad, concurrencia), sustituidos por un preset cuando lo hay.

### Presets listos para usar

| Preset | Alcance | Agresividad | Duración máx. | Peticiones máx. | Pruebas máx. | Profundidad máx. | Confirmación reforzada |
|---|---|---|---|---|---|---|---|
| `prod-safe` | strict | doux | 300 s | 1 000 | 500 | 1 | no |
| `staging-full` | standard | standard | 1 800 s | 20 000 | 10 000 | 2 | no |
| `lab-deep` | large | agressif | 3 600 s | 100 000 | 50 000 | 4 | no |
| `lab-extreme` | large | violent | 7 200 s | 500 000 | 250 000 | 5 | **sí** |
| `api-hardened` | api | agressif | 1 800 s | 50 000 | 25 000 | 3 | no |

Un escaneo queda bloqueado mientras no se confirme. Se exige una confirmación **reforzada** (escribir la frase exacta `OUI-J-AI-L-AUTORISATION`) en cuanto está presente uno de estos tres factores: agresividad `violent`, preset `lab-extreme` o verificación TLS desactivada (`--insecure-tls`) — para una combinación inusual sin ninguno de estos tres factores, confirmación simple sí/no.

## 5. Pruebas de seguridad ejecutadas

Pipeline automático, en cada URL descubierta dentro del alcance (y en cada formulario `GET` que se encuentre en ella):

| Prueba | Activación | Qué se comprueba |
|---|---|---|
| Fuzzing genérico de parámetro | cualquier parámetro de query string | Comportamiento del objetivo ante valores límite/malformados |
| Fuzzing de cabeceras | una vez por URL, 4 cabeceras fijas (`User-Agent`, `Referer`, `X-Forwarded-For`, `Accept-Language`) | Comportamiento del objetivo ante valores límite/malformados en una cabecera |
| Fuzzing de formulario (solo `GET`) | cualquier campo de formulario `GET` descubierto dentro del alcance | Comportamiento del objetivo ante valores límite/malformados en un campo de formulario |
| XSS reflejado | cualquier parámetro de query string | Reflejo no filtrado de un payload en la respuesta (no destructivo) |
| Inyección genérica | cualquier parámetro de query string | Detección de un error del servidor en respuesta a un payload de inyección (sin huella SQL/NoSQL específica) |
| Cabeceras de seguridad | una vez por URL | Cabeceras de seguridad ausentes o mal configuradas en la respuesta |

Las tres primeras pruebas (fuzzing genérico de parámetro/cabeceras/formulario) son un motor de mutación **sin detección** — nunca producen un `Finding` directamente; solo se contabilizan en el `Test` correspondiente los errores de servidor (5xx) encontrados. Solo las firmas (XSS, inyección, cabeceras de seguridad) generan findings.

## 6. Puntuación y severidad

Cada anomalía detectada se puntúa en 3 ejes (`impacto`, `explotabilidad`, `alcance`, de 1 a 5 cada uno) según la naturaleza de la observación — correspondencia deliberadamente **conservadora** (parte baja del intervalo, sin confirmación humana en esta etapa automática):

| Puntuación bruta (suma de los 3 ejes) | Severidad |
|---|---|
| ≥ 13 | `critical` |
| ≥ 10 | `high` |
| ≥ 7 | `medium` |
| < 7 | `low` |

Un ajuste manual (`severity_override`) sigue siendo posible, pero siempre exige una justificación explícita. Los findings equivalentes (mismo tipo, mismo endpoint, mismo parámetro) se deduplican, conservando la mejor prueba disponible (nivel de confianza `omega_lib.core.confidence.ConfidenceLevel` y, en caso de empate, la puntuación bruta).

## 7. Autenticación

Archivo YAML dedicado (`--auth-config`), nunca credenciales en claro en la línea de comandos:

| Modo | Efecto |
|---|---|
| `none` | Sin autenticación (por defecto) |
| `cookie` | Cookie de sesión proporcionada directamente |
| `bearer_token` | Token `Authorization: Bearer ...` |
| `login_form` | Autenticación por formulario (URL de inicio de sesión, campos usuario/contraseña) |

## 8. Arquitectura

Omega-Fuzz está estructurado en **Clean Architecture** (domain / application / infrastructure / interfaces / ports / core / app / plugins), alineado con la plantilla de la suite `omega-` (ver `omega-check`/`omega-deep`/`omega-fold`) y verificado por `import-linter` en cada modificación. El detalle completo está en **`docs/ARCHITECTURE.md`**.

Vista general muy breve:

```text
src/omega_fuzz/
├── domain/          Lógica de negocio pura (objetivos/alcance, peticiones, pruebas, findings, perfiles, informes...)
├── application/     Casos de uso (commands/queries) y orquestadores (descubrimiento, escaneo, informe, límites)
├── ports/           Contratos esperados por la aplicación (http_client, repositories, exporters...)
├── infrastructure/  Implementaciones concretas (httpx, BeautifulSoup, SQLite, exportadores Jinja2 — Textual NO está aquí)
├── interfaces/      tui/ (Textual) y cli/ (scriptable), con paridad funcional estricta
├── plugins/         Fuzzers y firmas (funciones puras, nunca acceso directo a la red)
├── app/             Ensamblaje (Container, composition root, ciclo de vida)
└── core/            Vocabulario transversal, errores, constantes
```

Reglas de diseño:
- `plugins/fuzzers/` y `plugins/signatures/`: funciones puras que construyen planes de prueba (`Test` + `ScanRequest`), nunca tocan `HttpClient`.
- `infrastructure/network/`: se encarga de la red (`httpx`, streaming acotado en memoria), nunca juzga.
- `infrastructure/analyzers/`: lee una respuesta ya recibida, produce `Observation` estructuradas, nunca recalcula una puntuación.
- `interfaces/`: muestra, no contiene ninguna lógica de negocio.

## 9. Exportaciones

Los informes Markdown y HTML se escriben en el idioma elegido en Ajustes («Idioma de las exportaciones», por defecto el de la interfaz); el JSON sigue siendo un dato y no se traduce. Los informes se generan por defecto en `var/exports/` (ruta de ejecución anclada en la carpeta del proyecto, `$OMEGA_FUZZ_VAR_DIR` para sustituirla, también modificable en la pantalla Ajustes), o en la ruta indicada (`--output-dir`). Nombre de archivo plano, sin subcarpeta: `<preset>-<marca_temporal>.<ext>` (p. ej. `prod-safe-2026-09-01_14-30-22.html`).

### JSON, fuente de verdad

Estructura completa del informe (configuración efectiva, estadísticas, pruebas, findings), estrictamente serializable en JSON.

### Markdown, informe humano compacto

Legible fuera del terminal, sin códigos ANSI.

### HTML, informe web autónomo

5 temas a elegir (`--export-theme` en la CLI, selector en la TUI): `omega-base`, `omega-burn`, `omega-neon`, `light-basic`, `light-alt`.

## 10. Historial y objetivos favoritos

Cada escaneo se guarda (SQLite, `var/db/omega-fuzz.db`) con sus findings y se puede consultar desde la pantalla Historial de la TUI. Solo se almacenan `Scan` y `Finding` — ni la configuración efectiva ni las peticiones detalladas — así que no hay repetición, comparación ni nueva exportación desde esta pantalla (la pantalla lo explica en lugar de inventar datos).

La pantalla **Objetivos** conserva una lista de favoritos (URL normalizadas, `var/targets.json`), reutilizable para rellenar directamente el campo Objetivo de un nuevo escaneo.

## 11. Capturas de pantalla

Comando **Captura de pantalla** de la paleta (`Ctrl+P`): guarda un SVG de la pantalla TUI actual en `var/screenshots/` por defecto, modificable en la pantalla Ajustes (como la carpeta de exportación). Purga dedicada disponible en Ajustes.

## 12. Compatibilidad con terminales

La TUI (Textual) detecta automáticamente las capacidades del terminal (emulador, tamaño) y adapta en consecuencia su hoja de estilo estructural (`complete`/`standard`/`reduced`/`mono`), sin opción manual. El modo CLI sigue siempre en texto simple, independiente del terminal. Política compartida por toda la suite `omega-` (`omega-lib`, `terminal/policies.py`).

### Perfil según el emulador detectado

| Emulador | Perfil inicial |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | `complete` |
| Konsole, GNOME Terminal, Terminator, Xfce4 Terminal | `standard` |
| xterm, urxvt, SSH moderno | `reduced` |
| TTY Linux, SSH antiguo | `mono` |
| Emulador no reconocido | `reduced` (repliegue por defecto) |

### Perfil según el tamaño del terminal

| Tamaño mínimo (columnas × líneas) | Límite de perfil |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| por debajo | `mono` |

El perfil final elegido es **el más restrictivo de los dos** (emulador y tamaño) — se puede refrescar en directo con la tecla `r`.

## 13. Pruebas

```bash
source .venv/bin/activate
lint-imports        # verifica la Dependency Rule (6 contratos)
pytest -q           # 344 pruebas
ruff check src tests
mypy -p omega_fuzz
```

Estructura: `tests/unit/` (dominio y aplicación, sin E/S real), `tests/integration/` (sistema de archivos real mediante `tmp_path`, servidor HTTP ficticio `pytest-httpserver`, base SQLite real, CLI de extremo a extremo), `tests/tui/` (navegación mediante `Pilot`, estructural — sin verificación visual autoproclamada).

## 14. Fuera de alcance

- Fuzzing de cuerpos JSON (código presente, no conectado — ningún descubrimiento de esquema de API)
- Fuzzing de formularios `POST`/`PUT`/`DELETE` (excluidos por decisión, riesgo de escritura)
- Pruebas de lógica de negocio (IDOR, autorización, flujo de trabajo) fuera de la invocación manual
- Escaneo multiobjetivo simultáneo
- Repetición, comparación o exportación desde el historial
- Renderizado de JavaScript en el cliente
- Panel web

---

> Omega-Fuzz — Descubrir un perímetro, probarlo con salvaguardas explícitas, nunca adivinar lo que no se ha confirmado.
