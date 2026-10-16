# 🔍 AUDIT 23 UJI DI LUAR GERBANG — 21 Sep 2026

> **Kenapa audit ini ada:** `uji_tombol_contoh.py` ternyata **sudah GAGAL**
> berhari-hari, tapi **tidak ketahuan** karena **tidak masuk gerbang**.
> Bos minta diselidiki satu-satu (**Opsi A**).
>
> **Skrip audit:** `_sketsa/ukur_uji_luar_gerbang.py` — jalankan ulang kapan saja.

---

## 📊 HASIL: 10 JALAN · 13 RUSAK

| Status | Berkas |
|---|---|
| **JALAN** (10) | `uji_bar_model` · `uji_belajar_hp` · `uji_efek_tidak_langsung` · `uji_halaman` · `uji_klinik_lapangan` · `uji_mesin_s3_kalibrasi` · `uji_resep3` · `uji_spss_sav` · `uji_tuntas_kemampuan` · `uji_web_s3` |
| **RUSAK** (13) | `uji_final` · `uji_jalur_model` · `uji_kalibrasi` · `uji_kartu_ujit` · `uji_mesin` · `uji_mesin_s3` · `uji_mockup_konfirmasi` · `uji_model` · `uji_pita_tab` · `uji_setel` · `uji_struktural` · `uji_v3` · `uji_web_data` |

---

## 🎯 AKAR UTAMA — **PINTU UKUR SALAH** (kelas kesalahan K-09)

**TERUKUR: 0 dari 13 uji rusak mengukur lewat pintu produksi `buat_data()`.**
Semua mengukur dari **fungsi internal** atau modul yang **sudah tidak dipakai**.

### Bukti paling telak — kasus REGRESI SEDERHANA (`X1` minta **0,65**)

| Cara ukur | Hasil | Galat |
|---|---|---|
| `bangun_dari_spek()` **langsung** (cara uji lama) | **0,5161** | ❌ **0,134** |
| **PINTU PRODUKSI `buat_data()`** (cara aplikasi) | **0,6497** | ✅ **0,0003** |

⇒ **MESIN BENAR.** Yang salah **cara mengukur**.

**Sebabnya:** kalibrasi (`kalibrasi_per_jalur()`) bekerja **DI DALAM**
`buat_data()`. Fungsi internal membangun data **BELUM dikalibrasi** — bahan
setengah jadi. Mengukur bahan setengah jadi lalu menuduh hasil akhir = salah.

### Bukti kedua — S3 berantai

`uji_mesin_s3.py` dulu memanggil `bangun_berurutan(..., koreksi_atenuasi=False)`
(koreksi **dimatikan sengaja**) → galat 0,1854 & 0,0918 → lapor *"BELUM BISA"*.
Dari **pintu produksi**: galat **0,0003–0,0083** → **BISA**.

---

## 📦 MODUL LAMA vs MODUL PRODUKSI (terukur dari `app/`)

| Modul | Dipakai produksi? | Dipakai uji rusak? |
|---|---|---|
| `app/hitung/berurutan.py` | ✅ **3 berkas** | ✅ (tapi ukur internal) |
| `app/hitung/kalibrasi_jalur.py` | ✅ `berkas_kerja.py` | — |
| `app/hitung/generator.py` | ❌ **0** | ✅ `uji_final`, `uji_v3` |
| `app/hitung/struktural.py` | ❌ **0** | ✅ `uji_struktural` |
| `app/hitung/kalibrasi.py` | ❌ **0** | ✅ `uji_kalibrasi` |
| `app/hitung/setel.py` | ❌ **0** | ✅ `uji_setel` |

⇒ **Uji-uji ini menjaga mesin yang sudah digantikan.** Mereka bukan penjaga
produksi — mereka **peninggalan**. Dipakai `generator.py` (matriks korelasi)
yang 17Sep26 sudah **digantikan** `berurutan.py` karena *suppression effect*.

---

## ⚠️ BUKTI LEBIH KUAT: berantai SUDAH DIARSIPKAN

Bos (21Sep26): *"Berantai sudah tidak dipakai lagi"* →
Opsi **R1** = kartu berantai **ditutup dari pintu**.

**Terukur di browser sungguhan (21Sep26):**

| Uji | Hasil |
|---|---|
| Kartu tampak di layar? | ❌ **TIDAK** (`display:none`, tinggi **0 px**) |
| Terpilih otomatis? | ❌ **TIDAK** (default `sederhana`) |
| Kalau **DIPAKSA via JS**? | ⚠️ masih bisa terkirim `cara=berantai` |

**Tapi pengamannya ada:** `const ARSIP_RANTAI = true` + kalau terpilih →
**otomatis dipindah** ke `berganda` (`CARA = 'berganda'`). Dijaga
`sot.py::_periksa_kartu_regresi()`.

⇒ **Risiko = sangat kecil.** Tidak ada satu pun kode di halaman yang memaksa
pilih berantai.

---

## ✅ TINDAKAN YANG SUDAH DIKERJAKAN (21Sep26)

| # | Tindakan | Bukti |
|---|---|---|
| 1 | `uji_tombol_contoh.py` **diperbaiki** (baca bentuk PERAN, bukan `#baris-x`) | **17/0** · *terbukti bisa gagal* |
| 2 | `uji_tombol_contoh.py` **DIMASUKKAN GERBANG** | gerbang jadi **45 grup** |
| 3 | `uji_mesin_s3.py` **diperbaiki** (ukur dari pintu produksi) | **LULUS** · *terbukti bisa gagal* |
| 4 | `uji_mesin_s3.py` **DIMASUKKAN GERBANG** | idem |
| 5 | Berkas cacat **PALSU** `CACAT_RANTAI_BERANTAI_...md` **DIHAPUS** | tidak boleh simpan tuduhan salah |

---

## 📌 URUTAN TINDAKAN BERIKUTNYA (untuk 11 sisa)

**JANGAN buru-buru mengubah.** Tiap berkas harus lewat 3 pertanyaan:

```
1. Modul yang diuji MASIH DIPAKAI produksi?
   → TIDAK  ⇒ tandai "PENINGGALAN" (beri kepala berkas), jangan masuk gerbang
   → YA     ⇒ lanjut pertanyaan 2
2. Cara ukurnya lewat PINTU PRODUKSI (buat_data / rute HTTP)?
   → TIDAK  ⇒ PERBAIKI CARA UKUR (bukan mesin!)
   → YA     ⇒ lanjut pertanyaan 3
3. Kalau tetap GAGAL setelah diukur dari pintu produksi?
   → BARU curigai mesin. Lapor ke Bos DULU sebelum mengubah mesin.
```

**Aturan induk:** *"sebelum menuduh mesin rusak, pastikan kasus & cara ujinya benar"*
(sudah 3× dilanggar: 17Sep26, 20Sep26, 21Sep26 — jangan sampai ke-4).

---

## 🔴 PELAJARAN TERBESAR AUDIT INI

> **Uji yang tidak dijalankan siapa pun = uji mati.**
> Ia bisa jadi **jebakan** (GAGAL palsu, seperti `uji_tombol_contoh`) atau
> **penutup cacat** (GAGAL asli, tidak ketahuan).
>
> **13 dari 23 uji di luar gerbang ternyata RUSAK** — dan **tak satupun**
> menunjukkan mesin produksi bermasalah. Semuanya **cara ukur yang salah**.
>
> ⇒ **Setiap uji yang menyentuh mesin produksi WAJIB masuk gerbang**,
> atau WAJIB diberi kepala berkas *"PENINGGALAN — sebab: ..."*.
