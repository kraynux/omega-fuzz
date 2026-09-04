<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - MIT 许可证（参见 LICENSE 文件） -->
<div align="center">
  <img src="docs/assets/omega-fuzz.png" alt="Omega-Fuzz" width="256">
</div>

# 🗱 OMEGA-FUZZ

**漏洞扫描器**

> 由 **kraynux** 为 **Omega-server** 开发  
[https://kraynux.snake-mackarel.ts.net](https://kraynux.snake-mackarel.ts.net)

官方页面：[OMEGA-FUZZ](https://kraynux.snake-mackarel.ts.net/omega-fuzz/) &nbsp; 预览：[Screenshots](https://kraynux.snake-mackarel.ts.net/omega-fuzz/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

**语言：**  
[Français](README.md) · [English](README.en.md) · [Español](README.es.md) · [Русский](README.ru.md) · [中文](README.zh-CN.md)

**Omega-Fuzz** 是一款本地终端应用程序（TUI [Textual](https://github.com/Textualize/textual) + 可脚本化 CLI），用于在获得授权的环境中执行 Web 发现和安全测试（HTTP 模糊测试），例如实验室、个人镜像和明确获准的测试项目。

这是 `omega-` 套件中的第六个工具（继 `omega-scan`、`omega-stress`、`omega-check`、`omega-deep` 和 `omega-fold` 之后），采用 Clean Architecture 架构。完整的技术细节请参阅 `docs/ARCHITECTURE.md`。

## 1. 愿景与范围

### Omega-Fuzz 的功能

- 使用由明确 scope 限制的 BFS 发现单个目标的范围（协议/子域名/允许或阻止的路径/深度），始终启用安全限制。
- 对每个已发现 URL 中的 query string 参数、HTTP 标头和 `GET` 表单执行通用模糊测试，并检查三类特征：非破坏性的反射型 XSS、通用注入（检测响应中的错误）以及缺失或配置错误的安全标头。请参阅 [§5](#5-执行的安全测试)。
- 从影响/可利用性/范围三个维度对每个异常进行评分，并推导出严重性（`low`/`medium`/`high`/`critical`）；按照 `(type, endpoint, parameter)` 去重，同时保留最佳证据。请参阅 [§6](#6-评分与严重性)。
- 通过专用 YAML 文件支持身份验证（cookie、bearer token、登录表单）；绝不会将凭据放在命令行中。
- 通过 TUI（Textual）或可脚本化 CLI 输出结果，支持三种导出格式（JSON、Markdown 和包含 5 种主题的 HTML）。
- 使用 SQLite 持久保存扫描及其 findings 的历史记录，并维护可重复使用的收藏目标列表。
- 在执行任何激进、扩展型扫描，或禁用 TLS 验证的扫描之前，要求明确确认（最敏感的情况需要输入严格短语）。

### Omega-Fuzz 不执行的功能

- JSON 请求体模糊测试：代码已存在（`plugins/fuzzers/json_body_fuzzer.py`），但尚未接入（HTML/BFS 发现不会生成 JSON API schema，也没有可用的模板来源）。
- `POST`/`PUT`/`DELETE` 表单模糊测试：出于设计考虑从自动 pipeline 中排除（目标上可能产生非预期写入）；仅测试 `GET` 表单。
- 业务逻辑测试（IDOR、授权控制、workflow 中断）：代码已存在（`plugins/logic_tests/`），但仍处于自动 pipeline 之外，只能单独调用；标准扫描永远不会触发它。
- 并行多目标扫描：每次扫描只处理一个目标。
- 从历史记录界面重放、比较或导出：只持久化 `Scan` 和 `Finding`（不保存完整的实际配置或请求）；从历史记录重新执行或导出会生成不可靠的数据，因此界面会解释这一限制，而不是静默提供相关选项。
- 客户端 JavaScript 渲染（页面按服务器提供的原样获取，不会在无头浏览器中执行）。
- Web 控制面板。

## 2. 安装

### 前置要求

- Python 3.10+
- 用于安装依赖的 Internet 连接
- 对于 TUI：终端中需要安装 [Nerd Font](https://www.nerdfonts.com/)，用于显示标题图标。如果没有该字体，字符会显示为空方框（与 emoji 类似的限制，但 Nerd Font 在终端用户中更为普及）。缺少字体不会影响功能，仅影响外观。

### 安装

```bash
[ -d omega-fuzz ] && echo "ℹ️ 已在此处解压，跳过此步骤。" || tar -xzf omega-fuzz.tar.gz
cd omega-fuzz/
chmod +x install.sh
./install.sh
```

`install.sh`：

1. 如果 `.venv` 尚不存在，则创建虚拟环境。
2. 安装依赖（先处理 `vendor/omega-lib/`，然后执行 `pip install -e .`；`pyproject.toml` 始终是唯一的事实来源）。
3. 将 `omega-fuzz.sh` 和 `install.sh` 设置为可执行。
4. 将 `fuzz` 别名添加到 `~/.bashrc` 和 `~/.zshrc`（如果已存在则不会重复添加）。

### 依赖

在 `pyproject.toml` 中声明（不存在 `requirements.txt`）：
- `omega-lib`：套件共享库（导出主题、终端检测、`ConfidenceLevel`），已包含在 `vendor/omega-lib/` 中
- `httpx`：异步 HTTP 请求（发现 + 模糊测试），响应采用流式处理（即使目标提供数 GB 的文件，也不会将完整响应缓存在内存中）
- `beautifulsoup4` + `lxml`：提取 URL 和 HTML 表单
- `jinja2`：HTML 导出的模板引擎
- `textual`：TUI 界面、主题和终端自动适配
- `pyyaml`：加载 `--auth-config` 文件
- 开发依赖（`pip install -e ".[dev]"`）：`pytest`、`pytest-asyncio`、`pytest-cov`、`pytest-httpserver`、`ruff`、`mypy`、`import-linter`

## 3. 使用方法

### 交互模式（TUI）

建议日常使用时采用此模式 — 不带参数启动：

```bash
./omega-fuzz.sh
```
如果已经创建别名，只需在终端中输入：
```bash
fuzz
```

流程：启动界面（按键或点击后关闭）→ 主菜单（Scanner / Targets / Settings / History / Help）→ 输入目标（完整 URL，必须包含 `http://`/`https://` 协议），选择 preset 或手动配置（scope + aggressiveness），可选身份验证、TLS 验证和限制覆盖 → 审核界面（普通确认；敏感情况需要严格短语 `OUI-J-AI-L-AUTORISATION`）→ 扫描（不确定进度指示器，可随时点击 **停止**）→ 结果（findings、导出）→ 从主菜单查看历史（过去扫描的详细信息及相关 findings）和收藏目标。终端适配（颜色、尺寸和结构降级）会自动完成。

#### 键盘快捷键

| 按键 | 操作 |
|---|---|
| `↑` / `↓` | 在屏幕元素之间移动 |
| `Tab` / `Shift+Tab` | 在表单字段之间移动 |
| `Esc` | 返回上一屏（主页会显示退出确认） |
| `t` | 下一个主题（立即应用，无需确认） |
| `r` | 刷新终端检测 |
| `a` | 显示帮助（包括 preset 表格） |
| `q` | 退出（需要确认） |
| `Ctrl+P` | 命令面板（Theme、Quit、Screenshot） |

### 可脚本化模式（CLI）

```bash
# 使用可直接使用的 preset 扫描
./omega-fuzz.sh scan --target https://example.com --preset prod-safe

# 手动组合 scope + aggressiveness（不使用 preset）
./omega-fuzz.sh scan --target https://example.com --scope-profile standard --aggressiveness standard

# 使用身份验证（YAML 文件；绝不要在命令行中输入凭据）
./omega-fuzz.sh scan --target https://example.com --preset staging-full --auth-config auth.yaml

# Dry run：显示实际配置和预计计划；不会发送请求
./omega-fuzz.sh scan --target https://example.com --preset prod-safe --dry-run

# 定向导出（目录、格式、HTML 主题）
./omega-fuzz.sh scan --target https://example.com --preset prod-safe \
    --output-dir ./rapports --format html --export-theme omega-neon
```

`scan` 选项：

| 选项 | 默认值 | 作用 |
|---|---|---|
| `--target` | *(必需)* | 目标 URL；必须使用 `http://`/`https://` 协议（不会自动补全） |
| `--preset` | — | 可直接使用的 preset（参阅 [§4](#4-scope-配置文件与-preset)） |
| `--scope-profile` | — | scope 配置文件，与 `--aggressiveness` 组合使用，不能与 `--preset` 同时使用 |
| `--aggressiveness` | — | 激进程度，与 `--scope-profile` 组合使用，不能与 `--preset` 同时使用 |
| `--auth-config` | — | 身份验证 YAML 文件 |
| `--insecure-tls` | 已禁用 | 禁用 TLS 验证（触发增强确认） |
| `--max-duration` | *(来自配置文件)* | 覆盖最大持续时间（秒） |
| `--max-requests` | *(来自配置文件)* | 覆盖最大请求数 |
| `--max-tests` | *(来自配置文件)* | 覆盖最大测试数 |
| `--max-concurrent` | *(来自配置文件)* | 覆盖最大并发数 |
| `--dry-run` | 已禁用 | 显示实际配置和预计计划；不发送请求 |
| `--output-dir` | `var/exports/` | 导出报告目录，文件名为 `<preset>-<timestamp>.<ext>`（可在 Settings 中覆盖） |
| `--format` | `all` | `json`、`markdown`、`html` 或 `all` |
| `--export-theme` | `omega-base` | 导出 HTML 报告的主题（对 json/markdown 无影响） |

CLI 没有 `history`/`show` 子命令：只能从 TUI 查看历史记录和收藏目标。

如果 `install.sh` 创建了别名，则无需 `./omega-fuzz.sh` 前缀，在终端任意位置都可以执行 `fuzz scan ...`。

## 4. Scope 配置文件与 preset

### Scope 配置文件

| 配置文件 | 模式 | 最大深度 | 限制 |
|---|---|---|---|
| `strict` | 精确目标 | 1 | 阻止 `/health`、`/ready`、`/metrics`、`/favicon.ico`、`/robots.txt` |
| `standard` | + 子域名 | 2 | 阻止常见静态子域名、技术路径和资源（images/css/js/fonts） |
| `large` | + 子域名 | 4 | 仅阻止技术路径和资源（包括归档文件/PDF） |
| `api` | 精确目标 | 3 | 限制为 `/api`、`/v1`、`/v2`；阻止文档和资源 |
| `custom` | + 子域名 | 3 | 默认没有限制 — 手动配置的起点 |

无论选择哪种配置文件，二进制或大型扩展名列表（`.iso`、`.zip`、`.exe`、`.mp4` 等）都会**始终**从爬取和模糊测试中排除，即使使用 `custom` 也是如此。此类文件的链接不会通过真实 HTTP 请求获取，以避免下载目录让扫描长时间变慢。

### 激进程度

`doux` · `standard` · `agressif` · `violent` — 每个级别都有自己的基础限制（持续时间、请求数、测试数、深度和并发数），在适用时可由 preset 覆盖。

### 可直接使用的 preset

| Preset | Scope | 激进程度 | 最大持续时间 | 最大请求数 | 最大测试数 | 最大深度 | 增强确认 |
|---|---|---|---|---|---|---|---|
| `prod-safe` | strict | doux | 300 秒 | 1,000 | 500 | 1 | 否 |
| `staging-full` | standard | standard | 1,800 秒 | 20,000 | 10,000 | 2 | 否 |
| `lab-deep` | large | agressif | 3,600 秒 | 100,000 | 50,000 | 4 | 否 |
| `lab-extreme` | large | violent | 7,200 秒 | 500,000 | 250,000 | 5 | **是** |
| `api-hardened` | api | agressif | 1,800 秒 | 50,000 | 25,000 | 3 | 否 |

扫描在获得确认前会保持阻止状态。出现以下三个因素中的任意一个时，必须进行**增强确认**（输入准确短语 `OUI-J-AI-L-AUTORISATION`）：激进程度为 `violent`、使用 `lab-extreme` preset，或禁用 TLS 验证（`--insecure-tls`）。不包含这些因素的异常组合只需要普通的“是/否”确认。

## 5. 执行的安全测试

自动 pipeline 会针对 scope 中发现的每个 URL 以及其中找到的每个 `GET` 表单执行：

| 测试 | 触发条件 | 检查内容 |
|---|---|---|
| 通用参数模糊测试 | 每个 query string 参数 | 目标对边界值或格式错误值的行为 |
| 标头模糊测试 | 每个 URL 一次，4 个固定标头（`User-Agent`、`Referer`、`X-Forwarded-For`、`Accept-Language`） | 目标对标头中的边界值或格式错误值的行为 |
| 表单模糊测试（仅 `GET`） | scope 中发现的每个 `GET` 表单字段 | 目标对表单字段中的边界值或格式错误值的行为 |
| 反射型 XSS | 每个 query string 参数 | 响应中 payload 的未过滤反射（非破坏性） |
| 通用注入 | 每个 query string 参数 | 对注入 payload 的响应中服务器错误的检测（不执行特定 SQL/NoSQL 指纹识别） |
| 安全标头 | 每个 URL 一次 | 响应中缺失或配置错误的安全标头 |

前三项测试（通用参数/标头/表单模糊测试）是**不进行检测**的变异引擎：它们不会直接生成 `Finding`；只有遇到的服务器错误（5xx）会计入相应的 `Test`。只有特征检测（XSS、注入和安全标头）会生成 findings。

## 6. 评分与严重性

每个检测到的异常会根据观察结果的性质，从三个维度（`impact`、`exploitability`、`scope`，每项 1 到 5 分）进行评分。映射过程有意保持**保守**（取范围下限，在当前自动阶段不进行人工确认）：

| 原始分数（三个维度之和） | 严重性 |
|---|---|
| ≥ 13 | `critical` |
| ≥ 10 | `high` |
| ≥ 7 | `medium` |
| < 7 | `low` |

可以进行手动调整（`severity_override`），但始终需要明确说明理由。等效 findings（类型、endpoint 和参数均相同）会被去重，并保留最佳可用证据（先比较置信度 `omega_lib.core.confidence.ConfidenceLevel`，相同情况下再比较原始分数）。

## 7. 身份验证

使用专用 YAML 文件（`--auth-config`），绝不在命令行中输入凭据：

| 模式 | 作用 |
|---|---|
| `none` | 不进行身份验证（默认） |
| `cookie` | 直接提供会话 Cookie |
| `bearer_token` | `Authorization: Bearer ...` 令牌 |
| `login_form` | 通过表单进行身份验证（登录 URL、用户名和密码字段） |

## 8. 架构

Omega-Fuzz 采用 **Clean Architecture**（domain / application / infrastructure / interfaces / ports / core / app / plugins），与 `omega-` 套件模板保持一致（参见 `omega-check`/`omega-deep`/`omega-fold`），并在每次修改后由 `import-linter` 检查。完整说明位于 **`docs/ARCHITECTURE.md`**。

简要结构：

```text
src/omega_fuzz/
├── domain/          纯业务逻辑（目标/scope、请求、测试、findings、配置文件、报告等）
├── application/     用例（commands/queries）和编排器（发现、扫描、报告、限制）
├── ports/           应用所需的契约（http_client、repositories、exporters 等）
├── infrastructure/  具体实现（httpx、BeautifulSoup、SQLite、Jinja2 导出器 — Textual 不在此处）
├── interfaces/      tui/（Textual）和 cli/（可脚本化），保持严格的功能对等
├── plugins/         Fuzzers 和特征检测（纯函数，从不直接访问网络）
├── app/             组装（Container、composition root、生命周期）
└── core/            跨模块术语、错误和常量
```

设计规则：
- `plugins/fuzzers/` 和 `plugins/signatures/`：用于构建测试计划（`Test` + `ScanRequest`）的纯函数；绝不访问 `HttpClient`。
- `infrastructure/network/`：负责网络操作（`httpx`、内存受限的流式处理），不做判断。
- `infrastructure/analyzers/`：读取已接收的响应并生成结构化的 `Observation`，绝不重新计算分数。
- `interfaces/`：只负责显示，不包含业务逻辑。

## 9. 导出

默认情况下，报告生成于 `var/exports/`（运行时路径以项目目录为基准，可使用 `$OMEGA_FUZZ_VAR_DIR` 覆盖，也可以在 Settings 中覆盖），或者生成到 `--output-dir` 指定的路径。文件名为扁平结构，不包含子目录：`<preset>-<timestamp>.<ext>`（例如 `prod-safe-2026-09-01_14-30-22.html`）。

### JSON，事实来源

报告的完整结构（实际配置、统计信息、测试和 findings），严格可序列化为 JSON。

### Markdown，紧凑的人类可读报告

可在终端之外阅读，不包含 ANSI 代码。

### HTML，独立的 Web 报告

提供 5 种主题（CLI 使用 `--export-theme`，TUI 使用选择器）：`omega-base`、`omega-burn`、`omega-neon`、`light-basic`、`light-alt`。

## 10. 历史记录与收藏目标

每次扫描都会与 findings 一起持久化（SQLite，`var/db/omega-fuzz.db`），并可从 TUI 的历史记录界面查看。只保存 `Scan` 和 `Finding`，不会保存实际配置或详细请求，因此无法从此界面重放、比较或重新导出（界面会解释这一点，而不会生成虚假数据）。

**Targets** 界面会保存收藏列表（规范化 URL，`var/targets.json`），可用于直接预填新扫描的 Target 字段。

## 11. 屏幕截图

命令面板（`Ctrl+P`）中的 **Screenshot** 命令默认会将当前 TUI 屏幕保存为 SVG，位置为 `var/screenshots/`。可在 Settings 中覆盖该位置（与导出目录相同），Settings 中还提供专用清理功能。

## 12. 终端兼容性

TUI（Textual）会自动检测终端能力（模拟器和尺寸），并相应调整结构样式表（`complete`/`standard`/`reduced`/`mono`），无需手动设置标志。CLI 模式始终保持纯文本，与终端无关。整个 `omega-` 套件共享此策略（`omega-lib`、`terminal/policies.py`）。

### 按检测到的模拟器选择配置文件

| 模拟器 | 初始配置文件 |
|---|---|
| Ghostty、Alacritty、WezTerm、Kitty | `complete` |
| Konsole、GNOME Terminal、Terminator、Xfce4 Terminal | `standard` |
| xterm、urxvt、现代 SSH | `reduced` |
| Linux TTY、旧版 SSH | `mono` |
| 未识别的模拟器 | `reduced`（默认回退） |

### 按终端尺寸选择配置文件

| 最小尺寸（列 × 行） | 配置文件上限 |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| 更小 | `mono` |

最终配置文件为**两者中限制更严格的一个**（模拟器和尺寸）；可以使用 `r` 键实时刷新。

## 13. 测试

```bash
source .venv/bin/activate
lint-imports        # 检查 Dependency Rule（6 个契约）
pytest -q           # 317 个测试
ruff check src tests
mypy -p omega_fuzz
```

结构：`tests/unit/`（domain 和 application，不进行真实 I/O）、`tests/integration/`（通过 `tmp_path` 使用真实文件系统、通过 `pytest-httpserver` 使用虚假 HTTP 服务器、真实 SQLite 数据库、端到端 CLI）、`tests/tui/`（通过 `Pilot` 进行导航，结构测试；不声称执行自动视觉验证）。

## 14. 不在范围内

- JSON 请求体模糊测试（代码存在但未接入 — 不进行 API schema 发现）
- `POST`/`PUT`/`DELETE` 表单模糊测试（出于设计排除，存在写入风险）
- 业务逻辑测试（IDOR、授权、workflow），只能手动调用
- 同时扫描多个目标
- 从历史记录中重放、比较或导出
- 客户端 JavaScript 渲染
- Web 控制面板

---

> Omega-Fuzz — 发现范围，在明确安全限制下进行测试，绝不猜测未经确认的内容。
