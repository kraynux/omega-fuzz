<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - Licença MIT (ver arquivo LICENSE) -->
<div align="center">
  <img src="../../assets/omega-fuzz.png" alt="Omega-Fuzz" width="384">
</div>

# 🗱 OMEGA-FUZZ

**Scanner de vulnerabilidades**

> Desenvolvido por **kraynux** para o **Omega-server** 
[https://kraynux.snake-mackarel.ts.net](https://kraynux.snake-mackarel.ts.net)

Página oficial: [OMEGA-FUZZ](https://kraynux.snake-mackarel.ts.net/omega-fuzz/) &nbsp; Prévia: [Capturas de tela](https://kraynux.snake-mackarel.ts.net/omega-fuzz/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

🌐 Interface e relatórios exportados disponíveis em **17 idiomas** — veja [Idiomas da interface](#idiomas-da-interface).  
**Idiomas:**  
<img src="https://flagcdn.com/w20/fr.png" alt="Français" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)

**Omega-Fuzz** é um aplicativo local de terminal (TUI [Textual](https://github.com/Textualize/textual) + CLI scriptável) que conduz a descoberta e os testes de segurança web (fuzzing HTTP) para ambientes autorizados (laboratórios, espelhos pessoais, trabalhos de teste com consentimento explícito).

Ferramenta da suíte `omega-`, estruturada em Clean Architecture — veja `docs/ARCHITECTURE.md` para o detalhe técnico completo.

## 1. Visão e escopo

### O que o Omega-Fuzz faz

- Descobre o perímetro de um alvo único por meio de um BFS limitado por um escopo explícito (esquema/subdomínios/caminhos permitidos-bloqueados/profundidade), nunca sem salvaguardas.
- Fuzzing genérico dos parâmetros de query string, dos cabeçalhos HTTP e dos formulários `GET` encontrados em cada URL descoberta, e verifica três famílias de assinaturas: XSS refletido não destrutivo, injeção genérica (detecção de erro na resposta), cabeçalhos de segurança ausentes ou mal configurados — veja [§5](#5-testes-de-segurança-executados).
- Pontua cada anomalia em 3 eixos (impacto/explorabilidade/alcance) e deduz dela uma severidade (`low`/`medium`/`high`/`critical`), desduplicada por `(tipo, endpoint, parâmetro)` mantendo a melhor evidência — veja [§6](#6-pontuação-e-severidade).
- Suporta autenticação (cookie, bearer token, formulário de login) por meio de um arquivo YAML dedicado, nunca com credenciais em texto claro na linha de comando.
- Apresenta o resultado na TUI (Textual) ou na CLI scriptável, com três exportações (JSON, Markdown, HTML com 5 temas).
- Mantém um histórico persistente das varreduras e de seus findings (SQLite), e uma lista de alvos favoritos reutilizáveis.
- Exige uma confirmação explícita (frase estrita para os casos mais sensíveis) antes de qualquer varredura agressiva, estendida ou com a verificação TLS desativada.

### O que o Omega-Fuzz não faz

- Fuzzing de corpos JSON — o código existe (`plugins/fuzzers/json_body_fuzzer.py`), mas não está conectado (a descoberta HTML/BFS não produz nenhum esquema de API JSON nem nenhuma fonte de template aproveitável).
- Fuzzing de formulários `POST`/`PUT`/`DELETE` — excluídos do pipeline automático por escolha (risco de escrita indesejada no alvo); apenas os formulários `GET` são testados.
- Testes de lógica de negócio (IDOR, controle de autorização, quebra de fluxo de trabalho) — o código existe (`plugins/logic_tests/`), mas fica fora do pipeline automático, só pode ser invocado separadamente e nunca é acionado por uma varredura padrão.
- Varredura de vários alvos em paralelo — um único alvo por varredura.
- Repetição, comparação ou exportação a partir da tela Histórico — apenas `Scan` e `Finding` são persistidos (nem a configuração efetiva completa nem as requisições), então repetir ou exportar de novo a partir do histórico inventaria dados; a tela explica isso em vez de oferecê-lo em silêncio.
- Renderização de JavaScript no cliente (a página é obtida como servida, não executada em um navegador headless).
- Painel web.

## 2. Instalação

### Pré-requisitos

- Python 3.10+
- Conexão com a Internet, para as dependências
- Para a TUI: uma fonte [Nerd Font](https://www.nerdfonts.com/) instalada no terminal, para o ícone do cabeçalho — sem ela, esse caractere aparece como um quadrado vazio (mesma limitação de um emoji, mas muito mais disponível entre os usuários de terminal). A ausência não tem consequência no funcionamento, é puramente estética.

### Instalação

```bash
[ -d omega-fuzz ] && echo "ℹ️ Já extraído aqui, etapa ignorada." || tar -xzf omega-fuzz.tar.gz
cd omega-fuzz/
chmod +x install.sh
./install.sh
```

`install.sh`:

1. Cria o ambiente virtual `.venv` se ele ainda não existir.
2. Instala as dependências (`vendor/omega-lib/` e depois `pip install -e .`, `pyproject.toml` continua sendo a única fonte de verdade).
3. Torna `omega-fuzz.sh` e `install.sh` executáveis.
4. Adiciona o alias `fuzz` a `~/.bashrc` e `~/.zshrc` (sem duplicata se já existir).

### Dependências

Declaradas em `pyproject.toml` (sem `requirements.txt`):
- `omega-lib`: biblioteca compartilhada da suíte (temas de exportação, detecção de terminal, `ConfidenceLevel`) — incluída em `vendor/omega-lib/`
- `httpx`: requisições HTTP assíncronas (descoberta + fuzzing), leitura da resposta em streaming (nunca um buffer completo na memória, mesmo com um arquivo de vários GB servido pelo alvo)
- `beautifulsoup4` + `lxml`: extração das URLs e formulários HTML
- `jinja2`: templates para a exportação HTML
- `textual`: interface TUI, temas, adaptação automática ao terminal
- `pyyaml`: carregamento do arquivo `--auth-config`
- Dependências de desenvolvimento (`pip install -e ".[dev]"`): `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-httpserver`, `ruff`, `mypy`, `import-linter`

## 3. Uso

### Modo interativo (TUI)

Recomendado para o uso diário — iniciado sem argumentos:

```bash
./omega-fuzz.sh
```
se você criou o alias, basta digitar `fuzz` no terminal:
```bash
fuzz
```

Percurso: tela de abertura (fecha com uma tecla ou um clique) → menu principal (Escanear / Alvos / Configurações / Histórico / Ajuda) → entrada do alvo (URL completa, esquema `http://`/`https://` obrigatório), preset ou configuração manual (escopo + agressividade), autenticação opcional, verificação TLS, ajustes de limites → tela de revisão (confirmação simples, ou frase estrita `OUI-J-AI-L-AUTORISATION` para os casos sensíveis) → varredura (indicador indeterminado, botão **Parar** a qualquer momento) → resultados (findings, exportação) → histórico (detalhe de uma varredura passada, findings associados) e alvos favoritos a partir do menu principal. A adaptação ao terminal (cores, tamanho, degradação estrutural) é automática.

#### Atalhos de teclado

| Tecla | Ação |
|---|---|
| `↑` / `↓` | Navegar entre os elementos de uma tela |
| `Tab` / `Shift+Tab` | Navegar entre os campos de um formulário |
| `Esc` | Voltar à tela anterior (confirmação de saída na tela inicial) |
| `t` | Próximo tema (aplicado imediatamente, sem confirmação) |
| `r` | Atualizar a detecção do terminal |
| `a` | Mostrar a ajuda (tabela de presets incluída) |
| `q` | Sair (com confirmação) |
| `Ctrl+P` | Paleta de comandos (Theme, Sair, Captura de tela) |

### Idiomas da interface

A interface está disponível em 17 idiomas: francês, inglês, espanhol, português (Brasil), italiano, alemão, neerlandês, polonês, russo, chinês simplificado, vietnamita, tailandês, indonésio, japonês, coreano, hindi e árabe. A escolha é feita nas Configurações («Langue / Language») e vale depois que a interface é reiniciada; a variável `OMEGA_FUZZ_LANG` (por exemplo `OMEGA_FUZZ_LANG=en ./omega-fuzz.sh`) força um idioma durante uma sessão. Iniciado a partir do omega-suite, o omega-fuzz adota o idioma da suíte. Em um console de texto Linux (TTY), os idiomas com escrita não latina são exibidos em inglês durante a sessão. A linha de comando continua em francês.

### Modo scriptável (CLI)

```bash
# Varredura com um preset pronto para uso
./omega-fuzz.sh scan --target https://example.com --preset prod-safe

# Combinação manual escopo + agressividade (sem preset)
./omega-fuzz.sh scan --target https://example.com --scope-profile standard --aggressiveness standard

# Com autenticação (arquivo YAML, nunca credenciais em texto claro na linha de comando)
./omega-fuzz.sh scan --target https://example.com --preset staging-full --auth-config auth.yaml

# Dry-run: configuração efetiva e plano estimado, nenhuma requisição enviada
./omega-fuzz.sh scan --target https://example.com --preset prod-safe --dry-run

# Exportação direcionada (pasta, formatos, tema HTML)
./omega-fuzz.sh scan --target https://example.com --preset prod-safe \
    --output-dir ./rapports --format html --export-theme omega-neon
```

Opções de `scan`:

| Opção | Padrão | Efeito |
|---|---|---|
| `--target` | *(obrigatório)* | URL alvo, esquema `http://`/`https://` obrigatório (nunca completado automaticamente) |
| `--preset` | — | Preset pronto para uso (veja [§4](#4-perfis-de-escopo-e-presets)) |
| `--scope-profile` | — | Perfil de escopo, a combinar com `--aggressiveness`, sem `--preset` |
| `--aggressiveness` | — | Nível de agressividade, a combinar com `--scope-profile`, sem `--preset` |
| `--auth-config` | — | Arquivo YAML de autenticação |
| `--insecure-tls` | desativado | Desativa a verificação TLS (aciona a confirmação reforçada) |
| `--max-duration` | *(do perfil)* | Substitui a duração máxima (segundos) |
| `--max-requests` | *(do perfil)* | Substitui o número máximo de requisições |
| `--max-tests` | *(do perfil)* | Substitui o número máximo de testes |
| `--max-concurrent` | *(do perfil)* | Substitui a concorrência máxima |
| `--dry-run` | desativado | Mostra a configuração efetiva e o plano estimado, não envia nenhuma requisição |
| `--output-dir` | `var/exports/` | Pasta dos relatórios exportados, chamados `<preset>-<carimbo_de_data>.<ext>` (pode ser alterada nas Configurações) |
| `--format` | `all` | `json`, `markdown`, `html` ou `all` |
| `--export-theme` | `omega-base` | Tema do relatório HTML exportado (sem efeito em json/markdown) |

Não existe subcomando `history`/`show` na CLI: o histórico e os alvos favoritos só podem ser consultados pela TUI.

Se o alias foi criado pelo `install.sh`, `fuzz scan ...` funciona de qualquer lugar do terminal, sem o prefixo `./omega-fuzz.sh`.

## 4. Perfis de escopo e presets

### Perfis de escopo

| Perfil | Modo | Profundidade máx. | Restrições |
|---|---|---|---|
| `strict` | alvo exato | 1 | Bloqueia `/health`, `/ready`, `/metrics`, `/favicon.ico`, `/robots.txt` |
| `standard` | + subdomínios | 2 | Bloqueia subdomínios estáticos comuns, caminhos técnicos, recursos (imagens/css/js/fontes) |
| `large` | + subdomínios | 4 | Bloqueia apenas os caminhos técnicos e os recursos (incluindo arquivos compactados/PDF) |
| `api` | alvo exato | 3 | Restrito a `/api`, `/v1`, `/v2`; bloqueia documentação e recursos |
| `custom` | + subdomínios | 3 | Nenhuma restrição por padrão — ponto de partida para uma configuração manual |

Qualquer que seja o perfil escolhido, uma lista de extensões binárias ou volumosas (`.iso`, `.zip`, `.exe`, `.mp4`...) é **sempre** excluída do rastreamento e do fuzzing, mesmo em `custom` — um link para um arquivo desse tipo nunca é baixado por uma requisição HTTP real, para evitar que uma pasta de downloads deixe uma varredura lenta por longos minutos.

### Níveis de agressividade

`doux` · `standard` · `agressif` · `violent` — cada um tem seus próprios limites básicos (duração, requisições, testes, profundidade, concorrência), substituídos por um preset quando houver.

### Presets prontos para uso

| Preset | Escopo | Agressividade | Duração máx. | Requisições máx. | Testes máx. | Profundidade máx. | Confirmação reforçada |
|---|---|---|---|---|---|---|---|
| `prod-safe` | strict | doux | 300 s | 1.000 | 500 | 1 | não |
| `staging-full` | standard | standard | 1.800 s | 20.000 | 10.000 | 2 | não |
| `lab-deep` | large | agressif | 3.600 s | 100.000 | 50.000 | 4 | não |
| `lab-extreme` | large | violent | 7.200 s | 500.000 | 250.000 | 5 | **sim** |
| `api-hardened` | api | agressif | 1.800 s | 50.000 | 25.000 | 3 | não |

Uma varredura fica bloqueada enquanto não for confirmada. Uma confirmação **reforçada** (digitar a frase exata `OUI-J-AI-L-AUTORISATION`) é exigida assim que um destes três fatores estiver presente: agressividade `violent`, preset `lab-extreme` ou verificação TLS desativada (`--insecure-tls`) — para uma combinação incomum sem nenhum desses três fatores, confirmação simples sim/não.

## 5. Testes de segurança executados

Pipeline automático, em cada URL descoberta dentro do escopo (e em cada formulário `GET` encontrado nela):

| Teste | Acionamento | O que é verificado |
|---|---|---|
| Fuzzing genérico de parâmetro | qualquer parâmetro de query string | Comportamento do alvo diante de valores limite/malformados |
| Fuzzing de cabeçalhos | uma vez por URL, 4 cabeçalhos fixos (`User-Agent`, `Referer`, `X-Forwarded-For`, `Accept-Language`) | Comportamento do alvo diante de valores limite/malformados em um cabeçalho |
| Fuzzing de formulário (apenas `GET`) | qualquer campo de formulário `GET` descoberto dentro do escopo | Comportamento do alvo diante de valores limite/malformados em um campo de formulário |
| XSS refletido | qualquer parâmetro de query string | Reflexão não filtrada de um payload na resposta (não destrutivo) |
| Injeção genérica | qualquer parâmetro de query string | Detecção de erro do servidor em resposta a um payload de injeção (sem impressão digital SQL/NoSQL específica) |
| Cabeçalhos de segurança | uma vez por URL | Cabeçalhos de segurança ausentes ou mal configurados na resposta |

Os três primeiros testes (fuzzing genérico de parâmetro/cabeçalhos/formulário) são um motor de mutação **sem detecção** — nunca produzem um `Finding` diretamente; apenas os erros de servidor (5xx) encontrados são contabilizados no `Test` correspondente. Apenas as assinaturas (XSS, injeção, cabeçalhos de segurança) geram findings.

## 6. Pontuação e severidade

Cada anomalia detectada é avaliada em 3 eixos (`impacto`, `explorabilidade`, `alcance`, de 1 a 5 cada) conforme a natureza da observação — mapeamento deliberadamente **conservador** (parte baixa da faixa, sem confirmação humana nesta etapa automática):

| Pontuação bruta (soma dos 3 eixos) | Severidade |
|---|---|
| ≥ 13 | `critical` |
| ≥ 10 | `high` |
| ≥ 7 | `medium` |
| < 7 | `low` |

Um ajuste manual (`severity_override`) continua possível, mas sempre exige uma justificativa explícita. Os findings equivalentes (mesmo tipo, mesmo endpoint, mesmo parâmetro) são desduplicados, mantendo a melhor evidência disponível (nível de confiança `omega_lib.core.confidence.ConfidenceLevel` e, em caso de empate, a pontuação bruta).

## 7. Autenticação

Arquivo YAML dedicado (`--auth-config`), nunca credenciais em texto claro na linha de comando:

| Modo | Efeito |
|---|---|
| `none` | Nenhuma autenticação (padrão) |
| `cookie` | Cookie de sessão fornecido diretamente |
| `bearer_token` | Token `Authorization: Bearer ...` |
| `login_form` | Autenticação por formulário (URL de login, campos usuário/senha) |

## 8. Arquitetura

O Omega-Fuzz é estruturado em **Clean Architecture** (domain / application / infrastructure / interfaces / ports / core / app / plugins), alinhado com o modelo da suíte `omega-` (veja `omega-check`/`omega-deep`/`omega-fold`) e verificado pelo `import-linter` a cada modificação. O detalhe completo está em **`docs/ARCHITECTURE.md`**.

Visão geral bem curta:

```text
src/omega_fuzz/
├── domain/          Lógica de negócio pura (alvos/escopo, requisições, testes, findings, perfis, relatórios...)
├── application/     Casos de uso (commands/queries) e orquestradores (descoberta, varredura, relatório, limites)
├── ports/           Contratos esperados pela aplicação (http_client, repositories, exporters...)
├── infrastructure/  Implementações concretas (httpx, BeautifulSoup, SQLite, exportadores Jinja2 — o Textual NÃO fica aqui)
├── interfaces/      tui/ (Textual) e cli/ (scriptável), com paridade funcional estrita
├── plugins/         Fuzzers e assinaturas (funções puras, nunca acesso direto à rede)
├── app/             Montagem (Container, composition root, ciclo de vida)
└── core/            Vocabulário transversal, erros, constantes
```

Regras de design:
- `plugins/fuzzers/` e `plugins/signatures/`: funções puras que constroem planos de teste (`Test` + `ScanRequest`), nunca tocam no `HttpClient`.
- `infrastructure/network/`: cuida da rede (`httpx`, streaming limitado na memória), nunca julga.
- `infrastructure/analyzers/`: lê uma resposta já recebida, produz `Observation` estruturadas, nunca recalcula uma pontuação.
- `interfaces/`: exibe, não contém nenhuma lógica de negócio.

## 9. Exportações

Os relatórios Markdown e HTML são escritos no idioma escolhido nas Configurações («Idioma das exportações», por padrão o da interface); o JSON continua sendo um dado, não traduzido. Os relatórios são gerados em `var/exports/` por padrão (caminho de execução ancorado na pasta do projeto, `$OMEGA_FUZZ_VAR_DIR` para substituí-lo, também alterável na tela Configurações), ou no caminho indicado (`--output-dir`). Nome de arquivo plano, sem subpasta: `<preset>-<carimbo_de_data>.<ext>` (ex. `prod-safe-2026-09-01_14-30-22.html`).

### JSON, fonte de verdade

Estrutura completa do relatório (configuração efetiva, estatísticas, testes, findings), estritamente serializável em JSON.

### Markdown, relatório humano compacto

Legível fora do terminal, sem códigos ANSI.

### HTML, relatório web autônomo

5 temas à escolha (`--export-theme` na CLI, seletor na TUI): `omega-base`, `omega-burn`, `omega-neon`, `light-basic`, `light-alt`.

## 10. Histórico e alvos favoritos

Cada varredura é persistida (SQLite, `var/db/omega-fuzz.db`) com seus findings e pode ser consultada na tela Histórico da TUI. Apenas `Scan` e `Finding` são armazenados — nem a configuração efetiva nem as requisições detalhadas — portanto não há repetição, comparação nem nova exportação a partir dessa tela (a tela explica isso em vez de inventar dados).

A tela **Alvos** mantém uma lista de favoritos (URLs normalizadas, `var/targets.json`), reutilizável para preencher diretamente o campo Alvo de uma nova varredura.

## 11. Capturas de tela

Comando **Captura de tela** da paleta (`Ctrl+P`): salva um SVG da tela TUI atual em `var/screenshots/` por padrão, alterável na tela Configurações (como a pasta de exportação). Limpeza dedicada disponível nas Configurações.

## 12. Compatibilidade com terminais

A TUI (Textual) detecta automaticamente as capacidades do terminal (emulador, tamanho) e adapta sua folha de estilo estrutural de acordo (`complete`/`standard`/`reduced`/`mono`), sem opção manual. O modo CLI continua sempre em texto simples, independente do terminal. Política compartilhada por toda a suíte `omega-` (`omega-lib`, `terminal/policies.py`).

### Perfil conforme o emulador detectado

| Emulador | Perfil inicial |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | `complete` |
| Konsole, GNOME Terminal, Terminator, Xfce4 Terminal | `standard` |
| xterm, urxvt, SSH moderno | `reduced` |
| TTY Linux, SSH legado | `mono` |
| Emulador não reconhecido | `reduced` (alternativa padrão) |

### Perfil conforme o tamanho do terminal

| Tamanho mínimo (colunas × linhas) | Teto de perfil |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| abaixo | `mono` |

O perfil final adotado é **o mais restritivo dos dois** (emulador e tamanho) — pode ser atualizado ao vivo com a tecla `r`.

## 13. Testes

```bash
source .venv/bin/activate
lint-imports        # verifica a Dependency Rule (6 contratos)
pytest -q           # 344 testes
ruff check src tests
mypy -p omega_fuzz
```

Estrutura: `tests/unit/` (domínio e aplicação, sem E/S real), `tests/integration/` (sistema de arquivos real via `tmp_path`, servidor HTTP falso `pytest-httpserver`, banco SQLite real, CLI de ponta a ponta), `tests/tui/` (navegação via `Pilot`, estrutural — sem verificação visual autodeclarada).

## 14. Fora do escopo

- Fuzzing de corpos JSON (código presente, não conectado — nenhuma descoberta de esquema de API)
- Fuzzing de formulários `POST`/`PUT`/`DELETE` (excluídos por escolha, risco de escrita)
- Testes de lógica de negócio (IDOR, autorização, fluxo de trabalho) fora da invocação manual
- Varredura simultânea de vários alvos
- Repetição, comparação ou exportação a partir do histórico
- Renderização de JavaScript no cliente
- Painel web

---

> Omega-Fuzz — Descobrir um perímetro, testá-lo com salvaguardas explícitas, nunca adivinhar o que não foi confirmado.
