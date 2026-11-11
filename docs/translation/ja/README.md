<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - MITライセンス（LICENSEファイルを参照） -->
<div align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/assets/omega-fuzz.png" alt="Omega-Fuzz" width="512">
</div>

# 🗱 OMEGA-FUZZ

**脆弱性スキャナー**

> [kraynux](https://github.com/kraynux) が [Omega-Server](https://kraynux.snake-mackarel.ts.net) 向けに開発   

公式ページ: [OMEGA-FUZZ](https://kraynux.snake-mackarel.ts.net/omega-fuzz/) &nbsp; スクリーンショット: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-fuzz/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

🌐 インターフェイスとエクスポートされるレポートは **17言語** で利用できます — [インターフェイスの言語](#インターフェイスの言語) を参照してください。  
**言語：**  
<img src="https://flagcdn.com/w20/fr.png" alt="Français" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)

**Omega-Fuzz** は、許可された環境（ラボ、個人用ミラー、明示的に同意されたテスト）で、Webセキュリティの発見とテスト（HTTPファジング）を行うローカルのターミナルアプリケーションです（[Textual](https://github.com/Textualize/textual) ベースのTUI + スクリプト化可能なCLI）。

本ツールは `omega-` スイートの一部であり、Clean Architectureで構成されています。技術的な詳細は `docs/ARCHITECTURE.md` を参照してください。

## 1. ビジョンと対象範囲

### Omega-Fuzzが行うこと

- 明示的なスコープ（スキーム、サブドメイン、許可/拒否パス、深さ）で制限されたBFSにより、単一ターゲットの対象範囲を発見します。保護措置なしで実行されることはありません。
- 発見された各URLで見つかったクエリ文字列パラメータ、HTTPヘッダー、`GET` フォームに対して汎用ファジングを行い、3種類のシグネチャを検証します：非破壊的な反射型XSS、汎用インジェクション（レスポンス内のエラー検出）、欠落または誤設定のセキュリティヘッダー — [§5](#5-実行されるセキュリティテスト) を参照。
- 各異常を3軸（影響、悪用可能性、範囲）で採点し、`low`/`medium`/`high`/`critical` の重大度を導出します。`(種別, エンドポイント, パラメータ)` で重複を排除し、最良の証拠を保持します — [§6](#6-スコアと重大度) を参照。
- 専用のYAMLファイルによる認証（Cookie、Bearerトークン、ログインフォーム）をサポートします。認証情報がコマンドラインに平文で渡されることはありません。
- 結果をTUI（Textual）またはスクリプト化可能なCLIで表示し、JSON、Markdown、HTML（5テーマ）の3形式でエクスポートします。
- スキャン履歴とfindingsをSQLiteに永続化し、再利用可能なお気に入りターゲットの一覧も保持します。
- 攻撃的なスキャン、拡張スキャン、またはTLS検証を無効化したスキャンの前に、明示的な確認（最も機微なケースでは正確なフレーズ）を要求します。

### Omega-Fuzzが行わないこと

- JSONボディのファジング — コードは存在します（`plugins/fuzzers/json_body_fuzzer.py`）が、接続されていません（HTML/BFSによる発見はJSON APIスキーマや利用可能なテンプレートソースを生成しません）。
- `POST`/`PUT`/`DELETE` フォームのファジング — 自動パイプラインから意図的に除外されています（ターゲットへの意図しない書き込みのリスク）。テストされるのは `GET` フォームのみです。
- ビジネスロジックのテスト（IDOR、認可制御、ワークフローの破壊）— コードは存在します（`plugins/logic_tests/`）が、自動パイプラインの外にあり、個別に呼び出す場合のみ利用でき、標準スキャンによって決して起動されません。
- 複数ターゲットの並列スキャン — 1スキャンにつき1ターゲットです。
- 履歴画面からの再実行、比較、エクスポート — 永続化されるのは `Scan` と `Finding` のみです（完全な実効設定やリクエストは保存されません）。履歴からの再実行や再エクスポートはデータを作り出すことになるため、画面はその旨を説明します。
- クライアント側JavaScriptのレンダリング — ページはサーバーが提供した通りの形式で取得され、headlessブラウザで実行されません。
- Webダッシュボード。

## 2. インストール

### 前提条件

- Python 3.10以上
- 依存関係のインストールのためのインターネット接続
- TUI用：ヘッダーアイコンを表示するため、ターミナルに [Nerd Font](https://www.nerdfonts.com/) がインストールされている必要があります。ない場合、その文字は空の四角として表示されます（絵文字と同じ制限ですが、ターミナルユーザーにはより広く普及しています）。フォントがなくても動作には影響せず、外観上の問題のみです。

### インストール

```bash
[ -d omega-fuzz ] && echo "ℹ️ ここで既に展開済みです。この手順をスキップします。" || tar -xzf omega-fuzz.tar.gz
cd omega-fuzz/
chmod +x install.sh
./install.sh
```

`install.sh` の処理：

1. `.venv` 仮想環境が存在しない場合に作成します。
2. 依存関係をインストールします（`vendor/omega-lib/`、次に `pip install -e .`。`pyproject.toml` が唯一の信頼できる情報源です）。
3. `omega-fuzz.sh` と `install.sh` を実行可能にします。
4. `~/.bashrc` と `~/.zshrc` に `fuzz` エイリアスを追加します（既にある場合は重複しません）。

### 依存関係

`pyproject.toml` で宣言されています（`requirements.txt` はありません）：

- `omega-lib`：スイート共通ライブラリ（エクスポートテーマ、ターミナル検出、`ConfidenceLevel`）— `vendor/omega-lib/` に同梱
- `httpx`：非同期HTTPリクエスト（発見 + ファジング）、レスポンスのストリーミング（ターゲットが提供する複数GBのファイルでも、レスポンス全体をメモリにバッファリングしません）
- `beautifulsoup4` + `lxml`：URLとHTMLフォームの抽出
- `jinja2`：HTMLエクスポートのテンプレート
- `textual`：TUIインターフェイス、テーマ、ターミナルへの自動適応
- `pyyaml`：`--auth-config` ファイルの読み込み
- 開発用依存関係（`pip install -e ".[dev]"`）：`pytest`、`pytest-asyncio`、`pytest-cov`、`pytest-httpserver`、`ruff`、`mypy`、`import-linter`

## 3. 使い方

### 対話モード（TUI）

日常利用に推奨されます — 引数なしで起動します：

```bash
./omega-fuzz.sh
```

エイリアスを作成済みであれば、ターミナルで `fuzz` と入力するだけです：

```bash
fuzz
```

流れ：スタート画面（キー操作またはクリックで閉じる）→ メインメニュー（スキャン / ターゲット / 設定 / 履歴 / ヘルプ）→ ターゲット入力（完全なURL、`http://`/`https://` スキームが必須）、プリセットまたは手動設定（スコープ + 攻撃性）、任意の認証、TLS検証、制限の上書き → 確認画面（通常は簡単な確認、機微なケースでは正確なフレーズ `OUI-J-AI-L-AUTORISATION`）→ スキャン（不確定プログレス、いつでも **停止** ボタンが利用可能）→ 結果（findings、エクスポート）→ 履歴（過去のスキャンの詳細と関連するfindings）、およびメインメニューからのお気に入りターゲット。ターミナルへの適応（色、サイズ、構造の段階的縮小）は自動です。

#### キーボードショートカット

| キー | 操作 |
|---|---|
| `↑` / `↓` | 画面内の要素間を移動 |
| `Tab` / `Shift+Tab` | フォームのフィールド間を移動 |
| `Esc` | 前の画面へ戻る（スタート画面では終了確認） |
| `t` | 次のテーマ（確認なしで即時適用） |
| `r` | ターミナル検出を更新 |
| `a` | ヘルプを表示（同梱プリセットの一覧） |
| `q` | 終了（確認あり） |
| `Ctrl+P` | コマンドパレット（Theme、終了、スクリーンショット） |

### インターフェイスの言語

インターフェイスは17言語で利用できます：フランス語、英語、スペイン語、ポルトガル語（ブラジル）、イタリア語、ドイツ語、オランダ語、ポーランド語、ロシア語、簡体字中国語、ベトナム語、タイ語、インドネシア語、日本語、韓国語、ヒンディー語、アラビア語。言語は設定画面（「言語 / Language」）で選択し、インターフェイスの再起動後に適用されます。環境変数 `OMEGA_FUZZ_LANG`（例：`OMEGA_FUZZ_LANG=en ./omega-fuzz.sh`）でセッション単位の言語を強制できます。omega-suiteから起動した場合、omega-fuzzはスイートの言語を使用します。Linuxのテキストコンソール（TTY）では、非ラテン文字の言語はセッション中は英語で表示されます。コマンドラインはフランス語のままです。

### お問い合わせとサポート

ヘルプ（`a` キー）には **お問い合わせとサポート** 画面があります：*コーヒーをおごる*（開発者の PayPal ページ）、*サポートに連絡*（メールアドレスとサイトのお問い合わせフォームをそのまま表示）、*ユーザーとして登録（匿名）*、*更新を確認*。 登録は任意で、既定では無効、送信は一度だけです。利用者の数と、希望すればその大陸または国（選択式のリストのみ、自由入力なし）を数えるためだけに使われます。送信されるのは、ランダムに生成したキー、ソフトウェア名（`omega-fuzz`）とそのバージョンだけで、名前、マシン名、設定、対象、結果は決して送信されません。IP アドレスは登録データには保存されませんが、通常のアクセスと同様に、受信サーバーのセキュリティチェックとログを通過します。 同じ画面からいつでも取り消せます（*登録を取り消す*）。 更新の確認は、サイトで公開されているバージョンの一覧を読むだけで、クリックしない限り行われません。

### スクリプトモード（CLI）

```bash
# 用意されたプリセットでスキャン
./omega-fuzz.sh scan --target https://example.com --preset prod-safe

# スコープと攻撃性を手動で組み合わせる（プリセットなし）
./omega-fuzz.sh scan --target https://example.com --scope-profile standard --aggressiveness standard

# 認証付き（YAMLファイル。認証情報をコマンドラインに平文で渡しません）
./omega-fuzz.sh scan --target https://example.com --preset staging-full --auth-config auth.yaml

# Dry-run：実効設定と推定プランを表示し、リクエストは送信しません
./omega-fuzz.sh scan --target https://example.com --preset prod-safe --dry-run

# エクスポート先を指定（フォルダ、形式、HTMLテーマ）
./omega-fuzz.sh scan --target https://example.com --preset prod-safe \
    --output-dir ./rapports --format html --export-theme omega-neon
```

`scan` のオプション：

| オプション | 既定値 | 効果 |
|---|---|---|
| `--target` | *（必須）* | 対象URL。`http://`/`https://` スキームが必須（自動補完されません） |
| `--preset` | — | 用意されたプリセット（[§4](#4-スコーププロファイルとプリセット) を参照） |
| `--scope-profile` | — | スコーププロファイル。`--aggressiveness` と組み合わせ、`--preset` とは併用しません |
| `--aggressiveness` | — | 攻撃性レベル。`--scope-profile` と組み合わせ、`--preset` とは併用しません |
| `--auth-config` | — | 認証用YAMLファイル |
| `--insecure-tls` | 無効 | TLS検証を無効化します（強化確認をトリガーします） |
| `--max-duration` | *（プロファイル値）* | 最大実行時間（秒）を上書きします |
| `--max-requests` | *（プロファイル値）* | 最大リクエスト数を上書きします |
| `--max-tests` | *（プロファイル値）* | 最大テスト数を上書きします |
| `--max-concurrent` | *（プロファイル値）* | 最大同時実行数を上書きします |
| `--dry-run` | 無効 | 実効設定と推定プランを表示し、リクエストを送信しません |
| `--output-dir` | `var/exports/` | エクスポートされるレポートのフォルダ。名前は `<preset>-<タイムスタンプ>.<拡張子>`（設定画面で上書き可能） |
| `--format` | `all` | `json`、`markdown`、`html`、または `all` |
| `--export-theme` | `omega-base` | エクスポートされるHTMLレポートのテーマ（json/markdownには影響しません） |

CLIには `history`/`show` サブコマンドはありません：履歴とお気に入りターゲットはTUIからのみ参照できます。

`install.sh` によってエイリアスが作成されている場合、`fuzz scan ...` は `./omega-fuzz.sh` の接頭辞なしでターミナルのどこからでも実行できます。

## 4. スコーププロファイルとプリセット

### スコーププロファイル

| プロファイル | モード | 最大深度 | 制限 |
|---|---|---|---|
| `strict` | 正確なターゲット | 1 | `/health`、`/ready`、`/metrics`、`/favicon.ico`、`/robots.txt` をブロック |
| `standard` | + サブドメイン | 2 | 一般的な静的サブドメイン、技術的パス、アセット（画像/css/js/フォント）をブロック |
| `large` | + サブドメイン | 4 | 技術的パスとアセット（アーカイブ/PDFを含む）のみブロック |
| `api` | 正確なターゲット | 3 | `/api`、`/v1`、`/v2` に制限。ドキュメントとアセットをブロック |
| `custom` | + サブドメイン | 3 | 既定の制限なし — 手動設定の出発点 |

選択したプロファイルに関わらず、バイナリ/大容量ファイルの拡張子一覧（`.iso`、`.zip`、`.exe`、`.mp4` など）は、`custom` であっても **常に** クロールとファジングから除外されます。この種のファイルへのリンクは実際のHTTPリクエストでは取得されません。ダウンロードフォルダがスキャンを長時間遅延させるのを防ぐためです。

### 攻撃性レベル

`doux` · `standard` · `agressif` · `violent` — 各レベルには固有の基本制限（時間、リクエスト数、テスト数、深さ、同時実行数）があり、プリセットが指定されていればそれが上書きします。

### 用意されたプリセット

| プリセット | スコープ | 攻撃性 | 最大時間 | 最大リクエスト | 最大テスト | 最大深度 | 強化確認 |
|---|---|---|---|---|---|---|---|
| `prod-safe` | strict | doux | 300秒 | 1,000 | 500 | 1 | なし |
| `staging-full` | standard | standard | 1,800秒 | 20,000 | 10,000 | 2 | なし |
| `lab-deep` | large | agressif | 3,600秒 | 100,000 | 50,000 | 4 | なし |
| `lab-extreme` | large | violent | 7,200秒 | 500,000 | 250,000 | 5 | **あり** |
| `api-hardened` | api | agressif | 1,800秒 | 50,000 | 25,000 | 3 | なし |

スキャンは確認されるまでブロックされます。**強化確認**（正確なフレーズ `OUI-J-AI-L-AUTORISATION` の入力）は、次の3要素のいずれかが存在する場合に必要です：攻撃性 `violent`、プリセット `lab-extreme`、TLS検証の無効化（`--insecure-tls`）。これら3要素のいずれも含まない通常とは異なる組み合わせでは、単純なはい/いいえの確認で十分です。

## 5. 実行されるセキュリティテスト

スコープ内で発見された各URL（およびそこで見つかった各 `GET` フォーム）に対する自動パイプラインです：

| テスト | 実行条件 | 検証内容 |
|---|---|---|
| 汎用パラメータファジング | すべてのクエリ文字列パラメータ | 境界値/不正形式の値に対するターゲットの挙動 |
| ヘッダーファジング | URLごとに1回、4つの固定ヘッダー（`User-Agent`、`Referer`、`X-Forwarded-For`、`Accept-Language`） | ヘッダー内の境界値/不正形式の値に対するターゲットの挙動 |
| フォームファジング（`GET` のみ） | スコープ内で発見されたすべての `GET` フォームフィールド | フォームフィールド内の境界値/不正形式の値に対するターゲットの挙動 |
| 反射型XSS | すべてのクエリ文字列パラメータ | レスポンス内でのペイロードの未フィルタ反射（非破壊的） |
| 汎用インジェクション | すべてのクエリ文字列パラメータ | インジェクションペイロードに対するレスポンス内のサーバーエラー検出（特定のSQL/NoSQLフィンガープリントは行いません） |
| セキュリティヘッダー | URLごとに1回 | レスポンス内の欠落または誤設定のセキュリティヘッダー |

最初の3つのテスト（汎用パラメータ/ヘッダー/フォームファジング）は **検出なし** の変異エンジンです — 直接 `Finding` を生成することはありません。遭遇したサーバーエラー（5xx）のみが対応する `Test` にカウントされます。findingsを生成するのはシグネチャ（XSS、インジェクション、セキュリティヘッダー）のみです。

## 6. スコアと重大度

検出された各異常は、観測内容に応じて3軸（`impact`、`exploitability`、`scope`、各1〜5）で採点されます。マッピングは意図的に **保守的** です（レンジの下限、この自動段階では人間による確認はありません）：

| 生スコア（3軸の合計） | 重大度 |
|---|---|
| ≥ 13 | `critical` |
| ≥ 10 | `high` |
| ≥ 7 | `medium` |
| < 7 | `low` |

手動調整（`severity_override`）は可能ですが、常に明示的な根拠が必要です。等価なfindings（同じ種別、同じエンドポイント、同じパラメータ）は重複排除され、利用可能な最良の証拠が保持されます（信頼度 `omega_lib.core.confidence.ConfidenceLevel`、同点の場合は生スコア）。

## 7. 認証

専用のYAMLファイル（`--auth-config`）。認証情報をコマンドラインに平文で渡すことはありません：

| モード | 効果 |
|---|---|
| `none` | 認証なし（既定） |
| `cookie` | セッションCookieを直接提供 |
| `bearer_token` | `Authorization: Bearer ...` トークン |
| `login_form` | フォームによる認証（ログインURL、ユーザー/パスワードフィールド） |

## 8. アーキテクチャ

Omega-Fuzzは **Clean Architecture**（domain / application / infrastructure / interfaces / ports / core / app / plugins）で構成され、`omega-` スイートのテンプレート（`omega-check`/`omega-deep`/`omega-fold` を参照）に沿い、変更のたびに `import-linter` で検証されます。詳細は **`docs/ARCHITECTURE.md`** にあります。

非常に短い概要：

```text
src/omega_fuzz/
├── domain/          純粋なドメインロジック（ターゲット/スコープ、リクエスト、テスト、findings、プロファイル、レポートなど）
├── application/     ユースケース（commands/queries）とオーケストレーター（発見、スキャン、レポート、制限）
├── ports/           アプリケーションが期待する契約（http_client、repositories、exporters など）
├── infrastructure/  具体的な実装（httpx、BeautifulSoup、SQLite、Jinja2エクスポーター — Textualはここにはありません）
├── interfaces/      tui/（Textual）と cli/（スクリプト化可能）、機能的に厳密に対等
├── plugins/         ファザーとシグネチャ（純粋関数、ネットワークへ直接アクセスしない）
├── app/             組み立て（Container、composition root、ライフサイクル）
└── core/            横断的な語彙、エラー、定数
```

設計ルール：

- `plugins/fuzzers/` と `plugins/signatures/`：テストプラン（`Test` + `ScanRequest`）を構築する純粋関数であり、`HttpClient` には決して触れません。
- `infrastructure/network/`：ネットワーク処理を行います（`httpx`、メモリ制限付きストリーミング）。判断は行いません。
- `infrastructure/analyzers/`：既に受信したレスポンスを読み、構造化された `Observation` を生成します。スコアを再計算しません。
- `interfaces/`：表示のみを行い、ビジネスロジックを含みません。

## 9. エクスポート

MarkdownおよびHTMLレポートは、設定画面で選択した言語（「エクスポートの言語」、既定はインターフェイスの言語）で出力されます。JSONはデータのままであり、翻訳されません。レポートは既定で `var/exports/` に生成されます（実行時パスはプロジェクトフォルダに固定され、`$OMEGA_FUZZ_VAR_DIR` で上書き可能、設定画面からも上書きできます）。または指定したパス（`--output-dir`）に出力されます。ファイル名はフラットでサブフォルダなしです：`<preset>-<タイムスタンプ>.<拡張子>`（例：`prod-safe-2026-09-01_14-30-22.html`）。

### JSON、信頼できる情報源

レポートの完全な構造（実効設定、統計、テスト、findings）。厳密にJSONシリアライズ可能です。

### Markdown、人間向けのコンパクトなレポート

ターミナル外でも読め、ANSIコードを含みません。

### HTML、自己完結型のWebレポート

5つのテーマから選択できます（CLIでは `--export-theme`、TUIではセレクター）：`omega-base`、`omega-burn`、`omega-neon`、`light-basic`、`light-alt`。

## 10. 履歴とお気に入りターゲット

各スキャンはfindingsとともにSQLite（`var/db/omega-fuzz.db`）に永続化され、TUIの履歴画面から参照できます。保存されるのは `Scan` と `Finding` のみです — 完全な実効設定や詳細なリクエストは保存されません — ため、この画面からは再実行、比較、再エクスポートはできません（画面はその旨を説明し、データを作り出しません）。

**ターゲット** 画面はお気に入りの一覧（正規化されたURL、`var/targets.json`）を保持し、新しいスキャンのターゲット欄を直接埋めるために再利用できます。

## 11. スクリーンショット

コマンドパレット（`Ctrl+P`）の **スクリーンショット** コマンド：現在のTUI画面のSVGを既定で `var/screenshots/` に保存します。設定画面で上書き可能です（エクスポートフォルダと同様）。設定画面には専用の削除機能もあります。

## 12. ターミナル互換性

TUI（Textual）はターミナルの能力（エミュレーター、サイズ）を自動検出し、それに応じて構造的なスタイルシート（`complete`/`standard`/`reduced`/`mono`）を調整します。手動フラグは不要です。CLIは常にプレーンテキストで、ターミナルに依存しません。このポリシーは `omega-` スイート全体で共有されています（`omega-lib`、`terminal/policies.py`）。

### 検出されたエミュレーターによるプロファイル

| エミュレーター | 初期プロファイル |
|---|---|
| Ghostty、Alacritty、WezTerm、Kitty | `complete` |
| Konsole、GNOME Terminal、Terminator、Xfce4 Terminal | `standard` |
| xterm、urxvt、モダンなSSH | `reduced` |
| Linux TTY、レガシーSSH | `mono` |
| 未認識のエミュレーター | `reduced`（既定のフォールバック） |

### ターミナルサイズによるプロファイル

| 最小サイズ（列 × 行） | プロファイル上限 |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| それ未満 | `mono` |

最終的なプロファイルは、両者のうち **より制限的な方**（エミュレーターとサイズ）です。`r` キーでリアルタイムに更新できます。

## 13. テスト

```bash
source .venv/bin/activate
lint-imports        # Dependency Rule（6契約）を検証
pytest -q           # 344テスト
ruff check src tests
mypy -p omega_fuzz
```

構成：`tests/unit/`（ドメインとアプリケーション、実際のI/Oなし）、`tests/integration/`（`tmp_path` による実際のファイルシステム、`pytest-httpserver` の偽HTTPサーバー、実際のSQLiteデータベース、エンドツーエンドのCLI）、`tests/tui/`（`Pilot` によるナビゲーション、構造的な検証 — 自動視覚検証を主張するものではありません）。

## 14. 対象外

- JSONボディのファジング（コードは存在するが未接続 — APIスキーマの発見なし）
- `POST`/`PUT`/`DELETE` フォームのファジング（意図的に除外、書き込みリスク）
- 手動呼び出し以外のビジネスロジックテスト（IDOR、認可、ワークフロー）
- 複数ターゲットの同時スキャン
- 履歴からの再実行、比較、エクスポート
- クライアント側JavaScriptのレンダリング
- Webダッシュボード

---

> Omega-Fuzz — 対象範囲を発見し、明示的な保護措置のもとでテストし、確認されていないことを推測しません。

<p align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/ja/omega-fuzz/A.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/ja/omega-fuzz/B.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/ja/omega-fuzz/C.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/ja/omega-fuzz/D.png" width="24%" />
</p>
