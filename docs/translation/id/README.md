<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - Lisensi MIT (lihat berkas LICENSE) -->
<div align="center">
  <img src="../../assets/omega-fuzz.png" alt="Omega-Fuzz" width="384">
</div>

# 🗱 OMEGA-FUZZ

**Pemindai kerentanan**

> Dikembangkan oleh [kraynux](https://github.com/kraynux) untuk [Omega-Server](https://kraynux.snake-mackarel.ts.net)   

Halaman resmi: [OMEGA-FUZZ](https://kraynux.snake-mackarel.ts.net/omega-fuzz/) &nbsp; Tangkapan layar: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-fuzz/screenshots/)  

[![Lisensi: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Antarmuka](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

🌐 Antarmuka dan laporan ekspor tersedia dalam **17 bahasa** — lihat [Bahasa antarmuka](#bahasa-antarmuka).  
**Bahasa:**  
<img src="https://flagcdn.com/w20/fr.png" alt="Français" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)

**Omega-Fuzz** adalah aplikasi terminal lokal (TUI [Textual](https://github.com/Textualize/textual) + CLI yang dapat dijalankan sebagai skrip) yang melakukan penemuan dan pengujian keamanan web (fuzzing HTTP) pada lingkungan yang diotorisasi: lab, mirror pribadi, atau pengujian yang telah disetujui secara eksplisit.

Alat ini bagian dari rangkaian `omega-` dan dibangun dengan Clean Architecture — lihat `docs/ARCHITECTURE.md` untuk detail teknis lengkap.

## 1. Visi dan cakupan

### Apa yang dilakukan Omega-Fuzz

- Menemukan cakupan satu target dengan BFS yang dibatasi oleh scope eksplisit (skema, subdomain, jalur yang diizinkan/diblokir, kedalaman), tanpa pernah berjalan tanpa pengaman.
- Melakukan fuzzing generik terhadap parameter query string, header HTTP, dan formulir `GET` yang ditemukan pada setiap URL yang ditemukan, lalu memeriksa tiga kelompok signature: reflected XSS non-destruktif, injection generik (deteksi kesalahan dalam respons), serta security header yang hilang atau salah konfigurasi — lihat [§5](#5-pengujian-keamanan-yang-dijalankan).
- Menilai setiap anomali pada 3 sumbu (dampak, eksploitabilitas, cakupan) dan menurunkan severity (`low`/`medium`/`high`/`critical`), melakukan deduplikasi berdasarkan `(jenis, endpoint, parameter)` sambil menyimpan bukti terbaik — lihat [§6](#6-skor-dan-severity).
- Mendukung autentikasi (cookie, bearer token, formulir login) melalui berkas YAML khusus; kredensial tidak pernah diberikan sebagai teks biasa di baris perintah.
- Menampilkan hasil di TUI (Textual) atau CLI yang dapat dijalankan sebagai skrip, dengan tiga ekspor (JSON, Markdown, HTML dengan 5 tema).
- Menyimpan riwayat pemindaian dan findings secara persisten di SQLite, serta daftar target favorit yang dapat digunakan ulang.
- Memerlukan konfirmasi eksplisit (frasa ketat untuk kasus paling sensitif) sebelum pemindaian agresif, diperluas, atau dengan verifikasi TLS dinonaktifkan.

### Apa yang tidak dilakukan Omega-Fuzz

- Fuzzing body JSON — kode tersedia (`plugins/fuzzers/json_body_fuzzer.py`) tetapi belum dihubungkan (penemuan HTML/BFS tidak menghasilkan schema API JSON atau sumber templat yang dapat dipakai).
- Fuzzing formulir `POST`/`PUT`/`DELETE` — dikecualikan dari pipeline otomatis secara sengaja (risiko penulisan yang tidak diinginkan pada target); hanya formulir `GET` yang diuji.
- Pengujian logika bisnis (IDOR, kontrol otorisasi, pemutusan workflow) — kode tersedia (`plugins/logic_tests/`) tetapi tetap di luar pipeline otomatis, hanya dapat dipanggil terpisah dan tidak pernah dipicu oleh pemindaian standar.
- Pemindaian multi-target paralel — satu target per pemindaian.
- Replay, perbandingan, atau ekspor dari layar Riwayat — hanya `Scan` dan `Finding` yang disimpan (bukan konfigurasi efektif lengkap atau permintaan); replay atau ekspor ulang dari riwayat akan membuat data. Layar menjelaskan hal ini alih-alih menawarkan fitur secara diam-diam.
- Rendering JavaScript sisi klien (halaman diambil sebagaimana disajikan, tidak dijalankan di browser headless).
- Dashboard web.

## 2. Instalasi

### Prasyarat

- Python 3.10+
- Koneksi internet, untuk dependensi
- Untuk TUI: font [Nerd Font](https://www.nerdfonts.com/) terpasang di terminal, untuk ikon header — tanpa itu, karakter ditampilkan sebagai kotak kosong (batasan yang sama dengan emoji, tetapi jauh lebih umum tersedia bagi pengguna terminal). Ketiadaan font tidak memengaruhi fungsi; murni kosmetik.

### Instalasi

```bash
[ -d omega-fuzz ] && echo "ℹ️ Sudah diekstrak di sini, langkah dilewati." || tar -xzf omega-fuzz.tar.gz
cd omega-fuzz/
chmod +x install.sh
./install.sh
```

`install.sh`:

1. Membuat virtual environment `.venv` jika belum ada.
2. Menginstal dependensi (`vendor/omega-lib/` lalu `pip install -e .`; `pyproject.toml` tetap menjadi satu-satunya sumber kebenaran).
3. Menjadikan `omega-fuzz.sh` dan `install.sh` dapat dieksekusi.
4. Menambahkan alias `fuzz` ke `~/.bashrc` dan `~/.zshrc` (tanpa duplikasi jika sudah ada).

### Dependensi

Dideklarasikan di `pyproject.toml` (tanpa `requirements.txt`):

- `omega-lib`: pustaka bersama rangkaian alat (tema ekspor, deteksi terminal, `ConfidenceLevel`) — di-vendorisasi di `vendor/omega-lib/`
- `httpx`: permintaan HTTP asinkron (penemuan + fuzzing), streaming respons (tidak pernah menyimpan seluruh respons dalam memori, bahkan untuk berkas multi-GB yang disajikan target)
- `beautifulsoup4` + `lxml`: ekstraksi URL dan formulir HTML
- `jinja2`: templat untuk ekspor HTML
- `textual`: antarmuka TUI, tema, adaptasi otomatis ke terminal
- `pyyaml`: memuat berkas `--auth-config`
- Dependensi pengembangan (`pip install -e ".[dev]"`): `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-httpserver`, `ruff`, `mypy`, `import-linter`

## 3. Penggunaan

### Mode interaktif (TUI)

Direkomendasikan untuk penggunaan sehari-hari — dijalankan tanpa argumen:

```bash
./omega-fuzz.sh
```

jika alias telah dibuat, cukup ketik `fuzz` di terminal:

```bash
fuzz
```

Alur: layar awal (ditutup dengan tombol atau klik) → menu utama (Pindai / Target / Pengaturan / Riwayat / Bantuan) → memasukkan target (URL lengkap, skema `http://`/`https://` wajib), preset atau konfigurasi manual (scope + agresivitas), autentikasi opsional, verifikasi TLS, override batas → layar tinjauan (konfirmasi sederhana, atau frasa ketat `OUI-J-AI-L-AUTORISATION` untuk kasus sensitif) → pemindaian (indikator tak tentu, tombol **Hentikan** tersedia kapan pun) → hasil (findings, ekspor) → riwayat (detail pemindaian sebelumnya dan findings terkait) serta target favorit dari menu utama. Adaptasi terminal (warna, ukuran, degradasi struktural) terjadi otomatis.

#### Pintasan keyboard

| Tombol | Tindakan |
|---|---|
| `↑` / `↓` | Navigasi antar elemen layar |
| `Tab` / `Shift+Tab` | Navigasi antar kolom formulir |
| `Esc` | Kembali ke layar sebelumnya (konfirmasi keluar di layar awal) |
| `t` | Tema berikutnya (diterapkan langsung, tanpa konfirmasi) |
| `r` | Menyegarkan deteksi terminal |
| `a` | Menampilkan bantuan (tabel preset bawaan) |
| `q` | Keluar (dengan konfirmasi) |
| `Ctrl+P` | Palet perintah (Theme, Keluar, Tangkapan layar) |

### Bahasa antarmuka

Antarmuka tersedia dalam 17 bahasa: Prancis, Inggris, Spanyol, Portugis (Brasil), Italia, Jerman, Belanda, Polandia, Rusia, Mandarin Sederhana, Vietnam, Thailand, Indonesia, Jepang, Korea, Hindi, dan Arab. Bahasa dipilih di Pengaturan («Bahasa / Language») dan diterapkan setelah antarmuka dimulai ulang; variabel `OMEGA_FUZZ_LANG` (misalnya `OMEGA_FUZZ_LANG=en ./omega-fuzz.sh`) memaksa bahasa selama satu sesi. Saat dijalankan dari omega-suite, omega-fuzz menggunakan bahasa rangkaian alat tersebut. Pada konsol teks Linux (TTY), bahasa dengan tulisan non-Latin ditampilkan dalam bahasa Inggris selama sesi. Baris perintah tetap dalam bahasa Prancis.

### Mode skrip (CLI)

```bash
# Pemindaian dengan preset siap pakai
./omega-fuzz.sh scan --target https://example.com --preset prod-safe

# Kombinasi manual scope + agresivitas (tanpa preset)
./omega-fuzz.sh scan --target https://example.com --scope-profile standard --aggressiveness standard

# Dengan autentikasi (berkas YAML, tidak pernah kredensial teks biasa di baris perintah)
./omega-fuzz.sh scan --target https://example.com --preset staging-full --auth-config auth.yaml

# Dry-run: konfigurasi efektif dan rencana perkiraan, tidak ada permintaan dikirim
./omega-fuzz.sh scan --target https://example.com --preset prod-safe --dry-run

# Ekspor tertarget (folder, format, tema HTML)
./omega-fuzz.sh scan --target https://example.com --preset prod-safe \
    --output-dir ./rapports --format html --export-theme omega-neon
```

Opsi `scan`:

| Opsi | Default | Efek |
|---|---|---|
| `--target` | *(wajib)* | URL target, skema `http://`/`https://` wajib (tidak pernah dilengkapi otomatis) |
| `--preset` | — | Preset siap pakai (lihat [§4](#4-profil-scope-dan-preset)) |
| `--scope-profile` | — | Profil scope, dikombinasikan dengan `--aggressiveness`, tanpa `--preset` |
| `--aggressiveness` | — | Tingkat agresivitas, dikombinasikan dengan `--scope-profile`, tanpa `--preset` |
| `--auth-config` | — | Berkas YAML autentikasi |
| `--insecure-tls` | nonaktif | Menonaktifkan verifikasi TLS (memicu konfirmasi diperkuat) |
| `--max-duration` | *(dari profil)* | Mengganti durasi maksimum (detik) |
| `--max-requests` | *(dari profil)* | Mengganti jumlah permintaan maksimum |
| `--max-tests` | *(dari profil)* | Mengganti jumlah pengujian maksimum |
| `--max-concurrent` | *(dari profil)* | Mengganti konkurensi maksimum |
| `--dry-run` | nonaktif | Menampilkan konfigurasi efektif dan rencana perkiraan, tidak mengirim permintaan |
| `--output-dir` | `var/exports/` | Folder laporan ekspor, dinamai `<preset>-<timestamp>.<ekstensi>` (dapat diganti di Pengaturan) |
| `--format` | `all` | `json`, `markdown`, `html`, atau `all` |
| `--export-theme` | `omega-base` | Tema laporan HTML yang diekspor (tidak berpengaruh pada json/markdown) |

Tidak ada subperintah `history`/`show` di CLI: riwayat dan target favorit hanya dapat dilihat dari TUI.

Jika alias telah dibuat oleh `install.sh`, `fuzz scan ...` berfungsi dari mana saja di terminal, tanpa prefiks `./omega-fuzz.sh`.

## 4. Profil scope dan preset

### Profil scope

| Profil | Mode | Kedalaman maksimum | Pembatasan |
|---|---|---|---|
| `strict` | target tepat | 1 | Memblokir `/health`, `/ready`, `/metrics`, `/favicon.ico`, `/robots.txt` |
| `standard` | + subdomain | 2 | Memblokir subdomain statis umum, jalur teknis, dan aset (gambar/css/js/font) |
| `large` | + subdomain | 4 | Hanya memblokir jalur teknis dan aset (termasuk arsip/PDF) |
| `api` | target tepat | 3 | Membatasi `/api`, `/v1`, `/v2`; memblokir dokumentasi dan aset |
| `custom` | + subdomain | 3 | Tanpa pembatasan default — titik awal untuk konfigurasi manual |

Apa pun profil yang dipilih, daftar ekstensi biner/berkas besar (`.iso`, `.zip`, `.exe`, `.mp4`, dst.) **selalu** dikecualikan dari crawl dan fuzzing, bahkan pada `custom` — tautan ke berkas jenis ini tidak pernah diambil dengan permintaan HTTP nyata, agar folder unduhan tidak memperlambat pemindaian selama beberapa menit.

### Tingkat agresivitas

`doux` · `standard` · `agressif` · `violent` — masing-masing memiliki batas dasar sendiri (durasi, permintaan, pengujian, kedalaman, konkurensi), yang dapat diganti oleh preset bila ada.

### Preset siap pakai

| Preset | Scope | Agresivitas | Durasi maksimum | Permintaan maksimum | Pengujian maksimum | Kedalaman maksimum | Konfirmasi diperkuat |
|---|---|---|---|---|---|---|---|
| `prod-safe` | strict | doux | 300 detik | 1.000 | 500 | 1 | tidak |
| `staging-full` | standard | standard | 1.800 detik | 20.000 | 10.000 | 2 | tidak |
| `lab-deep` | large | agressif | 3.600 detik | 100.000 | 50.000 | 4 | tidak |
| `lab-extreme` | large | violent | 7.200 detik | 500.000 | 250.000 | 5 | **ya** |
| `api-hardened` | api | agressif | 1.800 detik | 50.000 | 25.000 | 3 | tidak |

Pemindaian diblokir sampai dikonfirmasi. Konfirmasi **diperkuat** (mengetik frasa persis `OUI-J-AI-L-AUTORISATION`) diperlukan bila salah satu dari tiga faktor ini ada: agresivitas `violent`, preset `lab-extreme`, atau verifikasi TLS dinonaktifkan (`--insecure-tls`) — untuk kombinasi tidak biasa tanpa salah satu dari tiga faktor ini, konfirmasi sederhana ya/tidak.

## 5. Pengujian keamanan yang dijalankan

Pipeline otomatis, pada setiap URL yang ditemukan dalam scope (dan setiap formulir `GET` yang ditemukan di sana):

| Pengujian | Pemicu | Yang diperiksa |
|---|---|---|
| Fuzzing parameter generik | setiap parameter query string | Perilaku target terhadap nilai batas/malformed |
| Fuzzing header | sekali per URL, 4 header tetap (`User-Agent`, `Referer`, `X-Forwarded-For`, `Accept-Language`) | Perilaku target terhadap nilai batas/malformed pada header |
| Fuzzing formulir (hanya `GET`) | setiap kolom formulir `GET` yang ditemukan dalam scope | Perilaku target terhadap nilai batas/malformed pada kolom formulir |
| Reflected XSS | setiap parameter query string | Refleksi payload yang tidak difilter dalam respons (non-destruktif) |
| Injection generik | setiap parameter query string | Deteksi kesalahan server dalam respons terhadap payload injection (tanpa fingerprint SQL/NoSQL spesifik) |
| Security headers | sekali per URL | Security header yang hilang atau salah konfigurasi dalam respons |

Tiga pengujian pertama (fuzzing parameter/header/formulir generik) adalah mesin mutasi **tanpa deteksi** — tidak pernah menghasilkan `Finding` secara langsung; hanya kesalahan server (5xx) yang ditemui yang dihitung pada `Test` terkait. Hanya signature (XSS, injection, security headers) yang menghasilkan findings.

## 6. Skor dan severity

Setiap anomali yang terdeteksi dinilai pada 3 sumbu (`impact`, `exploitability`, `scope`, masing-masing 1–5) sesuai sifat pengamatan — pemetaan sengaja **konservatif** (bagian bawah rentang, tanpa konfirmasi manusia pada tahap otomatis ini):

| Skor mentah (jumlah 3 sumbu) | Severity |
|---|---|
| ≥ 13 | `critical` |
| ≥ 10 | `high` |
| ≥ 7 | `medium` |
| < 7 | `low` |

Penyesuaian manual (`severity_override`) tetap memungkinkan tetapi selalu memerlukan justifikasi eksplisit. Findings yang setara (jenis, endpoint, dan parameter sama) dideduplikasi dengan menyimpan bukti terbaik yang tersedia (tingkat keyakinan `omega_lib.core.confidence.ConfidenceLevel`, lalu skor mentah bila seri).

## 7. Autentikasi

Berkas YAML khusus (`--auth-config`), tidak pernah kredensial teks biasa di baris perintah:

| Mode | Efek |
|---|---|
| `none` | Tanpa autentikasi (default) |
| `cookie` | Cookie sesi diberikan langsung |
| `bearer_token` | Token `Authorization: Bearer ...` |
| `login_form` | Autentikasi melalui formulir (URL login, kolom pengguna/kata sandi) |

## 8. Arsitektur

Omega-Fuzz disusun dalam **Clean Architecture** (domain / application / infrastructure / interfaces / ports / core / app / plugins), selaras dengan templat rangkaian `omega-` (lihat `omega-check`/`omega-deep`/`omega-fold`) dan diverifikasi oleh `import-linter` pada setiap perubahan. Detail lengkap ada di **`docs/ARCHITECTURE.md`**.

Gambaran singkat:

```text
src/omega_fuzz/
├── domain/          Logika bisnis murni (target/scope, permintaan, pengujian, findings, profil, laporan...)
├── application/     Use case (commands/queries) dan orkestrator (penemuan, pemindaian, laporan, batas)
├── ports/           Kontrak yang diharapkan aplikasi (http_client, repositories, exporters...)
├── infrastructure/  Implementasi konkret (httpx, BeautifulSoup, SQLite, exporter Jinja2 — Textual TIDAK di sini)
├── interfaces/      tui/ (Textual) dan cli/ (dapat dijalankan sebagai skrip), paritas fungsional ketat
├── plugins/         Fuzzer dan signature (fungsi murni, tidak pernah akses jaringan langsung)
├── app/             Perakitan (Container, composition root, siklus hidup)
└── core/            Kosakata lintas, kesalahan, konstanta
```

Aturan desain:

- `plugins/fuzzers/` dan `plugins/signatures/`: fungsi murni yang membuat rencana pengujian (`Test` + `ScanRequest`), tidak pernah menyentuh `HttpClient`.
- `infrastructure/network/`: melakukan operasi jaringan (`httpx`, streaming dengan batas memori), tidak pernah menilai.
- `infrastructure/analyzers/`: membaca respons yang sudah diterima, menghasilkan `Observation` terstruktur, tidak pernah menghitung ulang skor.
- `interfaces/`: menampilkan, tidak memuat logika bisnis.

## 9. Ekspor

Laporan Markdown dan HTML ditulis dalam bahasa yang dipilih di Pengaturan («Bahasa ekspor», default bahasa antarmuka); JSON tetap berupa data dan tidak diterjemahkan. Laporan dibuat secara default di `var/exports/` (jalur runtime dikaitkan dengan folder proyek, `$OMEGA_FUZZ_VAR_DIR` untuk menggantinya, juga dapat diganti di layar Pengaturan), atau pada jalur yang ditentukan (`--output-dir`). Nama berkas datar, tanpa subfolder: `<preset>-<timestamp>.<ekstensi>` (misalnya `prod-safe-2026-09-01_14-30-22.html`).

### JSON, sumber kebenaran

Struktur laporan lengkap (konfigurasi efektif, statistik, pengujian, findings), dapat diserialisasi ke JSON secara ketat.

### Markdown, laporan ringkas untuk manusia

Dapat dibaca di luar terminal, tanpa kode ANSI.

### HTML, laporan web mandiri

5 tema pilihan (`--export-theme` di CLI, pemilih di TUI): `omega-base`, `omega-burn`, `omega-neon`, `light-basic`, `light-alt`.

## 10. Riwayat dan target favorit

Setiap pemindaian disimpan (SQLite, `var/db/omega-fuzz.db`) bersama findings-nya dan dapat dilihat dari layar Riwayat di TUI. Hanya `Scan` dan `Finding` yang disimpan — bukan konfigurasi efektif lengkap atau permintaan terperinci — sehingga tidak ada replay, perbandingan, atau ekspor ulang dari layar ini (layar menjelaskannya alih-alih membuat data).

Layar **Target** menyimpan daftar favorit (URL ternormalisasi, `var/targets.json`), dapat digunakan ulang untuk mengisi langsung kolom Target pemindaian baru.

## 11. Tangkapan layar

Perintah **Tangkapan layar** dari palet (`Ctrl+P`): menyimpan SVG layar TUI saat ini secara default ke `var/screenshots/`, dapat diganti di layar Pengaturan (seperti folder ekspor). Pembersihan khusus tersedia di Pengaturan.

## 12. Kompatibilitas terminal

TUI (Textual) mendeteksi kemampuan terminal secara otomatis (emulator, ukuran) dan menyesuaikan stylesheet strukturalnya (`complete`/`standard`/`reduced`/`mono`), tanpa flag manual. CLI selalu berupa teks biasa, independen dari terminal. Kebijakan ini dipakai bersama oleh seluruh rangkaian `omega-` (`omega-lib`, `terminal/policies.py`).

### Profil berdasarkan emulator yang terdeteksi

| Emulator | Profil awal |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | `complete` |
| Konsole, GNOME Terminal, Terminator, Xfce4 Terminal | `standard` |
| xterm, urxvt, SSH modern | `reduced` |
| TTY Linux, SSH lama | `mono` |
| Emulator tidak dikenali | `reduced` (fallback default) |

### Profil berdasarkan ukuran terminal

| Ukuran minimum (kolom × baris) | Batas profil |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| di bawahnya | `mono` |

Profil akhir adalah **yang paling membatasi dari keduanya** (emulator dan ukuran) — dapat disegarkan langsung dengan tombol `r`.

## 13. Pengujian

```bash
source .venv/bin/activate
lint-imports        # memverifikasi Dependency Rule (6 kontrak)
pytest -q           # 344 pengujian
ruff check src tests
mypy -p omega_fuzz
```

Struktur: `tests/unit/` (domain dan application, tanpa I/O nyata), `tests/integration/` (filesystem nyata melalui `tmp_path`, server HTTP palsu `pytest-httpserver`, basis data SQLite nyata, CLI end-to-end), `tests/tui/` (navigasi melalui `Pilot`, pemeriksaan struktural — bukan klaim verifikasi visual otomatis).

## 14. Di luar cakupan

- Fuzzing body JSON (kode ada, belum dihubungkan — tidak ada penemuan schema API)
- Fuzzing formulir `POST`/`PUT`/`DELETE` (dikecualikan secara sengaja, risiko penulisan)
- Pengujian logika bisnis (IDOR, otorisasi, workflow) di luar pemanggilan manual
- Pemindaian multi-target simultan
- Replay, perbandingan, atau ekspor dari riwayat
- Rendering JavaScript sisi klien
- Dashboard web

---

> Omega-Fuzz — Temukan cakupan, uji dengan pengaman eksplisit, dan jangan pernah menebak apa yang belum dikonfirmasi.
