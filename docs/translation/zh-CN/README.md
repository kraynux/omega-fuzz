<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - MIT 许可证（参见 LICENSE 文件） -->
<div align="center">
  <img src="../../assets/omega-fuzz.png" alt="Omega-Fuzz" width="384">
</div>

# 🗱 OMEGA-FUZZ

**漏洞扫描器**

> 由 **kraynux** 为 **Omega-server** 开发  
> [https://kraynux.snake-mackarel.ts.net](https://kraynux.snake-mackarel.ts.net)

官方页面：[OMEGA-FUZZ](https://kraynux.snake-mackarel.ts.net/omega-fuzz/) &nbsp; 截图：[Screenshots](https://kraynux.snake-mackarel.ts.net/omega-fuzz/screenshots/)  

[![许可证：MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![平台](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![界面](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

🌐 界面和导出报告支持 **17 种语言** — 参见[界面语言](#界面语言)。  
**语言：**  
<img src="https://flagcdn.com/w20/fr.png" alt="Français" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)

**Omega-Fuzz** 是一个本地终端应用（基于 [Textual](https://github.com/Textualize/textual) 的 TUI，以及可脚本化的 CLI），用于在已授权环境中执行 Web 安全发现与测试（HTTP fuzzing），例如实验室、个人镜像或已明确同意的测试项目。

该工具属于 `omega-` 工具系列，采用 Clean Architecture 构建 — 完整技术细节见 `docs/ARCHITECTURE.md`。

## 1. 目标与范围

### Omega-Fuzz 做什么

- 通过 BFS 发现单个目标的范围，并由明确的 scope 限制（协议、子域名、允许/阻止的路径、深度），绝不会在没有防护措施的情况下运行。
- 对在每个发现 URL 上找到的查询字符串参数、HTTP 请求头和 `GET` 表单执行通用 fuzzing，并检查三类签名：非破坏性反射型 XSS、通用注入（检测响应中的错误）以及缺失或配置不当的安全响应头 — 参见[§5](#5-执行的安全测试)。
- 按影响、可利用性和范围三个维度评估每项异常，并推导出严重级别（`low`/`medium`/`high`/`critical`），按 `(类型, endpoint, 参数)` 去重并保留最佳证据 — 参见[§6](#6-评分与严重级别)。
- 通过专用 YAML 文件支持认证（cookie、Bearer token、登录表单）；凭据绝不会以明文形式出现在命令行中。
- 在 TUI（Textual）或可脚本化 CLI 中呈现结果，并提供三种导出格式（JSON、Markdown、五种主题的 HTML）。
- 在 SQLite 中持久保存扫描历史及其发现结果，并维护可重复使用的收藏目标列表。
- 在执行任何激进扫描、扩展扫描或禁用 TLS 验证的扫描前，要求明确确认（在最敏感的情况下需要输入准确短语）。

### Omega-Fuzz 不做什么

- JSON 请求体 fuzzing — 代码存在（`plugins/fuzzers/json_body_fuzzer.py`），但尚未接入（HTML/BFS 发现不会产生任何 JSON API schema，也没有可利用的模板来源）。
- `POST`/`PUT`/`DELETE` 表单 fuzzing — 出于自动化流水线的设计选择而被排除（存在对目标产生非预期写入的风险）；仅测试 `GET` 表单。
- 业务逻辑测试（IDOR、授权控制、流程破坏）— 代码存在（`plugins/logic_tests/`），但仍在自动化流水线之外，只能单独调用，绝不会由标准扫描触发。
- 多目标并行扫描 — 每次扫描仅针对一个目标。
- 从历史界面重新执行、比较或导出 — 仅持久化 `Scan` 和 `Finding`（不包括完整生效配置或请求）；从历史重新执行或导出会制造数据。界面会说明这一点，而不是静默提供该功能。
- 客户端 JavaScript 渲染（页面按服务器返回的原样获取，不会在 headless 浏览器中执行）。
- Web 仪表板。

## 2. 安装

### 前提条件

- Python 3.10+
- 安装依赖需要网络连接
- 使用 TUI 时，终端需安装 [Nerd Font](https://www.nerdfonts.com/) 字体以显示标题图标 — 否则该字符会显示为空白方块（与 emoji 的限制相同，但在终端用户中更为常见）。缺失不会影响功能，纯属外观问题。

### 安装

```bash
[ -d omega-fuzz ] && echo "ℹ️ 已在此解压，跳过该步骤。" || tar -xzf omega-fuzz.tar.gz
cd omega-fuzz/
chmod +x install.sh
./install.sh
```

`install.sh` 会：

1. 在 `.venv` 虚拟环境不存在时创建它。
2. 安装依赖（先安装 `vendor/omega-lib/`，然后执行 `pip install -e .`；`pyproject.toml` 仍是唯一事实来源）。
3. 为 `omega-fuzz.sh` 和 `install.sh` 添加执行权限。
4. 在 `~/.bashrc` 和 `~/.zshrc` 中添加 `fuzz` 别名（若已存在则不重复添加）。

### 依赖

依赖在 `pyproject.toml` 中声明（没有 `requirements.txt`）：

- `omega-lib` — 工具系列共享库（导出主题、终端检测、`ConfidenceLevel`）— 位于 `vendor/omega-lib/`
- `httpx` — 异步 HTTP 请求（发现 + fuzzing）及响应流式处理（绝不会将完整响应缓冲在内存中，即使目标提供的是数 GB 的文件）
- `beautifulsoup4` + `lxml` — 提取 URL 和 HTML 表单
- `jinja2` — HTML 导出模板
- `textual` — TUI 界面、主题、自动适配终端
- `pyyaml` — 加载 `--auth-config` 文件
- 开发依赖（`pip install -e ".[dev]"`）：`pytest`、`pytest-asyncio`、`pytest-cov`、`pytest-httpserver`、`ruff`、`mypy`、`import-linter`

## 3. 使用方法

### 交互模式（TUI）

推荐用于日常使用 — 不带参数启动：

```bash
./omega-fuzz.sh
```

如果已创建别名，只需在终端输入 `fuzz`：

```bash
fuzz
```

流程：启动界面（按键或点击后关闭）→ 主菜单（扫描 / 目标 / 设置 / 历史 / 帮助）→ 输入目标（完整 URL，必须包含 `http://`/`https://` 协议）、选择预设或手动配置（scope + 攻击强度）、可选认证、TLS 验证、覆盖限制 → 审核界面（简单确认，敏感情况需输入准确短语 `OUI-J-AI-L-AUTORISATION`）→ 扫描（不确定进度指示，随时可点击**停止**）→ 结果（findings、导出）→ 历史界面（查看过往扫描详情及相关 findings）以及主菜单中的收藏目标。终端适配（颜色、尺寸、结构降级）自动完成。

#### 键盘快捷键

| 按键 | 操作 |
|---|---|
| `↑` / `↓` | 在界面元素间导航 |
| `Tab` / `Shift+Tab` | 在表单字段间导航 |
| `Esc` | 返回上一界面（在启动界面会要求确认退出） |
| `t` | 切换到下一个主题（立即生效，无需确认） |
| `r` | 刷新终端检测 |
| `a` | 显示帮助（包含预设表格） |
| `q` | 退出（需确认） |
| `Ctrl+P` | 命令面板（Theme、退出、截图） |

### 界面语言

界面支持 17 种语言：法语、英语、西班牙语、葡萄牙语（巴西）、意大利语、德语、荷兰语、波兰语、俄语、简体中文、越南语、泰语、印尼语、日语、韩语、印地语和阿拉伯语。可在“设置”（“语言 / Language”）中选择语言，重启界面后生效；环境变量 `OMEGA_FUZZ_LANG`（例如 `OMEGA_FUZZ_LANG=en ./omega-fuzz.sh`）可在单次会话中强制指定语言。从 omega-suite 启动时，omega-fuzz 会采用整个工具套件的语言。在 Linux 文本控制台（TTY）中，非拉丁文字语言在会话期间会以英语显示。命令行界面保持法语。

### 脚本模式（CLI）

```bash
# 使用现成预设扫描
./omega-fuzz.sh scan --target https://example.com --preset prod-safe

# 手动组合 scope 和 aggressiveness（不使用预设）
./omega-fuzz.sh scan --target https://example.com --scope-profile standard --aggressiveness standard

# 使用认证（YAML 文件，绝不在命令行中明文提供凭据）
./omega-fuzz.sh scan --target https://example.com --preset staging-full --auth-config auth.yaml

# Dry-run：显示生效配置和预估计划，不发送任何请求
./omega-fuzz.sh scan --target https://example.com --preset prod-safe --dry-run

# 指定导出（目录、格式、HTML 主题）
./omega-fuzz.sh scan --target https://example.com --preset prod-safe \
    --output-dir ./rapports --format html --export-theme omega-neon
```

`scan` 命令选项：

| 选项 | 默认值 | 说明 |
|---|---|---|
| `--target` | *（必填）* | 目标 URL，必须包含 `http://`/`https://` 协议（绝不会自动补全） |
| `--preset` | — | 现成预设（参见[§4](#4-范围配置与预设)） |
| `--scope-profile` | — | 范围配置，需与 `--aggressiveness` 组合使用，不与 `--preset` 同时使用 |
| `--aggressiveness` | — | 攻击强度，需与 `--scope-profile` 组合使用，不与 `--preset` 同时使用 |
| `--auth-config` | — | 认证 YAML 文件 |
| `--insecure-tls` | 关闭 | 禁用 TLS 验证（触发强化确认） |
| `--max-duration` | *（来自配置）* | 覆盖最大持续时间（秒） |
| `--max-requests` | *（来自配置）* | 覆盖最大请求数 |
| `--max-tests` | *（来自配置）* | 覆盖最大测试数 |
| `--max-concurrent` | *（来自配置）* | 覆盖最大并发数 |
| `--dry-run` | 关闭 | 显示生效配置和预估计划，不发送任何请求 |
| `--output-dir` | `var/exports/` | 导出报告目录，文件名为 `<preset>-<时间戳>.<扩展名>`（可在设置中覆盖） |
| `--format` | `all` | `json`、`markdown`、`html` 或 `all` |
| `--export-theme` | `omega-base` | 导出的 HTML 报告主题（对 json/markdown 无影响） |

CLI 中没有 `history`/`show` 子命令：历史和收藏目标只能在 TUI 中查看。

如果 `install.sh` 已创建别名，`fuzz scan ...` 可在终端任意位置使用，无需 `./omega-fuzz.sh` 前缀。

## 4. 范围配置与预设

### 范围配置

| 配置 | 模式 | 最大深度 | 限制 |
|---|---|---|---|
| `strict` | 精确目标 | 1 | 阻止 `/health`、`/ready`、`/metrics`、`/favicon.ico`、`/robots.txt` |
| `standard` | + 子域名 | 2 | 阻止常见静态子域名、技术路径和静态资源（图片/css/js/字体） |
| `large` | + 子域名 | 4 | 仅阻止技术路径和静态资源（包括压缩包/PDF） |
| `api` | 精确目标 | 3 | 限制为 `/api`、`/v1`、`/v2`；阻止文档和静态资源 |
| `custom` | + 子域名 | 3 | 默认无限制 — 手动配置的起点 |

无论选择哪种配置，二进制/大体积文件扩展名列表（`.iso`、`.zip`、`.exe`、`.mp4` 等）**始终**被排除在爬取和 fuzzing 之外，即使在 `custom` 模式下也是如此 — 指向此类文件的链接绝不会通过真实 HTTP 请求获取，以避免下载目录使扫描变慢数分钟。

### 攻击强度

`doux` · `standard` · `agressif` · `violent` — 每个强度都有自己的基础限制（时长、请求数、测试数、深度、并发数），若使用预设则会被其覆盖。

### 现成预设

| 预设 | 范围 | 攻击强度 | 最大时间 | 最大请求 | 最大测试 | 最大深度 | 强化确认 |
|---|---|---|---|---|---|---|---|
| `prod-safe` | strict | doux | 300 秒 | 1,000 | 500 | 1 | 否 |
| `staging-full` | standard | standard | 1,800 秒 | 20,000 | 10,000 | 2 | 否 |
| `lab-deep` | large | agressif | 3,600 秒 | 100,000 | 50,000 | 4 | 否 |
| `lab-extreme` | large | violent | 7,200 秒 | 500,000 | 250,000 | 5 | **是** |
| `api-hardened` | api | agressif | 1,800 秒 | 50,000 | 25,000 | 3 | 否 |

扫描在确认前会被阻止。当存在以下三个因素中的任意一个时，需要**强化**确认（输入准确短语 `OUI-J-AI-L-AUTORISATION`）：攻击强度为 `violent`、预设为 `lab-extreme`，或禁用 TLS 验证（`--insecure-tls`）— 若为不含这三个因素中任何一个的异常组合，则只需简单的是/否确认。

## 5. 执行的安全测试

自动化流水线，针对范围内发现的每个 URL（以及其中发现的每个 `GET` 表单）：

| 测试 | 触发条件 | 检查内容 |
|---|---|---|
| 通用参数 fuzzing | 每个查询字符串参数 | 目标对边界值或畸形值的反应 |
| 请求头 fuzzing | 每个 URL 一次，4 个固定请求头（`User-Agent`、`Referer`、`X-Forwarded-For`、`Accept-Language`） | 目标对请求头中边界值或畸形值的反应 |
| 表单 fuzzing（仅 `GET`） | 范围内发现的每个 `GET` 表单字段 | 目标对表单字段中边界值或畸形值的反应 |
| 反射型 XSS | 每个查询字符串参数 | payload 是否未经过滤地反射到响应中（非破坏性） |
| 通用注入 | 每个查询字符串参数 | 注入 payload 后是否在响应中检测到服务器错误（不进行特定 SQL/NoSQL 指纹识别） |
| 安全响应头 | 每个 URL 一次 | 响应中缺失或配置不当的安全响应头 |

前三类测试（通用参数/请求头/表单 fuzzing）是**无检测**的变异引擎 — 它们绝不会直接产生 `Finding`；仅统计在相应 `Test` 中遇到的 5xx 服务器错误。只有签名（XSS、注入、安全响应头）会生成 findings。

## 6. 评分与严重级别

每项检测到的异常按三个维度评分（`impact`、`exploitability`、`scope`，各 1 到 5 分），评分依据观察性质而定 — 映射刻意**保守**（取范围下限，在此自动阶段没有任何人工确认）：

| 原始分数（3 个维度之和） | 严重级别 |
|---|---|
| ≥ 13 | `critical` |
| ≥ 10 | `high` |
| ≥ 7 | `medium` |
| < 7 | `low` |

仍可手动调整（`severity_override`），但始终需要明确理由。等价 findings（相同类型、相同 endpoint、相同参数）会被去重，并保留最佳可用证据（置信度 `omega_lib.core.confidence.ConfidenceLevel`，若相同则比较原始分数）。

## 7. 认证

专用 YAML 文件（`--auth-config`），绝不在命令行中明文提供凭据：

| 模式 | 说明 |
|---|---|
| `none` | 无认证（默认） |
| `cookie` | 直接提供会话 cookie |
| `bearer_token` | `Authorization: Bearer ...` 令牌 |
| `login_form` | 通过表单认证（登录 URL、用户名/密码字段） |

## 8. 架构

Omega-Fuzz 按 **Clean Architecture** 组织（domain / application / infrastructure / interfaces / ports / core / app / plugins），与 `omega-` 系列模板保持一致（参见 `omega-check`/`omega-deep`/`omega-fold`），并在每次修改时由 `import-linter` 验证。完整细节见 **`docs/ARCHITECTURE.md`**。

简要概览：

```text
src/omega_fuzz/
├── domain/          纯业务逻辑（目标/范围、请求、测试、findings、配置、报告等）
├── application/     用例（commands/queries）和编排器（发现、扫描、报告、限制）
├── ports/           应用期望的契约（http_client、repositories、exporters 等）
├── infrastructure/  具体实现（httpx、BeautifulSoup、SQLite、Jinja2 导出器 — Textual 不在此层）
├── interfaces/      tui/（Textual）和 cli/（可脚本化），功能严格对等
├── plugins/         fuzzers 和签名（纯函数，绝不直接访问网络）
├── app/             组装（Container、composition root、生命周期）
└── core/            通用词汇、错误、常量
```

设计规则：

- `plugins/fuzzers/` 和 `plugins/signatures/`：构建测试计划（`Test` + `ScanRequest`）的纯函数，绝不使用 `HttpClient`。
- `infrastructure/network/`：执行网络操作（`httpx`、内存受限的流式处理），绝不作判断。
- `infrastructure/analyzers/`：读取已收到的响应，产生结构化 `Observation`，绝不重新计算评分。
- `interfaces/`：仅负责显示，不包含业务逻辑。

## 9. 导出

Markdown 和 HTML 报告会以“设置”中选择的语言（“导出语言”，默认为界面语言）生成；JSON 仍为数据格式，不作翻译。报告默认生成到 `var/exports/`（运行时路径锚定在项目目录，可用 `$OMEGA_FUZZ_VAR_DIR` 覆盖，也可在设置界面覆盖），或写到指定路径（`--output-dir`）。文件名为扁平结构，无子目录：`<preset>-<时间戳>.<扩展名>`（例如 `prod-safe-2026-09-01_14-30-22.html`）。

### JSON，事实来源

完整的报告结构（生效配置、统计信息、测试、findings），严格可 JSON 序列化。

### Markdown，紧凑的人类可读报告

可在终端外阅读，不含 ANSI 代码。

### HTML，独立 Web 报告

提供 5 种可选主题（CLI 中为 `--export-theme`，TUI 中为选择器）：`omega-base`、`omega-burn`、`omega-neon`、`light-basic`、`light-alt`。

## 10. 历史与收藏目标

每次扫描及其 findings 都会持久保存到 SQLite（`var/db/omega-fuzz.db`），可在 TUI 的历史界面查看。仅保存 `Scan` 和 `Finding` — 不保存完整生效配置或详细请求 — 因此该界面不支持重新执行、比较或再次导出（界面会说明这一点，而不是制造数据）。

“目标”界面保存收藏列表（标准化 URL，`var/targets.json`），可直接用于预填新扫描的“目标”字段。

## 11. 截图

命令面板（`Ctrl+P`）中的 **截图** 命令：默认将当前 TUI 界面保存为 SVG 到 `var/screenshots/`，可在设置界面覆盖（与导出目录相同）。设置中还提供专用清理功能。

## 12. 终端兼容性

TUI（Textual）会自动检测终端能力（模拟器、尺寸）并相应调整其结构样式表（`complete`/`standard`/`reduced`/`mono`），无需手动标志。CLI 始终保持纯文本，与终端无关。该策略由整个 `omega-` 系列共享（`omega-lib`、`terminal/policies.py`）。

### 按检测到的模拟器划分的配置

| 终端模拟器 | 初始配置 |
|---|---|
| Ghostty、Alacritty、WezTerm、Kitty | `complete` |
| Konsole、GNOME Terminal、Terminator、Xfce4 Terminal | `standard` |
| xterm、urxvt、现代 SSH | `reduced` |
| Linux TTY、旧版 SSH | `mono` |
| 未识别的模拟器 | `reduced`（默认回退） |

### 按终端尺寸划分的配置

| 最小尺寸（列 × 行） | 配置上限 |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| 更小 | `mono` |

最终采用的配置是两者中**更严格的一个**（模拟器和尺寸）— 可按 `r` 键实时刷新。

## 13. 测试

```bash
source .venv/bin/activate
lint-imports        # 验证 Dependency Rule（6 个契约）
pytest -q           # 344 个测试
ruff check src tests
mypy -p omega_fuzz
```

结构：`tests/unit/`（领域和应用，无真实 I/O）、`tests/integration/`（通过 `tmp_path` 使用真实文件系统、`pytest-httpserver` 模拟 HTTP 服务器、真实 SQLite 数据库、端到端 CLI）、`tests/tui/`（通过 `Pilot` 导航、结构化检查 — 不声称自动视觉验证）。

## 14. 超出范围

- JSON 请求体 fuzzing（代码存在，未接入 — 无 API schema 发现）
- `POST`/`PUT`/`DELETE` 表单 fuzzing（有意排除，存在写入风险）
- 未手动调用时的业务逻辑测试（IDOR、授权、流程）
- 多目标并行扫描
- 从历史重新执行、比较或导出
- 客户端 JavaScript 渲染
- Web 仪表板

---

> Omega-Fuzz — 发现范围，在明确防护下进行测试，绝不猜测未经确认的内容。
