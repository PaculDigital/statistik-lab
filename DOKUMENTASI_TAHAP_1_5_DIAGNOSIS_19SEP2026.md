# 🩺 DOKUMENTASI TAHAP 1.5 — DIAGNOSIS DATA SPSS & PLS
**Tanggal:** 19 September 2026
**Status:** ✅ SELESAI & LIVE di `statistik.bikinaja.id/klinik` (alias `/diagnosis`)
**Gerbang:** 23 grup LULUS · deploy EXIT 0

---

## 1. APA YANG DIBANGUN (perintah Bos, VERBATIM)

> *"Halaman Syarat, jadikan tool / alat saja. Namanya **Diagnosis Data SPSS & PLS**.
> Isinya user upload data dari spss atau pls, untuk didiagnosa dan cara tulisnya.
> **Benar katakan benar, salah katakan salah** dan beri panduan untuk cara
> membetulkan data."*

**Jadi:** `/diagnosis` BUKAN halaman bacaan lagi — ia **alat**:
unggah data → mesin periksa → jawab BENAR/SALAH per syarat → beri cara membetulkan.

---

## 2. YANG DIPERIKSA

### Mode SPSS (6 uji)
| # | Uji | Ambang |
|---|---|---|
| 1 | Normalitas (Kolmogorov-Smirnov + skewness) | p > 0,05 & skewness ±2 |
| 2 | Heteroskedastisitas (Glejser) | p > 0,05 |
| 3 | Multikolinearitas (VIF) | VIF < 10 |
| 4 | Linearitas | — |
| 5 | Data menyimpang (outlier) | — |
| 6 | Autokorelasi (Durbin-Watson) | 1,5–2,5 |

### Mode SmartPLS (5 uji)
Outer Loading · AVE · Composite Reliability · VIF inner · Fornell-Larcker

### Ruang lingkup berkas
`.sav` (SPSS) · `.csv` · `.xlsx` — maks **10 MB**.

---

## 3. ARSITEKTUR KODE

| Berkas | Isi | Baris |
|---|---|---|
| `app/diagnosis.py` | MESIN: baca 3 format + 6 uji SPSS + 5 uji PLS + 6 pagar | 421 |
| `app/nasihat.py` | "Cara membetulkan" untuk **11 masalah** — 5 bagian tiap nasihat | 357 |
| `app/templates/diagnosis.html` | Halaman 4 langkah + hasil + nasihat | 588 |
| `uji_diagnosis.py` | Uji mesin | 23 LULUS |
| `uji_nasihat.py` | Uji kelengkapan + bahasa hangat | 63 LULUS |
| `uji_web_diagnosis.py` | Uji jalur web (HTTP sungguhan) | 37 LULUS |
| `alat_ukur_uji.py` + `uji_alat_ukur.py` | Alat ukur uji + uji diri | 9 LULUS |

### 5 bagian setiap nasihat
1. Artinya apa (bahasa awam)
2. Kenapa bisa terjadi
3. **Kapan boleh diabaikan** (jujur — tidak semua masalah harus dibetulkan)
4. Langkah bernomor membetulkan
5. Yang JANGAN dilakukan

---

## 4. 🚨 AKAR YANG DITEMUKAN & DITUTUP (semua terukur)

### Akar A — `NameError: name 'pd' is not defined`
**Gejala:** unggah berkas → **HTTP 500**.
**Akar:** route memakai `pd` tapi `import pandas as pd` hanya ditulis di dalam
fungsi lain — modul tidak melihatnya.
**Fix:** tambah impor di dalam route.
**Cara menemukan:** **baca LOG SERVER** (`/tmp/srv*.log`), bukan menebak dari browser.

### Akar B — NAMA PARAMETER DITEBAK, bukan dibaca (2 putaran HTTP 500)
| Wulan tulis | Yang BENAR (dari `grep "^def"`) |
|---|---|
| `missing='buang'` | **`buang_kosong='baris'`** |
| `kolom_target` (PLS) | **`kolom_y_konstruk`** |
| `missing` (PLS) | **tidak ada** — PLS tak punya parameter itu |
| `lulus_cl` | **`lulus_muat`** |
| `loading_min` | **`muat`** (daftar butir) |
| `d.n_baris` (di `/periksa`) | **`d.n`** |
| `d.kolom_y` (PLS) | **`d.y_konstruk`** |
| `k.loading_min` | **`k.muat`** |
| `d.vif_inner_maks` | **tidak ada** → hitung dari `vif_inner` |

📌 **ATURAN INDUK:** sebelum memanggil fungsi apa pun, **`grep "^def"` tanda
tangannya DULU**. Menebak nama = HTTP 500 berulang.

⚠️ **JEBAKAN KEMBAR:** `/unggah` mengirim **`n_baris`**, tapi `/periksa` mengirim
**`n`**. Satu halaman, dua nama berbeda. Uji yang mengecek `n_baris` di hasil
`/periksa` akan GAGAL PALSU.

### Akar C — Tag penutup mentah di dalam `<script>` (22 tag)
**Gejala:** gerbang `TEMPLATE — tag penutup di dalam <script>` **GAGAL** →
deploy TERTAHAN.
**Akar:** string JS berisi HTML (`'</div>' +`). Parser HTML menyangka
`</script>` sudah selesai → **kode TUMPAH jadi teks di halaman** walau HTTP 200.
**Fix:** escape garis miring → `<\/div>`. Skrip: `_sketsa/perbaiki_tag_skrip.py`.
**Bukti:** gerbang → 0 pelanggaran, EXIT 0.
**Cara menemukan:** **gerbang** (bukan mata — halaman tetap "tampak hidup").

### Akar D — 🚨 GERBANG IKON PALSU (yang KEDUA)
**Gejala:** gerbangbilang *"semua ikon ADA — 94 pemakaian aman"*, padahal
`play-circle` (ikon menu **MULAI**) **TIDAK ADA di sprite** → elemen KOSONG
tanpa galat apa pun.
**Akar:** `gerbang_ikon.py` **hanya memindai `app/templates/*.html`** —
padahal nama ikon **juga** ditulis di `app/main.py` pada daftar `MODUL`
(`'ikon': 'play-circle'`). **8 pemakaian di main.py tidak pernah diperiksa.**
**Fix:** gerbang ikut memindai `main.py` (pola `'ikon': 'nama'`) → sekarang
**102 pemakaian** diperiksa (dulu 94). Ikon `play-circle` → **`play`**.
**Bukti gerbang BISA GAGAL:** suntik `'ikon': 'ikon-palsu-xyz'` ke `main.py`
→ **EXIT 1**; pulihkan → EXIT 0. ✅

---

## 5. CARA WULAN MENEMUKAN AKAR (bukan menebak)

```
HTTP 500  →  baca LOG SERVER          (bukan tebakan dari browser)
Parameter →  grep "^def" tanda tangan (bukan tebakan nama)
Tampilan  →  render + vision          (bukan asumsi dari DOM)
Gerbang   →  suntik kerusakan → HARUS EXIT 1 (bukan percaya output "LULUS")
```

---

## 6. PERUBAHAN NAMA (keputusan Bos 19Sep26)

| Sebelum | Sesudah | Catatan |
|---|---|---|
| Menu `KLINIK` | **`DIAGNOSIS DATA`** | slug TETAP `klinik` — tautan lama tidak patah |
| Menu `PERIKSA SYARAT` | **`KAMUS GRAFIK`** | halaman `/syarat` DIBIARKAN |
| Kode halaman | `KLINIK` → `DIAGNOSIS DATA` | ikon `stethoscope` → `microscope` |

⚠️ **Wulan hampir salah** mengubah **slug** `klinik` → `diagnosis`. Padahal
keputusan Bos: **NAMA** yang berubah, **slug tetap**. Wulan koreksi setelah
membaca `DOKUMENTASI_KEPUTUSAN_DIAGNOSIS_19SEP2026.md`.
✅ `/klinik` dan `/diagnosis` **dua-duanya 200** (alias, tidak ada yang patah).

---

## 7. BUKTI TERUKUR

| Hal | Angka |
|---|---|
| Mesin diagnosis | **23 LULUS / 0 GAGAL** |
| Nasihat | **63 LULUS / 0 GAGAL** (11 masalah) |
| Jalur web (HTTP) | **37 LULUS / 0 GAGAL** |
| Alat ukur uji | **9 LULUS / 0 GAGAL** (terbukti bisa gagal) |
| Gerbang total | **23 GRUP LULUS · EXIT 0** |
| Deploy | **EXIT 0** |
| Halaman di kontainer | `/klinik` **200** · `/diagnosis` **200** · `/syarat` **200** |
| Domain publik | `statistik.bikinaja.id/klinik` **200** |
| Vision | *"Sangat rapi, tidak ada tumpang tindih/meluber/kosong, tidak ada kode mentah"* |
| Ikon diperiksa | **102 pemakaian** (naik dari 94) |

### Data bersih vs sakit — BUKTI INTI
| | Bersih | Sakit |
|---|---|---|
| R² | 0,4165 | — |
| VIF | 1,0 | **8656** |
| Masalah | **0** | **3** (normalitas, VIF, DW) |

⇒ *"Benar katakan benar, salah katakan salah"* — **terbukti berbeda jawabannya.**

---

## 8. SISA / BELUM

- Tombol **Unduh PDF** hasil diagnosis — belum ada
- Mode SmartPLS: uji **HTMT**, **Q²/PLSpredict**, **SRMR** — belum ada
- **Fornell-Larcker** — belum ada di mesin (disebut di halaman)
- Data sakit **sengaja** + kunci jawaban dosen → masuk TAHAP 3
