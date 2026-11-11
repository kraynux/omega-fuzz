<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - MIT 라이선스(LICENSE 파일 참조) -->
<div align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/assets/omega-fuzz.png" alt="Omega-Fuzz" width="512">
</div>

# 🗱 OMEGA-FUZZ

**취약점 스캐너**

> [kraynux](https://github.com/kraynux)가 [Omega-Server](https://kraynux.snake-mackarel.ts.net)를 위해 개발   

공식 페이지: [OMEGA-FUZZ](https://kraynux.snake-mackarel.ts.net/omega-fuzz/) &nbsp; 스크린샷: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-fuzz/screenshots/)  

[![라이선스: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![플랫폼](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![인터페이스](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

🌐 인터페이스와 내보낸 보고서는 **17개 언어**로 제공됩니다 — [인터페이스 언어](#인터페이스-언어)를 참조하세요.  
**언어:**  
<img src="https://flagcdn.com/w20/fr.png" alt="Français" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)

**Omega-Fuzz**는 허가된 환경(랩, 개인 미러, 명시적으로 동의된 테스트)에서 웹 보안 발견 및 테스트(HTTP 퍼징)를 수행하는 로컬 터미널 애플리케이션입니다([Textual](https://github.com/Textualize/textual) 기반 TUI + 스크립트 가능한 CLI).

이 도구는 `omega-` 제품군의 일부이며 Clean Architecture로 구성되어 있습니다. 전체 기술 세부 사항은 `docs/ARCHITECTURE.md`를 참조하세요.

## 1. 비전과 범위

### Omega-Fuzz가 하는 일

- 명시적인 스코프(스킴, 서브도메인, 허용/차단 경로, 깊이)로 제한된 BFS를 통해 단일 대상의 범위를 발견합니다. 안전장치 없이 실행되지 않습니다.
- 발견된 각 URL에서 찾은 쿼리 문자열 매개변수, HTTP 헤더, `GET` 폼에 대해 일반 퍼징을 수행하고, 세 가지 서명군을 검사합니다: 비파괴적 반사형 XSS, 일반 인젝션(응답 오류 탐지), 누락되었거나 잘못 구성된 보안 헤더 — [§5](#5-수행되는-보안-테스트) 참조.
- 각 이상 현상을 3개 축(영향, 악용 가능성, 범위)으로 채점하고 `low`/`medium`/`high`/`critical` 심각도를 도출합니다. `(유형, 엔드포인트, 매개변수)` 기준으로 중복을 제거하고 최상의 증거를 유지합니다 — [§6](#6-점수와-심각도) 참조.
- 전용 YAML 파일을 통한 인증(cookie, bearer token, 로그인 폼)을 지원합니다. 자격 증명이 명령줄에 평문으로 전달되지 않습니다.
- 결과를 TUI(Textual) 또는 스크립트 가능한 CLI로 표시하고, JSON, Markdown, HTML(5가지 테마)의 세 가지 내보내기를 제공합니다.
- SQLite에 스캔 기록과 findings를 영구 저장하며, 재사용 가능한 즐겨찾기 대상 목록도 유지합니다.
- 공격적인 스캔, 확장 스캔 또는 TLS 검증이 비활성화된 스캔 전에 명시적인 확인(가장 민감한 경우에는 정확한 문구)을 요구합니다.

### Omega-Fuzz가 하지 않는 일

- JSON 본문 퍼징 — 코드는 존재하지만(`plugins/fuzzers/json_body_fuzzer.py`) 연결되어 있지 않습니다(HTML/BFS 발견은 JSON API 스키마나 사용 가능한 템플릿 소스를 생성하지 않음).
- `POST`/`PUT`/`DELETE` 폼 퍼징 — 자동 파이프라인에서 의도적으로 제외됩니다(대상에 대한 의도치 않은 쓰기 위험). `GET` 폼만 테스트됩니다.
- 비즈니스 로직 테스트(IDOR, 권한 제어, 워크플로우 중단) — 코드는 존재하지만(`plugins/logic_tests/`) 자동 파이프라인 외부에 있으며, 별도 호출 시에만 사용할 수 있고 표준 스캔이 실행하지 않습니다.
- 다중 대상 병렬 스캔 — 스캔당 하나의 대상입니다.
- 기록 화면에서 재실행, 비교 또는 내보내기 — `Scan`과 `Finding`만 저장됩니다(전체 유효 구성이나 요청은 저장되지 않음). 기록에서 재실행하거나 다시 내보내면 데이터를 만들게 되므로, 화면은 이를 설명할 뿐 조용히 기능을 제공하지 않습니다.
- 클라이언트 측 JavaScript 렌더링 — 페이지는 서버가 제공한 그대로 가져오며, headless 브라우저에서 실행되지 않습니다.
- 웹 대시보드.

## 2. 설치

### 전제 조건

- Python 3.10 이상
- 의존성 설치를 위한 인터넷 연결
- TUI용: 헤더 아이콘을 표시하려면 터미널에 [Nerd Font](https://www.nerdfonts.com/)가 설치되어 있어야 합니다. 없으면 해당 문자가 빈 사각형으로 표시됩니다(이모지와 같은 제한이지만 터미널 사용자에게는 훨씬 널리 보급됨). 폰트가 없어도 기능에는 영향이 없으며 순수하게 외관상의 문제입니다.

### 설치

```bash
[ -d omega-fuzz ] && echo "ℹ️ 이미 여기에 압축 해제됨. 이 단계 건너뜀." || tar -xzf omega-fuzz.tar.gz
cd omega-fuzz/
chmod +x install.sh
./install.sh
```

`install.sh`의 작업:

1. `.venv` 가상환경이 없으면 생성합니다.
2. 의존성을 설치합니다(`vendor/omega-lib/`, 이후 `pip install -e .`; `pyproject.toml`이 유일한 단일 진실 공급원으로 유지됨).
3. `omega-fuzz.sh`와 `install.sh`를 실행 가능하게 만듭니다.
4. `~/.bashrc`와 `~/.zshrc`에 `fuzz` 별칭을 추가합니다(이미 있으면 중복 추가하지 않음).

### 의존성

`pyproject.toml`에 선언됩니다(`requirements.txt` 없음):

- `omega-lib`: 제품군 공용 라이브러리(내보내기 테마, 터미널 감지, `ConfidenceLevel`) — `vendor/omega-lib/`에 포함
- `httpx`: 비동기 HTTP 요청(발견 + 퍼징), 응답 스트리밍(대상이 제공하는 수 GB 파일이라도 전체 응답을 메모리에 버퍼링하지 않음)
- `beautifulsoup4` + `lxml`: URL 및 HTML 폼 추출
- `jinja2`: HTML 내보내기 템플릿
- `textual`: TUI 인터페이스, 테마, 터미널 자동 적응
- `pyyaml`: `--auth-config` 파일 로드
- 개발 의존성(`pip install -e ".[dev]"`): `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-httpserver`, `ruff`, `mypy`, `import-linter`

## 3. 사용법

### 대화형 모드(TUI)

일상 사용에 권장됩니다 — 인수 없이 실행합니다:

```bash
./omega-fuzz.sh
```

별칭을 만들었다면 터미널에서 `fuzz`만 입력하면 됩니다:

```bash
fuzz
```

흐름: 시작 화면(키 입력 또는 클릭으로 닫힘) → 기본 메뉴(스캔 / 대상 / 설정 / 기록 / 도움말) → 대상 입력(전체 URL, `http://`/`https://` 스킴 필수), 프리셋 또는 수동 구성(스코프 + 공격성), 선택적 인증, TLS 검증, 제한 재정의 → 검토 화면(간단한 확인, 민감한 경우 정확한 문구 `OUI-J-AI-L-AUTORISATION`) → 스캔(불확정 진행 표시, 언제든 **중지** 버튼 사용 가능) → 결과(findings, 내보내기) → 기록(이전 스캔 상세 및 관련 findings), 기본 메뉴의 즐겨찾기 대상. 터미널 적응(색상, 크기, 구조적 저하)은 자동입니다.

#### 키보드 단축키

| 키 | 동작 |
|---|---|
| `↑` / `↓` | 화면 요소 간 탐색 |
| `Tab` / `Shift+Tab` | 폼 필드 간 탐색 |
| `Esc` | 이전 화면으로 돌아가기(시작 화면에서는 종료 확인) |
| `t` | 다음 테마(확인 없이 즉시 적용) |
| `r` | 터미널 감지 새로 고침 |
| `a` | 도움말 표시(포함된 프리셋 표) |
| `q` | 종료(확인 포함) |
| `Ctrl+P` | 명령 팔레트(Theme, 종료, 스크린샷) |

### 인터페이스 언어

인터페이스는 17개 언어로 제공됩니다: 프랑스어, 영어, 스페인어, 포르투갈어(브라질), 이탈리아어, 독일어, 네덜란드어, 폴란드어, 러시아어, 간체 중국어, 베트남어, 태국어, 인도네시아어, 일본어, 한국어, 힌디어, 아랍어. 언어는 설정(「언어 / Language」)에서 선택하며 인터페이스 재시작 후 적용됩니다. 환경 변수 `OMEGA_FUZZ_LANG`(예: `OMEGA_FUZZ_LANG=en ./omega-fuzz.sh`)는 한 세션 동안 언어를 강제합니다. omega-suite에서 실행하면 omega-fuzz는 제품군의 언어를 사용합니다. Linux 텍스트 콘솔(TTY)에서는 비라틴 문자 언어가 세션 동안 영어로 표시됩니다. 명령줄은 프랑스어로 유지됩니다.

### 문의 및 지원

도움말(`a` 키)에는 **문의 및 지원** 화면이 있습니다: *커피 한 잔 사기*(개발자의 PayPal 페이지), *지원팀에 문의*(이메일 주소와 사이트의 문의 양식을 그대로 표시), *사용자로 등록(익명)*, *업데이트 확인*. 등록은 자발적이며 기본적으로 꺼져 있고 한 번만 전송됩니다. 사용자 수와, 원하면 사용자의 대륙 또는 국가(닫힌 목록, 자유 입력 없음)를 세는 데에만 쓰입니다. 무작위로 생성한 키, 소프트웨어 이름(`omega-fuzz`)과 버전만 보내며, 이름, 컴퓨터 이름, 설정, 대상, 결과는 절대 보내지 않습니다. IP 주소는 등록 정보에 저장되지 않지만, 모든 방문과 마찬가지로 수신 서버의 보안 검사와 로그를 거칩니다. 같은 화면에서 언제든지 철회할 수 있습니다(*등록 취소*). 업데이트 확인은 사이트에 게시된 버전 목록만 읽으며, 클릭하지 않으면 절대 실행되지 않습니다.

### 스크립트 모드(CLI)

```bash
# 준비된 프리셋으로 스캔
./omega-fuzz.sh scan --target https://example.com --preset prod-safe

# 스코프 + 공격성 수동 조합(프리셋 없음)
./omega-fuzz.sh scan --target https://example.com --scope-profile standard --aggressiveness standard

# 인증 포함(YAML 파일, 명령줄에 평문 자격 증명 없음)
./omega-fuzz.sh scan --target https://example.com --preset staging-full --auth-config auth.yaml

# Dry-run: 유효 구성과 예상 계획 표시, 요청 전송 없음
./omega-fuzz.sh scan --target https://example.com --preset prod-safe --dry-run

# 대상 지정 내보내기(폴더, 형식, HTML 테마)
./omega-fuzz.sh scan --target https://example.com --preset prod-safe \
    --output-dir ./rapports --format html --export-theme omega-neon
```

`scan` 옵션:

| 옵션 | 기본값 | 효과 |
|---|---|---|
| `--target` | *(필수)* | 대상 URL, `http://`/`https://` 스킴 필수(자동 완성되지 않음) |
| `--preset` | — | 준비된 프리셋([§4](#4-스코프-프로필과-프리셋) 참조) |
| `--scope-profile` | — | 스코프 프로필, `--aggressiveness`와 조합, `--preset` 없이 사용 |
| `--aggressiveness` | — | 공격성 수준, `--scope-profile`과 조합, `--preset` 없이 사용 |
| `--auth-config` | — | 인증 YAML 파일 |
| `--insecure-tls` | 비활성 | TLS 검증 비활성화(강화 확인 유발) |
| `--max-duration` | *(프로필 값)* | 최대 지속 시간(초) 재정의 |
| `--max-requests` | *(프로필 값)* | 최대 요청 수 재정의 |
| `--max-tests` | *(프로필 값)* | 최대 테스트 수 재정의 |
| `--max-concurrent` | *(프로필 값)* | 최대 동시성 재정의 |
| `--dry-run` | 비활성 | 유효 구성과 예상 계획 표시, 요청 전송 없음 |
| `--output-dir` | `var/exports/` | 내보낸 보고서 폴더, 이름 `<preset>-<타임스탬프>.<확장자>`(설정에서 변경 가능) |
| `--format` | `all` | `json`, `markdown`, `html` 또는 `all` |
| `--export-theme` | `omega-base` | 내보낸 HTML 보고서 테마(json/markdown에는 영향 없음) |

CLI에는 `history`/`show` 하위 명령이 없습니다: 기록과 즐겨찾기 대상은 TUI에서만 볼 수 있습니다.

`install.sh`가 별칭을 만들었다면 `fuzz scan ...`은 `./omega-fuzz.sh` 접두어 없이 터미널 어디에서든 작동합니다.

## 4. 스코프 프로필과 프리셋

### 스코프 프로필

| 프로필 | 모드 | 최대 깊이 | 제한 |
|---|---|---|---|
| `strict` | 정확한 대상 | 1 | `/health`, `/ready`, `/metrics`, `/favicon.ico`, `/robots.txt` 차단 |
| `standard` | + 서브도메인 | 2 | 일반적인 정적 서브도메인, 기술 경로, 자산(이미지/css/js/폰트) 차단 |
| `large` | + 서브도메인 | 4 | 기술 경로와 자산(아카이브/PDF 포함)만 차단 |
| `api` | 정확한 대상 | 3 | `/api`, `/v1`, `/v2`로 제한, 문서와 자산 차단 |
| `custom` | + 서브도메인 | 3 | 기본 제한 없음 — 수동 구성의 출발점 |

선택한 프로필과 무관하게 바이너리/대용량 파일 확장자 목록(`.iso`, `.zip`, `.exe`, `.mp4` 등)은 `custom`에서도 **항상** 크롤링과 퍼징에서 제외됩니다 — 이런 유형 파일로의 링크는 실제 HTTP 요청으로 가져오지 않아 다운로드 폴더가 스캔을 수 분 동안 늦추는 것을 방지합니다.

### 공격성 수준

`doux` · `standard` · `agressif` · `violent` — 각 수준은 고유한 기본 제한(지속 시간, 요청, 테스트, 깊이, 동시성)을 가지며, 프리셋이 지정되면 이를 재정의합니다.

### 준비된 프리셋

| 프리셋 | 스코프 | 공격성 | 최대 시간 | 최대 요청 | 최대 테스트 | 최대 깊이 | 강화 확인 |
|---|---|---|---|---|---|---|---|
| `prod-safe` | strict | doux | 300초 | 1,000 | 500 | 1 | 아니요 |
| `staging-full` | standard | standard | 1,800초 | 20,000 | 10,000 | 2 | 아니요 |
| `lab-deep` | large | agressif | 3,600초 | 100,000 | 50,000 | 4 | 아니요 |
| `lab-extreme` | large | violent | 7,200초 | 500,000 | 250,000 | 5 | **예** |
| `api-hardened` | api | agressif | 1,800초 | 50,000 | 25,000 | 3 | 아니요 |

스캔은 확인될 때까지 차단됩니다. **강화 확인**(정확한 문구 `OUI-J-AI-L-AUTORISATION` 입력)은 다음 세 요소 중 하나라도 있을 때 필요합니다: 공격성 `violent`, 프리셋 `lab-extreme`, TLS 검증 비활성화(`--insecure-tls`). 이 세 요소 중 어느 것도 없는 비정상 조합에서는 단순 예/아니요 확인으로 충분합니다.

## 5. 수행되는 보안 테스트

스코프 내에서 발견된 각 URL(및 그곳에서 발견된 각 `GET` 폼)에 대한 자동 파이프라인:

| 테스트 | 실행 조건 | 검사 내용 |
|---|---|---|
| 일반 매개변수 퍼징 | 모든 쿼리 문자열 매개변수 | 경계값/잘못된 형식 값에 대한 대상 반응 |
| 헤더 퍼징 | URL당 1회, 4개 고정 헤더(`User-Agent`, `Referer`, `X-Forwarded-For`, `Accept-Language`) | 헤더 내 경계값/잘못된 형식 값에 대한 대상 반응 |
| 폼 퍼징(`GET`만) | 스코프에서 발견된 모든 `GET` 폼 필드 | 폼 필드 내 경계값/잘못된 형식 값에 대한 대상 반응 |
| 반사형 XSS | 모든 쿼리 문자열 매개변수 | 응답에서 페이로드의 필터링되지 않은 반사(비파괴적) |
| 일반 인젝션 | 모든 쿼리 문자열 매개변수 | 인젝션 페이로드에 대한 응답에서 서버 오류 탐지(특정 SQL/NoSQL 핑거프린팅 없음) |
| 보안 헤더 | URL당 1회 | 응답에서 누락되거나 잘못 구성된 보안 헤더 |

처음 세 테스트(일반 매개변수/헤더/폼 퍼징)는 **탐지 없는** 변형 엔진입니다 — 직접 `Finding`을 생성하지 않으며, 발견된 서버 오류(5xx)만 해당 `Test`에 집계됩니다. findings를 생성하는 것은 서명(XSS, 인젝션, 보안 헤더)뿐입니다.

## 6. 점수와 심각도

탐지된 각 이상 현상은 관찰 성격에 따라 3개 축(`impact`, `exploitability`, `scope`, 각 1–5)으로 채점됩니다 — 매핑은 의도적으로 **보수적**입니다(범위 하한, 이 자동 단계에서는 인간 확인 없음):

| 원시 점수(3축 합계) | 심각도 |
|---|---|
| ≥ 13 | `critical` |
| ≥ 10 | `high` |
| ≥ 7 | `medium` |
| < 7 | `low` |

수동 조정(`severity_override`)은 가능하지만 항상 명시적인 근거가 필요합니다. 동등한 findings(동일 유형, 동일 엔드포인트, 동일 매개변수)는 중복 제거되며, 이용 가능한 최상의 증거가 유지됩니다(신뢰도 `omega_lib.core.confidence.ConfidenceLevel`, 동률 시 원시 점수).

## 7. 인증

전용 YAML 파일(`--auth-config`), 명령줄에 평문 자격 증명 없음:

| 모드 | 효과 |
|---|---|
| `none` | 인증 없음(기본값) |
| `cookie` | 세션 쿠키 직접 제공 |
| `bearer_token` | `Authorization: Bearer ...` 토큰 |
| `login_form` | 폼 기반 인증(로그인 URL, 사용자/비밀번호 필드) |

## 8. 아키텍처

Omega-Fuzz는 **Clean Architecture**(domain / application / infrastructure / interfaces / ports / core / app / plugins)로 구성되며, `omega-` 제품군 템플릿(`omega-check`/`omega-deep`/`omega-fold` 참조)과 일치하고 변경 시마다 `import-linter`로 검증됩니다. 전체 세부 사항은 **`docs/ARCHITECTURE.md`**에 있습니다.

매우 짧은 개요:

```text
src/omega_fuzz/
├── domain/          순수 도메인 로직(대상/스코프, 요청, 테스트, findings, 프로필, 보고서 등)
├── application/     유스케이스(commands/queries)와 오케스트레이터(발견, 스캔, 보고서, 제한)
├── ports/           애플리케이션이 기대하는 계약(http_client, repositories, exporters 등)
├── infrastructure/  구체적 구현(httpx, BeautifulSoup, SQLite, Jinja2 exporter — Textual은 여기에 없음)
├── interfaces/      tui/(Textual) 및 cli/(스크립트 가능), 엄격한 기능 대등성
├── plugins/         퍼저와 서명(순수 함수, 네트워크 직접 접근 없음)
├── app/             조립(Container, composition root, 수명 주기)
└── core/            공통 어휘, 오류, 상수
```

설계 규칙:

- `plugins/fuzzers/` 및 `plugins/signatures/`: 테스트 계획(`Test` + `ScanRequest`)을 만드는 순수 함수이며, `HttpClient`를 절대 사용하지 않습니다.
- `infrastructure/network/`: 네트워크 작업을 수행합니다(`httpx`, 메모리 제한 스트리밍). 판단하지 않습니다.
- `infrastructure/analyzers/`: 이미 수신한 응답을 읽고 구조화된 `Observation`을 생성합니다. 점수를 재계산하지 않습니다.
- `interfaces/`: 표시만 하며 비즈니스 로직을 포함하지 않습니다.

## 9. 내보내기

Markdown 및 HTML 보고서는 설정에서 선택한 언어(「내보내기 언어」, 기본값은 인터페이스 언어)로 작성됩니다. JSON은 데이터로 유지되며 번역되지 않습니다. 보고서는 기본적으로 `var/exports/`에 생성됩니다(런타임 경로는 프로젝트 폴더에 고정, `$OMEGA_FUZZ_VAR_DIR`로 재정의 가능, 설정 화면에서도 재정의 가능). 또는 지정된 경로(`--output-dir`)에 생성됩니다. 파일명은 하위 폴더 없이 평면적입니다: `<preset>-<타임스탬프>.<확장자>`(예: `prod-safe-2026-09-01_14-30-22.html`).

### JSON, 단일 진실 공급원

보고서의 전체 구조(유효 구성, 통계, 테스트, findings), 엄격하게 JSON 직렬화 가능.

### Markdown, 사람을 위한 간결한 보고서

터미널 밖에서 읽을 수 있으며 ANSI 코드가 없습니다.

### HTML, 독립형 웹 보고서

5가지 테마 선택 가능(CLI의 `--export-theme`, TUI의 선택기): `omega-base`, `omega-burn`, `omega-neon`, `light-basic`, `light-alt`.

## 10. 기록 및 즐겨찾기 대상

각 스캔은 findings와 함께 SQLite(`var/db/omega-fuzz.db`)에 저장되며 TUI의 기록 화면에서 볼 수 있습니다. `Scan`과 `Finding`만 저장됩니다 — 전체 유효 구성이나 상세 요청은 저장되지 않습니다 — 따라서 이 화면에서는 재실행, 비교 또는 재내보내기가 없습니다(화면이 이를 설명하며 데이터를 만들지 않습니다).

**대상** 화면은 즐겨찾기 목록(정규화된 URL, `var/targets.json`)을 유지하며, 새 스캔의 대상 필드를 직접 채우는 데 재사용할 수 있습니다.

## 11. 스크린샷

명령 팔레트(`Ctrl+P`)의 **스크린샷** 명령: 현재 TUI 화면의 SVG를 기본적으로 `var/screenshots/`에 저장합니다. 설정 화면에서 변경 가능합니다(내보내기 폴더와 마찬가지). 설정에는 전용 정리 기능도 있습니다.

## 12. 터미널 호환성

TUI(Textual)는 터미널 기능(에뮬레이터, 크기)을 자동 감지하고 그에 따라 구조적 스타일시트(`complete`/`standard`/`reduced`/`mono`)를 조정합니다. 수동 플래그가 필요 없습니다. CLI는 항상 일반 텍스트이며 터미널과 무관합니다. 이 정책은 전체 `omega-` 제품군이 공유합니다(`omega-lib`, `terminal/policies.py`).

### 감지된 에뮬레이터별 프로필

| 에뮬레이터 | 초기 프로필 |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | `complete` |
| Konsole, GNOME Terminal, Terminator, Xfce4 Terminal | `standard` |
| xterm, urxvt, 최신 SSH | `reduced` |
| Linux TTY, 구형 SSH | `mono` |
| 인식되지 않는 에뮬레이터 | `reduced`(기본 폴백) |

### 터미널 크기별 프로필

| 최소 크기(열 × 행) | 프로필 상한 |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| 그 미만 | `mono` |

최종 프로필은 둘 중 **더 제한적인 쪽**(에뮬레이터와 크기)입니다 — `r` 키로 실시간 새로 고침할 수 있습니다.

## 13. 테스트

```bash
source .venv/bin/activate
lint-imports        # Dependency Rule(6개 계약) 검증
pytest -q           # 344개 테스트
ruff check src tests
mypy -p omega_fuzz
```

구조: `tests/unit/`(도메인 및 애플리케이션, 실제 I/O 없음), `tests/integration/`(`tmp_path`를 통한 실제 파일시스템, `pytest-httpserver` 가짜 HTTP 서버, 실제 SQLite 데이터베이스, 엔드투엔드 CLI), `tests/tui/`(`Pilot`을 통한 탐색, 구조적 검사 — 자동 시각 검증을 주장하지 않음).

## 14. 범위 밖

- JSON 본문 퍼징(코드 존재, 미연결 — API 스키마 발견 없음)
- `POST`/`PUT`/`DELETE` 폼 퍼징(의도적으로 제외, 쓰기 위험)
- 수동 호출 외 비즈니스 로직 테스트(IDOR, 권한, 워크플로우)
- 다중 대상 동시 스캔
- 기록에서 재실행, 비교 또는 내보내기
- 클라이언트 측 JavaScript 렌더링
- 웹 대시보드

---

> Omega-Fuzz — 범위를 발견하고, 명시적인 안전장치로 테스트하며, 확인되지 않은 것을 추측하지 않습니다.

<p align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/ko/omega-fuzz/A.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/ko/omega-fuzz/B.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/ko/omega-fuzz/C.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/ko/omega-fuzz/D.png" width="24%" />
</p>
