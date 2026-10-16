# 📝 CATATAN DISKUSI — VALIDITAS & RELIABILITAS + 12 UJI

> **Status: CATATAN DISKUSI — BELUM DIKERJAKAN, BELUM DI-ACC.**
> Arahan Bos 19Sep26: *"Masalah validitas dan reabilitas 12 uji itu diskusi saja,
> kamu catat biasa saja, mungkin nanti setelah project bisa kita bahas lagi."*
>
> ⚠️ **JANGAN mulai koding dari berkas ini.** Tunggu Bos membuka bahasan ini lagi.

Dicatat: 19 Sep 2026 · Sesi kartu uji t

---

## 🔴 KENYATAAN AWAL (hasil cek kode, bukan dugaan)

Pertanyaan Bos: *"apakah kita ada uji reabilitas dan uji validitas juga"*

**Jawaban jujur: BELUM ADA sebagai uji.** Tapi **mesinnya sebagian sudah ada.**

| Hal | Di mana | Status |
|---|---|---|
| Alpha Cronbach **dihitung** | `alpha_rencana()` di `app/hitung/*.py` | ✅ mesin (internal) |
| Alpha di **halaman ajar** | entri ke-6 kamus BELAJAR | ✅ ada |
| Setelan alpha | `/buat-data` (rendah/sedang/tinggi) | ✅ ada |
| Outer Loading · AVE · Composite Reliability | halaman `/syarat` | ⚠️ **keterangan saja** |
| **Uji validitas (r hitung vs r tabel)** | — | ❌ **BELUM** |
| **Uji reliabilitas (tabel alpha + alpha if item deleted)** | — | ❌ **BELUM** |
| KMO & Bartlett | — | ❌ belum |
| HTMT · Fornell-Larcker | — | ❌ belum |

**TEMUAN:** `app/templates/segera.html` **sudah menjanjikan** uji validitas
(*"...validitas, normalitas, multikolinearitas, heteroskedastisitas, outlier..."*)
tapi halamannya belum dikerjakan.

---

## 📚 27 UJI KUANTITATIF — PETA LENGKAP

### 🔵 TAHAP 1 — UJI INSTRUMEN (7)

| # | Uji | Alat | Ada? |
|---|---|---|---|
| 1 | Validitas isi (expert judgment) | manual/dosen | ❌ tak bisa diotomatiskan |
| 2 | Validitas konstruk — korelasi item-total | SPSS | ❌ |
| 3 | Validitas konstruk — CFA/faktor | AMOS/PLS | ❌ |
| 4 | Reliabilitas — Alpha Cronbach | SPSS | ⚠️ mesin ada |
| 5 | Reliabilitas — Alpha if Item Deleted | SPSS | ❌ |
| 6 | Reliabilitas — Composite Reliability | SmartPLS | ⚠️ keterangan |
| 7 | Reliabilitas — Split-half, KR-20 | SPSS | ❌ |

### 🟢 TAHAP 2 — UJI ASUMSI KLASIK (9)

| # | Uji | Ada? |
|---|---|---|
| 8 | Normalitas — P-P/Q-Q/histogram | ⚠️ keterangan |
| 9 | Normalitas — Kolmogorov-Smirnov / Shapiro-Wilk | ❌ |
| 10 | Normalitas — Skewness & Kurtosis | ❌ |
| 11 | Multikolinearitas — VIF & Tolerance | ✅ **JALAN** |
| 12 | Heteroskedastisitas — Scatter ZPRED×ZRESID | ✅ **JALAN** |
| 13 | Heteroskedastisitas — Glejser / Breusch-Pagan / White | ❌ |
| 14 | Linearitas — Scatter / Lack of Fit / Ramsey | ⚠️ keterangan |
| 15 | Autokorelasi — Durbin-Watson / Run Test | ❌ |
| 16 | Outlier — Box-Plot / Z-score / Mahalanobis | ❌ |

### 🟣 TAHAP 3 — UJI HIPOTESIS & LANJUTAN (11)

| # | Uji | Ada? |
|---|---|---|
| 17 | Uji t (parsial) | ✅ **JALAN** |
| 18 | Uji F (simultan) | ⚠️ mesin ada |
| 19 | R², Adjusted R² | ✅ **JALAN** |
| 20 | Mediasi — Sobel / Bootstrap | ✅ mesin terbukti |
| 21 | Moderasi — MRA / interaksi | ✅ mesin terbukti |
| 22 | Uji beda — t-test, ANOVA, ANCOVA, MANOVA | ❌ |
| 23 | Non-parametrik — Mann-Whitney, Kruskal-Wallis, Wilcoxon, Chi-Square | ❌ |
| 24 | Korelasi — Pearson, Spearman, Kendall | ❌ |
| 25 | PLS: Outer Loading, AVE, HTMT, Fornell-Larcker | ⚠️ keterangan; HTMT ❌ |
| 26 | PLS: Q², PLSpredict, SRMR, f² | ⚠️ sebagian |
| 27 | PLS: IPMA | ❌ |

**Ringkas:** ✅ sudah jalan **6** · ⚠️ mesin/keterangan ada **7** · ❌ belum **14**

---

## 🎯 USULAN WULAN — 12/13 UJI INTI (belum diputuskan Bos)

**Alasan jangan 27 semua:** tidak semua dipakai skripsi · sebagian tak bisa diotomatiskan ·
data simulasi hasilnya selalu bagus (membosankan) · yang dipakai 90% mahasiswa hanya ~12.

| Prioritas | Uji | Alasan |
|---|---|---|
| 🥇 1 | **Validitas (r hitung vs r tabel) + Reliabilitas (alpha + alpha if item deleted)** | paling sering dipakai & paling sering bingung |
| 🥈 2 | Normalitas (K-S + skewness) | wajib di skripsi |
| 🥉 3 | Uji F simultan | pasangan uji t |
| 4 | Durbin-Watson + Glejser | lengkapi asumsi klasik |
| 5 | HTMT + Fornell-Larcker | untuk yang pakai PLS |

### 📥 KOMPONEN INPUT — KUNCI PENTINGNYA

**Mahasiswa TIDAK perlu input apa-apa untuk uji-uji ini** — semua dihitung dari
**data yang sudah ada** di `/buat-data`.

| # | Yang diinput | Wajib? | Default otomatis |
|---|---|---|---|
| 1 | File data (CSV/XLSX) | ✅ | ← data terakhir dari /buat-data |
| 2 | Perlakuan (SPSS/PLS) | ✅ | ← pilihan terakhir |
| 3 | Daftar konstruk + anggotanya | ⚠️ bisa ditebak | ← tebak dari nama kolom (KP1,KP2 → KP) |
| 4 | Mana X, mana Y | ✅ | ← sudah ada di setelan |
| 5 | Nilai α (0,05/0,01) | ⚠️ | ← 0,05 |
| 6 | n tabel / df | ⚠️ | ← dari jumlah baris |

**Jadi yang benar-benar diklik mahasiswa: 1–2 saja.**

### 🖥️ 3 OPSI TAMPILAN (Wulan usul A)

| Opsi | Bagaimana | Catatan |
|---|---|---|
| **A** ⭐ | Tambah bagian di halaman **`/syarat`** yang SUDAH ADA | tidak nambah menu (aturan "sambungkan yang sudah ada") |
| B | Menu baru `/uji` | menu sudah 8 → makin bingung pemula |
| C | Menempel di `/buat-data` | halaman jadi sangat panjang, berat di HP |

---

## ⚠️ 3 HAL YANG WAJIB DIINGAT KALAU NANTI DIKERJAKAN

**1. Data simulasi = hasil selalu bagus.**
Uji normalitas, DW, Glejser **akan selalu lulus** karena kita yang membuat datanya begitu.
**Tanpa tombol "buat data yang melanggar asumsi", halaman ini kurang berguna untuk mengajar.**
→ nyambung ke **modul KLINIK** (sudah direncanakan).

**2. Validitas hanya menarik kalau n kecil.**
Data simulasi n=200 → korelasi tinggi → **semua item pasti valid**.
Relevan untuk **n 30–50** (uji coba kuesioner sungguhan).

**3. r tabel harus otomatis.**
Ini yang paling sering salah di mahasiswa — jangan suruh buka tabel manual.

---

## 🎁 FITUR BONUS YANG DIUSULKAN (belum diputuskan)

| Fitur | Nilai |
|---|---|
| Tombol **"Tebak konstruk"** dari nama kolom | user cuma konfirmasi |
| **r tabel & df otomatis** | hilangkan sumber salah tersering |
| Tombol **"Tampilkan kunci jawaban"** | untuk Bos mengajar (tersembunyi dari mahasiswa) |
| **Ekspor hasil ke .docx** | langsung tempel ke skripsi |

---

## 🔗 KAITAN

- Modul **KLINIK** (data sakit + kunci jawaban) — sudah ada di navigasi, belum berisi
- Modul **PEMILIH ALAT** (SPSS vs PLS) — **tujuan akhir Bos**, belum berisi
- Halaman **`/syarat`** — sudah ada (466 baris), isinya belum lengkap
