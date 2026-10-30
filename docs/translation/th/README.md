<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - สัญญาอนุญาต MIT (ดูไฟล์ LICENSE) -->
<div align="center">
  <img src="../../assets/omega-fuzz.png" alt="Omega-Fuzz" width="384">
</div>

# 🗱 OMEGA-FUZZ

**ตัวสแกนช่องโหว่**

> พัฒนาโดย **kraynux** สำหรับ **Omega-server**  
> [https://kraynux.snake-mackarel.ts.net](https://kraynux.snake-mackarel.ts.net)

หน้าทางการ: [OMEGA-FUZZ](https://kraynux.snake-mackarel.ts.net/omega-fuzz/) &nbsp; ภาพหน้าจอ: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-fuzz/screenshots/)  

[![สัญญาอนุญาต: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![แพลตฟอร์ม](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![อินเทอร์เฟซ](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

🌐 อินเทอร์เฟซและรายงานที่ส่งออกรองรับ **17 ภาษา** — ดู [ภาษาของอินเทอร์เฟซ](#ภาษาของอินเทอร์เฟซ)  
**ภาษา:**  
<img src="https://flagcdn.com/w20/fr.png" alt="Français" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)

**Omega-Fuzz** เป็นแอปพลิเคชันเทอร์มินัลในเครื่อง (TUI [Textual](https://github.com/Textualize/textual) + CLI ที่เขียนสคริปต์ได้) ซึ่งทำการค้นพบและทดสอบความปลอดภัยเว็บ (HTTP fuzzing) ในสภาพแวดล้อมที่ได้รับอนุญาต เช่น ห้องทดลอง มิเรอร์ส่วนตัว หรือการทดสอบที่ได้รับความยินยอมอย่างชัดเจน

เครื่องมือนี้เป็นส่วนหนึ่งของชุด `omega-` และถูกจัดโครงสร้างตาม Clean Architecture — ดูรายละเอียดทางเทคนิคทั้งหมดใน `docs/ARCHITECTURE.md`

## 1. วิสัยทัศน์และขอบเขต

### Omega-Fuzz ทำอะไร

- ค้นพบขอบเขตของเป้าหมายเดียวด้วย BFS โดยถูกจำกัดด้วย scope ที่ระบุชัดเจน (schema, โดเมนย่อย, เส้นทางที่อนุญาต/บล็อก, ความลึก) และไม่มีการทำงานโดยไม่มีมาตรการป้องกัน
- ทำ generic fuzzing กับพารามิเตอร์ query string, HTTP headers และฟอร์ม `GET` ที่พบในทุก URL ที่ค้นพบ แล้วตรวจสอบสามกลุ่มลายเซ็น: reflected XSS แบบไม่ทำลาย, generic injection (ตรวจจับข้อผิดพลาดในการตอบกลับ) และ security headers ที่ขาดหายหรือตั้งค่าผิด — ดู [§5](#5-การทดสอบความปลอดภัยที่ดำเนินการ)
- ให้คะแนนความผิดปกติแต่ละรายการใน 3 มิติ (ผลกระทบ, ความสามารถในการโจมตี, ขอบเขต) และสรุปเป็น severity (`low`/`medium`/`high`/`critical`) พร้อมลบรายการซ้ำตาม `(ประเภท, endpoint, พารามิเตอร์)` และเก็บหลักฐานที่ดีที่สุด — ดู [§6](#6-คะแนนและระดับความรุนแรง)
- รองรับการยืนยันตัวตน (cookie, bearer token, ฟอร์มเข้าสู่ระบบ) ผ่านไฟล์ YAML เฉพาะ โดยไม่มีข้อมูลรับรองแบบข้อความล้วนในบรรทัดคำสั่ง
- แสดงผลใน TUI (Textual) หรือ CLI ที่เขียนสคริปต์ได้ พร้อมการส่งออก 3 รูปแบบ (JSON, Markdown, HTML 5 ธีม)
- เก็บประวัติการสแกนและ findings อย่างถาวรใน SQLite รวมถึงรายการเป้าหมายโปรดที่ใช้ซ้ำได้
- ต้องมีการยืนยันอย่างชัดเจน (วลีที่กำหนดสำหรับกรณีที่อ่อนไหวที่สุด) ก่อนการสแกนแบบรุนแรง ขยายวง หรือที่ปิดการตรวจสอบ TLS

### Omega-Fuzz ไม่ทำอะไร

- Fuzzing เนื้อหา JSON — มีโค้ดอยู่ (`plugins/fuzzers/json_body_fuzzer.py`) แต่ยังไม่ได้เชื่อมต่อ (การค้นพบ HTML/BFS ไม่สร้าง JSON API schema หรือแหล่งเทมเพลตที่ใช้ได้)
- Fuzzing ฟอร์ม `POST`/`PUT`/`DELETE` — ถูกตัดออกจาก pipeline อัตโนมัติโดยเจตนา (เสี่ยงเขียนข้อมูลโดยไม่ตั้งใจบนเป้าหมาย) ทดสอบเฉพาะฟอร์ม `GET`
- การทดสอบ business logic (IDOR, การควบคุมสิทธิ์, การทำลาย workflow) — มีโค้ดอยู่ (`plugins/logic_tests/`) แต่อยู่นอก pipeline อัตโนมัติ เรียกใช้แยกเท่านั้น และไม่ถูกเรียกโดยการสแกนปกติ
- การสแกนหลายเป้าหมายพร้อมกัน — หนึ่งเป้าหมายต่อการสแกน
- การเล่นซ้ำ เปรียบเทียบ หรือส่งออกจากหน้าประวัติ — บันทึกเฉพาะ `Scan` และ `Finding` (ไม่บันทึกการตั้งค่าที่ใช้จริงทั้งหมดหรือคำขอ) การเล่นซ้ำหรือส่งออกจากประวัติจะสร้างข้อมูล หน้าจอจะอธิบายเรื่องนี้แทนการเสนอฟังก์ชันโดยไม่แจ้ง
- การเรนเดอร์ JavaScript ฝั่งไคลเอนต์ (ดึงหน้าเว็บตามที่เซิร์ฟเวอร์ส่งกลับ ไม่ได้รันในเบราว์เซอร์ headless)
- แดชบอร์ดเว็บ

## 2. การติดตั้ง

### ข้อกำหนด

- Python 3.10+
- การเชื่อมต่ออินเทอร์เน็ต เพื่อติดตั้ง dependencies
- สำหรับ TUI: ต้องติดตั้งฟอนต์ [Nerd Font](https://www.nerdfonts.com/) ในเทอร์มินัลเพื่อแสดงไอคอนส่วนหัว — หากไม่มี อักขระจะแสดงเป็นสี่เหลี่ยมว่าง (ข้อจำกัดเดียวกับ emoji แต่พบได้กว้างกว่าในผู้ใช้เทอร์มินัล) การขาดฟอนต์ไม่กระทบการทำงาน เป็นเพียงเรื่องการแสดงผล

### การติดตั้ง

```bash
[ -d omega-fuzz ] && echo "ℹ️ แตกไฟล์ไว้ที่นี่แล้ว ข้ามขั้นตอนนี้" || tar -xzf omega-fuzz.tar.gz
cd omega-fuzz/
chmod +x install.sh
./install.sh
```

`install.sh`:

1. สร้าง virtual environment `.venv` หากยังไม่มี
2. ติดตั้ง dependencies (`vendor/omega-lib/` แล้ว `pip install -e .`; `pyproject.toml` ยังคงเป็นแหล่งความจริงเดียว)
3. ทำให้ `omega-fuzz.sh` และ `install.sh` executable
4. เพิ่ม alias `fuzz` ใน `~/.bashrc` และ `~/.zshrc` (ไม่เพิ่มซ้ำหากมีอยู่แล้ว)

### Dependencies

ประกาศใน `pyproject.toml` (ไม่มี `requirements.txt`):

- `omega-lib`: ไลบรารีที่ใช้ร่วมกันของชุดเครื่องมือ (ธีมการส่งออก, การตรวจจับเทอร์มินัล, `ConfidenceLevel`) — รวมอยู่ใน `vendor/omega-lib/`
- `httpx`: HTTP requests แบบ asynchronous (การค้นพบ + fuzzing) และ streaming การตอบกลับ (ไม่เก็บ response เต็มในหน่วยความจำ แม้เป็นไฟล์หลาย GB ที่เป้าหมายให้บริการ)
- `beautifulsoup4` + `lxml`: ดึง URL และฟอร์ม HTML
- `jinja2`: เทมเพลตสำหรับส่งออก HTML
- `textual`: อินเทอร์เฟซ TUI, ธีม, ปรับตัวกับเทอร์มินัลอัตโนมัติ
- `pyyaml`: โหลดไฟล์ `--auth-config`
- Dependencies สำหรับพัฒนา (`pip install -e ".[dev]"`): `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-httpserver`, `ruff`, `mypy`, `import-linter`

## 3. การใช้งาน

### โหมดโต้ตอบ (TUI)

แนะนำสำหรับการใช้งานประจำ — รันโดยไม่มีอาร์กิวเมนต์:

```bash
./omega-fuzz.sh
```

หากสร้าง alias แล้ว พิมพ์ `fuzz` ในเทอร์มินัล:

```bash
fuzz
```

ลำดับการใช้งาน: หน้าเริ่มต้น (ปิดด้วยการกดปุ่มหรือคลิก) → เมนูหลัก (สแกน / เป้าหมาย / การตั้งค่า / ประวัติ / ช่วยเหลือ) → ป้อนเป้าหมาย (URL เต็ม ต้องมี schema `http://`/`https://`), preset หรือตั้งค่าเอง (scope + ความรุนแรง), การยืนยันตัวตนเลือกได้, การตรวจสอบ TLS, การ override ขีดจำกัด → หน้าตรวจทาน (ยืนยันปกติ หรือวลี `OUI-J-AI-L-AUTORISATION` สำหรับกรณีอ่อนไหว) → สแกน (ตัวบ่งชี้ไม่ระบุความคืบหน้า ปุ่ม **หยุด** ใช้ได้ตลอด) → ผลลัพธ์ (findings, ส่งออก) → ประวัติ (รายละเอียดการสแกนก่อนหน้าและ findings ที่เกี่ยวข้อง) และเป้าหมายโปรดจากเมนูหลัก การปรับตัวกับเทอร์มินัล (สี ขนาด การลดรูปแบบโครงสร้าง) เกิดขึ้นอัตโนมัติ

#### คีย์ลัด

| ปุ่ม | การทำงาน |
|---|---|
| `↑` / `↓` | นำทางระหว่างองค์ประกอบในหน้าจอ |
| `Tab` / `Shift+Tab` | นำทางระหว่างฟิลด์ของฟอร์ม |
| `Esc` | กลับหน้าก่อนหน้า (ยืนยันการออกที่หน้าเริ่มต้น) |
| `t` | ธีมถัดไป (ใช้ทันที ไม่ต้องยืนยัน) |
| `r` | รีเฟรชการตรวจจับเทอร์มินัล |
| `a` | แสดงช่วยเหลือ (ตาราง preset ที่มีให้) |
| `q` | ออก (มีการยืนยัน) |
| `Ctrl+P` | แผงคำสั่ง (Theme, ออก, ภาพหน้าจอ) |

### ภาษาของอินเทอร์เฟซ

อินเทอร์เฟซรองรับ 17 ภาษา: ฝรั่งเศส อังกฤษ สเปน โปรตุเกส (บราซิล) อิตาลี เยอรมัน ดัตช์ โปแลนด์ รัสเซีย จีนตัวย่อ เวียดนาม ไทย อินโดนีเซีย ญี่ปุ่น เกาหลี ฮินดี และอาหรับ เลือกภาษาใน “การตั้งค่า” («ภาษา / Language») และจะมีผลหลังรีสตาร์ตอินเทอร์เฟซ ตัวแปร `OMEGA_FUZZ_LANG` (เช่น `OMEGA_FUZZ_LANG=en ./omega-fuzz.sh`) บังคับภาษาตลอดหนึ่งเซสชัน เมื่อรันจาก omega-suite omega-fuzz จะใช้ภาษาของชุดเครื่องมือ บน Linux text console (TTY) ภาษาที่ใช้ระบบเขียนที่ไม่ใช่ละตินจะแสดงเป็นภาษาอังกฤษตลอดเซสชัน ส่วน command line ยังเป็นภาษาฝรั่งเศส

### โหมดสคริปต์ (CLI)

```bash
# สแกนด้วย preset ที่เตรียมไว้
./omega-fuzz.sh scan --target https://example.com --preset prod-safe

# ผสม scope + ความรุนแรงด้วยตนเอง (ไม่ใช้ preset)
./omega-fuzz.sh scan --target https://example.com --scope-profile standard --aggressiveness standard

# ใช้การยืนยันตัวตน (ไฟล์ YAML ไม่มีข้อมูลรับรองแบบข้อความล้วนในบรรทัดคำสั่ง)
./omega-fuzz.sh scan --target https://example.com --preset staging-full --auth-config auth.yaml

# Dry-run: แสดงการตั้งค่าที่ใช้จริงและแผนประมาณการ ไม่ส่งคำขอ
./omega-fuzz.sh scan --target https://example.com --preset prod-safe --dry-run

# ส่งออกแบบระบุปลายทาง (โฟลเดอร์ รูปแบบ ธีม HTML)
./omega-fuzz.sh scan --target https://example.com --preset prod-safe \
    --output-dir ./rapports --format html --export-theme omega-neon
```

ตัวเลือกของ `scan`:

| ตัวเลือก | ค่าเริ่มต้น | ผลลัพธ์ |
|---|---|---|
| `--target` | *(จำเป็น)* | URL เป้าหมาย ต้องมี schema `http://`/`https://` (ไม่เติมให้อัตโนมัติ) |
| `--preset` | — | Preset ที่เตรียมไว้ (ดู [§4](#4-โปรไฟล์ขอบเขตและ-preset)) |
| `--scope-profile` | — | โปรไฟล์ขอบเขต ใช้คู่กับ `--aggressiveness` โดยไม่ใช้ `--preset` |
| `--aggressiveness` | — | ระดับความรุนแรง ใช้คู่กับ `--scope-profile` โดยไม่ใช้ `--preset` |
| `--auth-config` | — | ไฟล์ YAML สำหรับการยืนยันตัวตน |
| `--insecure-tls` | ปิด | ปิดการตรวจสอบ TLS (ทำให้ต้องยืนยันแบบเข้มงวด) |
| `--max-duration` | *(จากโปรไฟล์)* | Override ระยะเวลาสูงสุด (วินาที) |
| `--max-requests` | *(จากโปรไฟล์)* | Override จำนวนคำขอสูงสุด |
| `--max-tests` | *(จากโปรไฟล์)* | Override จำนวนการทดสอบสูงสุด |
| `--max-concurrent` | *(จากโปรไฟล์)* | Override ความพร้อมกันสูงสุด |
| `--dry-run` | ปิด | แสดงการตั้งค่าที่ใช้จริงและแผนประมาณการ ไม่ส่งคำขอ |
| `--output-dir` | `var/exports/` | โฟลเดอร์รายงานที่ส่งออก ตั้งชื่อ `<preset>-<timestamp>.<นามสกุล>` (override ได้ในการตั้งค่า) |
| `--format` | `all` | `json`, `markdown`, `html` หรือ `all` |
| `--export-theme` | `omega-base` | ธีมของรายงาน HTML ที่ส่งออก (ไม่มีผลกับ json/markdown) |

ไม่มีคำสั่งย่อย `history`/`show` ใน CLI: ประวัติและเป้าหมายโปรดดูได้เฉพาะใน TUI

หาก alias ถูกสร้างโดย `install.sh` `fuzz scan ...` ใช้ได้จากทุกที่ในเทอร์มินัล โดยไม่ต้องมีคำนำหน้า `./omega-fuzz.sh`

## 4. โปรไฟล์ขอบเขตและ preset

### โปรไฟล์ขอบเขต

| โปรไฟล์ | โหมด | ความลึกสูงสุด | ข้อจำกัด |
|---|---|---|---|
| `strict` | เป้าหมายตรง | 1 | บล็อก `/health`, `/ready`, `/metrics`, `/favicon.ico`, `/robots.txt` |
| `standard` | + โดเมนย่อย | 2 | บล็อกโดเมนย่อยแบบ static ทั่วไป, เส้นทางเทคนิค และ assets (รูป/css/js/font) |
| `large` | + โดเมนย่อย | 4 | บล็อกเฉพาะเส้นทางเทคนิคและ assets (รวม archive/PDF) |
| `api` | เป้าหมายตรง | 3 | จำกัดที่ `/api`, `/v1`, `/v2`; บล็อกเอกสารและ assets |
| `custom` | + โดเมนย่อย | 3 | ไม่มีข้อจำกัดเริ่มต้น — จุดเริ่มสำหรับการตั้งค่าเอง |

ไม่ว่าจะเลือกโปรไฟล์ใด รายการนามสกุลไฟล์ binary/ขนาดใหญ่ (`.iso`, `.zip`, `.exe`, `.mp4` ฯลฯ) จะ **ถูกยกเว้น** จากการ crawl และ fuzzing เสมอ แม้ใน `custom` — ลิงก์ไปยังไฟล์ประเภทนี้จะไม่ถูกดึงด้วย HTTP request จริง เพื่อไม่ให้โฟลเดอร์ดาวน์โหลดทำให้การสแกนช้าลงหลายนาที

### ระดับความรุนแรง

`doux` · `standard` · `agressif` · `violent` — แต่ละระดับมีขีดจำกัดพื้นฐานของตนเอง (ระยะเวลา, คำขอ, การทดสอบ, ความลึก, ความพร้อมกัน) และ preset สามารถ override ได้หากระบุ

### Preset ที่เตรียมไว้

| Preset | ขอบเขต | ความรุนแรง | เวลาสูงสุด | คำขอสูงสุด | การทดสอบสูงสุด | ความลึกสูงสุด | ยืนยันแบบเข้มงวด |
|---|---|---|---|---|---|---|---|
| `prod-safe` | strict | doux | 300 วินาที | 1,000 | 500 | 1 | ไม่ |
| `staging-full` | standard | standard | 1,800 วินาที | 20,000 | 10,000 | 2 | ไม่ |
| `lab-deep` | large | agressif | 3,600 วินาที | 100,000 | 50,000 | 4 | ไม่ |
| `lab-extreme` | large | violent | 7,200 วินาที | 500,000 | 250,000 | 5 | **ใช่** |
| `api-hardened` | api | agressif | 1,800 วินาที | 50,000 | 25,000 | 3 | ไม่ |

การสแกนจะถูกบล็อกจนกว่าจะยืนยัน การยืนยัน **แบบเข้มงวด** (พิมพ์วลี `OUI-J-AI-L-AUTORISATION` ให้ตรง) จำเป็นเมื่อมีอย่างน้อยหนึ่งในสามปัจจัย: ความรุนแรง `violent`, preset `lab-extreme` หรือปิดการตรวจสอบ TLS (`--insecure-tls`) — หากเป็นการผสมผสานที่ผิดปกติโดยไม่มีหนึ่งในสามปัจจัยนี้ ใช้การยืนยันใช่/ไม่ใช่ปกติ

## 5. การทดสอบความปลอดภัยที่ดำเนินการ

Pipeline อัตโนมัติ สำหรับทุก URL ที่ค้นพบในขอบเขต (และฟอร์ม `GET` ทุกฟอร์มที่พบ):

| การทดสอบ | เงื่อนไขการรัน | สิ่งที่ตรวจสอบ |
|---|---|---|
| Generic parameter fuzzing | ทุกพารามิเตอร์ query string | พฤติกรรมของเป้าหมายต่อค่าขอบเขต/ผิดรูป |
| Header fuzzing | หนึ่งครั้งต่อ URL, 4 headers คงที่ (`User-Agent`, `Referer`, `X-Forwarded-For`, `Accept-Language`) | พฤติกรรมของเป้าหมายต่อค่าขอบเขต/ผิดรูปใน header |
| ฟอร์ม fuzzing (เฉพาะ `GET`) | ทุกฟิลด์ฟอร์ม `GET` ที่ค้นพบในขอบเขต | พฤติกรรมของเป้าหมายต่อค่าขอบเขต/ผิดรูปในฟิลด์ฟอร์ม |
| Reflected XSS | ทุกพารามิเตอร์ query string | การสะท้อน payload โดยไม่ถูกกรองใน response (ไม่ทำลาย) |
| Generic injection | ทุกพารามิเตอร์ query string | ตรวจจับข้อผิดพลาดเซิร์ฟเวอร์ใน response หลัง injection payload (ไม่ทำ SQL/NoSQL fingerprint เฉพาะ) |
| Security headers | หนึ่งครั้งต่อ URL | Security headers ที่ขาดหายหรือตั้งค่าผิดใน response |

สามการทดสอบแรก (generic fuzzing พารามิเตอร์/headers/ฟอร์ม) เป็น mutation engine **ที่ไม่ทำการตรวจจับ** — ไม่สร้าง `Finding` โดยตรง มีเพียงข้อผิดพลาดเซิร์ฟเวอร์ (5xx) ที่พบจะถูกนับใน `Test` ที่เกี่ยวข้อง เฉพาะลายเซ็น (XSS, injection, security headers) เท่านั้นที่สร้าง findings

## 6. คะแนนและระดับความรุนแรง

ความผิดปกติแต่ละรายการที่ตรวจพบจะได้คะแนนใน 3 มิติ (`impact`, `exploitability`, `scope` อย่างละ 1–5) ตามลักษณะของการสังเกต — mapping ถูกออกแบบให้ **อนุรักษ์นิยม** (ต่ำของช่วง ไม่มีการยืนยันโดยมนุษย์ในขั้นตอนอัตโนมัตินี้):

| คะแนนดิบ (ผลรวม 3 มิติ) | Severity |
|---|---|
| ≥ 13 | `critical` |
| ≥ 10 | `high` |
| ≥ 7 | `medium` |
| < 7 | `low` |

ยังสามารถปรับด้วยมือได้ (`severity_override`) แต่ต้องมีเหตุผลชัดเจนเสมอ findings ที่เทียบเท่ากัน (ประเภท, endpoint และพารามิเตอร์เดียวกัน) จะถูกลบซ้ำ โดยเก็บหลักฐานที่ดีที่สุดที่มี (ระดับความเชื่อมั่น `omega_lib.core.confidence.ConfidenceLevel` แล้วจึงใช้คะแนนดิบหากเท่ากัน)

## 7. การยืนยันตัวตน

ไฟล์ YAML เฉพาะ (`--auth-config`) ไม่มีข้อมูลรับรองแบบข้อความล้วนในบรรทัดคำสั่ง:

| โหมด | ผลลัพธ์ |
|---|---|
| `none` | ไม่มีการยืนยันตัวตน (ค่าเริ่มต้น) |
| `cookie` | ส่ง session cookie โดยตรง |
| `bearer_token` | โทเคน `Authorization: Bearer ...` |
| `login_form` | ยืนยันตัวตนผ่านฟอร์ม (URL เข้าสู่ระบบ, ฟิลด์ผู้ใช้/รหัสผ่าน) |

## 8. สถาปัตยกรรม

Omega-Fuzz ถูกจัดโครงสร้างเป็น **Clean Architecture** (domain / application / infrastructure / interfaces / ports / core / app / plugins) สอดคล้องกับเทมเพลตของชุด `omega-` (ดู `omega-check`/`omega-deep`/`omega-fold`) และตรวจสอบด้วย `import-linter` ทุกครั้งที่แก้ไข รายละเอียดทั้งหมดอยู่ใน **`docs/ARCHITECTURE.md`**

ภาพรวมสั้น ๆ:

```text
src/omega_fuzz/
├── domain/          Business logic บริสุทธิ์ (เป้าหมาย/ขอบเขต, requests, tests, findings, โปรไฟล์, รายงาน...)
├── application/     Use cases (commands/queries) และ orchestrators (การค้นพบ, สแกน, รายงาน, ขีดจำกัด)
├── ports/           สัญญาที่แอปพลิเคชันคาดหวัง (http_client, repositories, exporters...)
├── infrastructure/  การ implement จริง (httpx, BeautifulSoup, SQLite, Jinja2 exporters — Textual ไม่อยู่ที่นี่)
├── interfaces/      tui/ (Textual) และ cli/ (เขียนสคริปต์ได้) มีความเท่าเทียมเชิงฟังก์ชันอย่างเข้มงวด
├── plugins/         Fuzzers และ signatures (pure functions ไม่เข้าถึงเครือข่ายโดยตรง)
├── app/             การประกอบระบบ (Container, composition root, lifecycle)
└── core/            คำศัพท์ร่วม, errors, constants
```

กฎการออกแบบ:

- `plugins/fuzzers/` และ `plugins/signatures/`: pure functions ที่สร้างแผนทดสอบ (`Test` + `ScanRequest`) ไม่ใช้ `HttpClient`
- `infrastructure/network/`: ทำงานด้านเครือข่าย (`httpx`, streaming ที่จำกัดหน่วยความจำ) ไม่ตัดสินใจแทน
- `infrastructure/analyzers/`: อ่าน response ที่ได้รับแล้ว สร้าง `Observation` ที่มีโครงสร้าง ไม่คำนวณคะแนนซ้ำ
- `interfaces/`: แสดงผลเท่านั้น ไม่มี business logic

## 9. การส่งออก

รายงาน Markdown และ HTML เขียนด้วยภาษาที่เลือกใน “การตั้งค่า” («ภาษาของการส่งออก» ค่าเริ่มต้นคือภาษาของอินเทอร์เฟซ) JSON ยังคงเป็นข้อมูลและไม่ถูกแปล รายงานถูกสร้างใน `var/exports/` ตามค่าเริ่มต้น (runtime path ผูกกับโฟลเดอร์โปรเจกต์, `$OMEGA_FUZZ_VAR_DIR` เพื่อ override และ override ได้ในหน้าการตั้งค่า) หรือตามเส้นทางที่ระบุ (`--output-dir`) ชื่อไฟล์แบบแบน ไม่มีโฟลเดอร์ย่อย: `<preset>-<timestamp>.<นามสกุล>` (เช่น `prod-safe-2026-09-01_14-30-22.html`)

### JSON, แหล่งความจริง

โครงสร้างรายงานเต็ม (การตั้งค่าที่ใช้จริง, สถิติ, tests, findings) ที่ serialize เป็น JSON ได้อย่างเคร่งครัด

### Markdown, รายงานกระชับสำหรับมนุษย์

อ่านได้นอกเทอร์มินัล ไม่มี ANSI codes

### HTML, รายงานเว็บแบบสแตนด์อโลน

มี 5 ธีมให้เลือก (`--export-theme` ใน CLI, ตัวเลือกใน TUI): `omega-base`, `omega-burn`, `omega-neon`, `light-basic`, `light-alt`

## 10. ประวัติและเป้าหมายโปรด

การสแกนแต่ละครั้งถูกบันทึก (SQLite, `var/db/omega-fuzz.db`) พร้อม findings และดูได้จากหน้าประวัติใน TUI บันทึกเฉพาะ `Scan` และ `Finding` — ไม่บันทึกการตั้งค่าที่ใช้จริงทั้งหมดหรือคำขอโดยละเอียด — จึงไม่มีการเล่นซ้ำ เปรียบเทียบ หรือส่งออกใหม่จากหน้านี้ (หน้าจออธิบายเรื่องนี้แทนการสร้างข้อมูล)

หน้า **เป้าหมาย** เก็บรายการโปรด (URL ที่ normalize แล้ว, `var/targets.json`) ใช้ซ้ำเพื่อเติมฟิลด์เป้าหมายของการสแกนใหม่โดยตรง

## 11. ภาพหน้าจอ

คำสั่ง **ภาพหน้าจอ** ในแผงคำสั่ง (`Ctrl+P`): บันทึก SVG ของหน้า TUI ปัจจุบันไปที่ `var/screenshots/` ตามค่าเริ่มต้น สามารถ override ได้ในหน้าการตั้งค่า (เช่นเดียวกับโฟลเดอร์ส่งออก) มีฟังก์ชันล้างข้อมูลเฉพาะในการตั้งค่า

## 12. ความเข้ากันได้ของเทอร์มินัล

TUI (Textual) ตรวจจับความสามารถของเทอร์มินัลอัตโนมัติ (emulator, ขนาด) และปรับ structural stylesheet (`complete`/`standard`/`reduced`/`mono`) โดยไม่ต้องใช้ flag ด้วยมือ CLI ยังคงเป็นข้อความล้วนเสมอ ไม่ขึ้นกับเทอร์มินัล นโยบายนี้ใช้ร่วมกันทั้งชุด `omega-` (`omega-lib`, `terminal/policies.py`)

### โปรไฟล์ตาม emulator ที่ตรวจพบ

| Emulator | โปรไฟล์เริ่มต้น |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | `complete` |
| Konsole, GNOME Terminal, Terminator, Xfce4 Terminal | `standard` |
| xterm, urxvt, SSH สมัยใหม่ | `reduced` |
| Linux TTY, SSH รุ่นเก่า | `mono` |
| Emulator ที่ไม่รู้จัก | `reduced` (fallback เริ่มต้น) |

### โปรไฟล์ตามขนาดเทอร์มินัล

| ขนาดขั้นต่ำ (คอลัมน์ × บรรทัด) | เพดานโปรไฟล์ |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| ต่ำกว่า | `mono` |

โปรไฟล์สุดท้ายคือ **โปรไฟล์ที่จำกัดมากที่สุดจากทั้งสอง** (emulator และขนาด) — รีเฟรชแบบสดได้ด้วยปุ่ม `r`

## 13. การทดสอบ

```bash
source .venv/bin/activate
lint-imports        # ตรวจสอบ Dependency Rule (6 สัญญา)
pytest -q           # 344 tests
ruff check src tests
mypy -p omega_fuzz
```

โครงสร้าง: `tests/unit/` (domain และ application ไม่มี I/O จริง), `tests/integration/` (ระบบไฟล์จริงผ่าน `tmp_path`, fake HTTP server `pytest-httpserver`, SQLite จริง, CLI end-to-end), `tests/tui/` (นำทางผ่าน `Pilot`, structural checks — ไม่อ้างว่าตรวจสอบภาพอัตโนมัติ)

## 14. นอกขอบเขต

- Fuzzing เนื้อหา JSON (มีโค้ด แต่ไม่ได้เชื่อมต่อ — ไม่มีการค้นพบ API schema)
- Fuzzing ฟอร์ม `POST`/`PUT`/`DELETE` (ตัดออกโดยเจตนา เสี่ยงการเขียน)
- การทดสอบ business logic (IDOR, สิทธิ์, workflow) นอกการเรียกใช้ด้วยมือ
- การสแกนหลายเป้าหมายพร้อมกัน
- การเล่นซ้ำ เปรียบเทียบ หรือส่งออกจากประวัติ
- การเรนเดอร์ JavaScript ฝั่งไคลเอนต์
- แดชบอร์ดเว็บ

---

> Omega-Fuzz — ค้นพบขอบเขต ทดสอบด้วยมาตรการป้องกันที่ชัดเจน และไม่เดาสิ่งที่ยังไม่ได้รับการยืนยัน
