# MASTER_PLAN — Penelitian STATISTIK Lab.

**Sumber kebenaran proyek.** Kalau ada perbedaan antara berkas ini dengan dokumen
lain, **berkas ini yang menang**.

> ## ⚠️ TAPI DI ATAS INI MASIH ADA SATU SUMBER YANG LEBIH TINGGI: **KODE DI DISK**
>
> Arahan Bos 18Sep26: **"tetap prinsip SOT single source of truth"**.
>
> **Urutan kekuatan (dari paling benar):**
>
> | # | Sumber | Sifat |
> |---|---|---|
> | 1 | **Kode di disk** (`app/`, `gerbang_uji.py`, `sot.py`) | **KEBENARAN** |
> | 2 | `MASTER_PLAN.md` (berkas ini) | salinan — keputusan terkunci |
> | 3 | `FLAG_LANJUT_DISINI.md` | salinan — posisi kerja |
> | 4 | skill `statistik-lab` + `references/` | salinan — cara kerja |
> | 5 | memory / fact_store | salinan — pengingat |
>
> **Kalau dokumen berbeda dengan kode → KODE YANG MENANG, dokumen diperbaiki.**
>
> **ALAT:** `.venv/bin/python sot.py` — mencetak keadaan terkini **dihitung dari
> kode** (bentuk model, grup uji, halaman, jebakan). Sudah jadi **gerbang uji
> nomor 1**: `sot.py --periksa` → EXIT ≠ 0 kalau dokumen tidak selaras kode.
>
> **Angka apa pun di berkas ini adalah SNAPSHOT bertanggal** — jangan dihafal,
> **hitung ulang**.

- **Tanggal mulai:** 17 September 2026
- **Status:** **TAHAP 2.7 SELESAI DIKODING** (IDENTIFIKASI DATA: mahasiswa tandai PERAN kolom → **skor konstruk**) — **BELUM DEPLOY** (tunggu ACC Bos) · gerbang **60 grup EXIT 0** · SOT selaras
- **Berikutnya:** **deploy** (tunggu ACC) → tahap lanjut sesuai urutan resmi: **Pemilih alat → Ujian → Kualitatif → Login**
- **Cara tahu keadaan terkini:** `.venv/bin/python sot.py`  ← **satu pintu (SOT)**

---

## 0. RINGKASAN TERKINI (20 Sep 2026)

> ⚠️ **Angka di bawah adalah SNAPSHOT.** Untuk keadaan **sekarang**, jalankan
> `.venv/bin/python sot.py --periksa` — ia **MENGHITUNG dari kode**, bukan mengingat.

**Gerbang uji: 60 grup** (`gerbang_uji.py`). Snapshot 21Sep26:

| Grup uji | Asersi |
|---|---|
| INTI — semua model | 29 LULUS |
| MODEL JURNAL BOS (12 hipotesis) | 13 LULUS |
| PENUTUP — 2 mode + sampel kecil | 7 LULUS |
| KELAYAKAN SETELAN | 19 LULUS |
| MODEL LANJUTAN | 10 LULUS |
| WEB — 1–8 variabel + nama + n=2000 | 21 LULUS |
| WEB — istilah, tata letak, lingkaran, tag skrip, galat JS, kode tumpah | LULUS |
| **MESIN — cara menguji sederhana vs berganda** | **12 LULUS** |
| **MESIN — 10 bentuk model (mediasi/moderasi/gabungan)** | **10 LULUS** |
| WEB — slider & teks terpotong | LULUS |
| **WEB — sub-pilihan model (Regresi/Mediasi/Moderasi)** | **46 LULUS** |
| **WEB — nama ikon ada di sprite** | **LULUS** |
| **WEB — sintaks `<script>` inline setelah render Jinja** ⭐ BARU 20Sep26 | **14 LULUS** |
| **WEB — normalitas (slider 2 arah) + pintasan hetero** ⭐ BARU 20Sep26 | **57 LULUS** |
| **DIAGNOSIS — mesin SPSS & PLS (6+5 uji)** | **23 LULUS** |
| **DIAGNOSIS — teks 'cara membetulkan' 11 masalah** | **63 LULUS** |
| **DIAGNOSIS — jalur web (unggah → periksa → hasil)** | **37 LULUS** |
| **ALAT UKUR UJI — terbukti BISA GAGAL** | **9 LULUS** |
| ⭐ **GRAFIK — bahan gambar dari mesin (P-P, histogram, scatter)** | **33 LULUS** |
| ⭐ **GRAFIK — fungsi SVG dari data** | **24 LULUS** |
| ⭐ **GRAFIK — sampai ke halaman /klinik (jalur API)** | **18 LULUS** |
| ⭐ **GRAFIK — tombol contoh + tab Baca Grafik (jalur mahasiswa)** | **16 LULUS** |
| ⭐ **GRAFIK — uji grafiknya sendiri terbukti BISA GAGAL** | **22 LULUS** |
| ⭐ **PERAN — periksa penandaan + skor konstruk (murni)** ⭐ BARU 21Sep26 | **35 LULUS** |
| ⭐ **PERAN — skor konstruk: gabung kolom seperan** ⭐ BARU 21Sep26 | **35 LULUS** |
| ⭐ **PERAN — rute web periksa-peran (HTTP sungguhan)** ⭐ BARU 21Sep26 | **30 LULUS** |
| ⭐ **PERAN — alur halaman: unggah → peran → Hasil** ⭐ BARU 21Sep26 | **20 LULUS** |
| ⭐ **PERAN — peran sampai ke MESIN sebagai skor konstruk** ⭐ BARU 21Sep26 | **15 LULUS** |
| ⭐ **MESIN — S3 berantai dari pintu produksi** ⭐ BARU 21Sep26 | **LULUS** |
| ⭐ **KAITAN — mediasi & moderasi, mesin murni** ⭐ BARU 21Sep26 | **LULUS** |
| ⭐ **KAITAN — mediasi & moderasi sampai ke HASIL (pintu produksi)** ⭐ BARU 21Sep26 | **LULUS** |
| **Total** | **60 grup, SEMUA LULUS** |

### ⭐ TAHAP 2.1 SELESAI & LIVE (20Sep26) — GRAFIK HIDUP + TAB "BACA GRAFIK"

7 grafik SVG **statis** di `/syarat` → **grafik hidup** di `/klinik`
(dihitung dari data mahasiswa) + tab ke-3 BELAJAR **"Baca Grafik"**.
`/syarat` **dialihkan 308** → `/belajar#tab-3` (tautan lama tidak patah) · **menu 8 → 7**.

- **Mesin bahan gambar** — `app/diagnosis.py` hanya **MENAMBAH** kunci `titik`
  (`{zpred, zresid, pp, hist, xy}`) dari angka yang **sudah** dihitung → **NOL rumus statistik baru**.
- **Fungsi gambar** — `app/static/grafik_hidup.js` (`petakan` · `indeksSebar` · `ambilPada` ·
  `svgHetero` · `svgPP` · `svgHistogram` · `svgLinear`; `BATAS_TITIK = 500`).
  ⚠️ WAJIB dimuat di `<head>` `dasar.html` — kalau sebelum `</body>` jatuh SETELAH `{% block skrip %}` → mati senyap.
- **2 tombol contoh** — *"Coba contoh data yang sehat"* / *"Lihat contoh data bermasalah"*.
- **Uji:** `uji_bahan_gambar.py` 33 · `uji_grafik_hidup.js` 24 · `uji_web_grafik.py` 18 ·
  `uji_tombol_contoh.py` 15 · `uji_tab_baca_grafik.py` 16 · `uji_alat_ukur_grafik.py` 22 (**terbukti BISA GAGAL**).
- Dokumen: `DOKUMENTASI_TAHAP_2_GRAFIK_HIDUP_20SEP2026.md`.

⚠️ **AKAR TERPENTING (ketemu dari uji-suntik, bukan dari membaca kode):**
`svgHetero`/`svgPP`/`svgLinear` dulu memakai `const n = zp.length` — panjang **satu** larik,
padahal dua larik bisa **beda panjang** → titik `NaN` **HILANG tanpa galat apa pun**;
pada data >500 baris jumlah titik **melampaui batas jaga** (terukur **5000** padahal 500).
BENAR: `const n = idx.length`.

⚠️ **BUG LAMA yang ikut ditutup:** `n is not defined` — ada di **cadangan baris 400 SEBELUM Tahap 2**;
halaman `/klinik` **mati** tiap habis unggah, mahasiswa cuma lihat *"Koneksi ke server terputus"*.

### TAHAP 1.6 SELESAI (20Sep26) — NORMALITAS + TOMBOL PINTASAN HETERO
`/belajar` tab **Materi & Kamus** = **8 tombol** (dulu 7):
`Heteroskedastisitas` · `β` · `p-value` · `R²` · `VIF` · `Alpha` · `Uji t` · ⭐**`Normalitas`**
- **Heteroskedastisitas** — slider tetap **+ 2 tombol** `Contoh sehat` / `Contoh sakit`
  (menyala otomatis mengikuti posisi slider).
- **Normalitas** — slider **DUA ARAH** `−100…+100` (miring kiri ↔ lonceng ↔ miring kanan),
  gambar histogram 21–22 batang.
- **Kalimat penegas HIDUP** — fungsi `kalimatTafsir()` mengganti kalimat pita mengikuti
  slider: *"**Tidak ada corong — justru ini yang bagus**"* (hetero, 0–17) dan
  *"**Tidak ada kemiringan — justru ini yang bagus**"* (normalitas, |v| < 18).
  Entri lain **tidak tersentuh**.
- Judul tab uji t: `Uji t: signifikan kok negatif?` → **`Uji t: masalah uji t`**.

⚠️ **AKAR: slider dulu milik BERSAMA** (`min="0" max="100"` dipaku). Normalitas butuh
rentang sendiri → `pilih()` kini menyetel `slider.min`/`slider.max` dari
`kk.min`/`kk.maks` **per-entri**. Terbukti entri lama tetap 0…100 (`uji_normalitas.py` bagian 6).

⚠️ **AKAR TERBESAR: satu `}` hilang mematikan SELURUH halaman.** Skrip sisip
(`sisip_kamus_normalitas.py`) memakai penanda `"  },\n  beta: {\n"` → `replace()`
menghapus penutup entri `hetero` → `SyntaxError: Unexpected identifier 'normalitas'`
→ **50.177 karakter skrip MATI**, halaman tetap **HTTP 200**, konsol hanya 404 favicon.
Perbaikan: tambah `},` penutup entri hetero.
**Gerbang BARU grup ke-25 `gerbang_sintaks_js.py`** menutup lubang ini
(render Jinja → `node --check` tiap `<script>` inline; **terbukti BISA GAGAL**).
Dokumen: `DOKUMENTASI_TAHAP_1_6_NORMALITAS_20SEP2026.md`.

### TAHAP 1.5 SELESAI (19Sep26) — DIAGNOSIS DATA SPSS & PLS
`/diagnosis` (alias `/klinik`) = **ALAT**: unggah `.sav`/`.csv`/`.xlsx`
(maks 10 MB) → periksa → jawab BENAR/SALAH + **cara membetulkan**.
- **Mode SPSS (6):** normalitas · heteroskedastisitas (Glejser) · VIF ·
  linearitas · outlier · Durbin-Watson
- **Mode SmartPLS (5):** outer loading · AVE · composite reliability · VIF inner ·
  Fornell-Larcker
- **11 nasihat** (`app/nasihat.py`): arti · kenapa · kapan boleh diabaikan ·
  langkah bernomor · yang JANGAN dilakukan
- **Nama menu:** `KLINIK` → **DIAGNOSIS DATA** (slug TETAP `klinik`);
  `PERIKSA SYARAT` → **KAMUS GRAFIK** (`/syarat` dibiarkan)
- **Nasihat WAJIB hangat** — dilarang `PERINGATAN/GAGAL/BAHAYA/ANDA HARUS`
- Detail: `DOKUMENTASI_TAHAP_1_5_DIAGNOSIS_19SEP2026.md`

### 📌 ATURAN BARU (19Sep26, dari teguran Bos)
1. **`grep "^def"` sebelum memanggil fungsi** — jangan tebak nama parameter
   (9 nama salah tebak = 2 putaran HTTP 500).
2. **Sebelum menulis alat: CARI alat yang sudah ada.** Bos: *"cek dulu alat yang
   dipakai kemarin, jangan buat-buat script, semua sudah ada."*
3. **Gerbang ikon WAJIB memindai `app/main.py`** juga (daftar `MODUL`), bukan
   hanya `templates/*.html` — 8 pemakaian pernah luput.
4. **Baca dokumen keputusan sebelum mengubah nama/slug.**

**TEMUAN 18Sep26 (audit mesin) — bug tersembunyi berhari-hari:**
`item_per` diambil dari **nilai bawaan (4)**, bukan dari bentuk data. Kalau pemanggil
memakai `item_per=3` → `IndexError` → **4 bentuk moderasi mustahil dibangun** dan
**tidak ada yang tahu** (semua uji lama memakai 4). **Ditutup di 3 berkas:**
`berurutan.py` · `generator.py` · `struktural.py`. Aturannya: **ukur dari data,
jangan percaya nilai bawaan.**

**3 temuan baru yang mengubah mesin** (detail: `DOKUMENTASI_MESIN_DATA_17SEP2026.md`
& skill `statistik-lab`):

1. **Derau otomatis 0,5/1,0 → 0,6.** Aturan lama "2 saudara → 1,0" memperbaiki
   dual mediasi tapi **MERUSAK HOC** (galat 0,0644). **0,6 aman semua bentuk.**
2. **Interaksi harus masuk ke target masing-masing.** Versi lama hanya ke `Y`
   → moderasi jalur-a mati (`X1×Z1→M` −0,0122). Berkas baru:
   `app/hitung/spek_pembangun.py` → `X1×Z1→M` **0,2372** ✅
3. **Rumus VIF harus bentuk matriks.** Asumsi seragam mentok 9,01 → ganti →
   VIF **15,07** terdeteksi ✅

**Berkas baru:** `app/hitung/kelayakan.py` (pemeriksa kelayakan setelan) ·
`app/hitung/spek_pembangun.py` (interaksi di target mana pun) ·
`uji_kelayakan.py` (19 LULUS) · `uji_model_lanjutan.py` (10 LULUS).

**Setelan mustahil DITOLAK JUJUR** — 8 prediktor total β=2,52 → R²=1,94 (mustahil)
→ tolak + sarankan β wajar. Aturan: R² wajar 0,25–0,60 (ilmu sosial).

---

- **Pemilik:** Bos (dosen Statistik Penelitian)
- **Asisten:** Wulan

---

## 1. APA INI

Media pembelajaran statistik penelitian berbasis **browser web** untuk:
1. **Latihan SPSS** — mahasiswa mengolah data hasil simulasi.
2. **Latihan SEM-PLS** — jalur, medi asi, moderasi.
3. **Contoh mengajar** — Bos mengajar statistik penelitian.
4. **Modul kualitatif** (menyusul, mesin berbeda).

**Nama tampil:** "Penelitian STATISTIK Lab."
**Domain rencana:** `statistik.bikinaja.id`
**Kontainer:** `simulasi-olah-data` (port **8120**, bridge default)
**Deploy:** pola `jalankan.sh` seperti EduAi & Bayana

---

## 2. KEPUTUSAN TERKUNCI (jangan diubah tanpa ACC Bos)

| # | Keputusan | Nilai |
|---|---|---|
| 2.1 | Bentuk | Web browser, simple, menarik, interaktif |
| 2.2 | Hitungan statistik | **LOKAL (numpy/pandas)** — TANPA AI, gratis, instan |
| 2.3 | AI | HANYA interpretasi + generate soal. Sumber **9router**. **Tombol ON/OFF** wajib |
| 2.4 | AI OFF | Ujian tetap jalan lewat **bank soal statis** (jangan mati total) |
| 2.5 | Login | Tidak dibatasi saat develop; **kerangka autentikasi disiapkan dari awal** |
| 2.6 | Tema | **Terang-warm** (BUKAN gelap-cinematic) |
| 2.7 | Bahasa | Indonesia akademik |
| 2.8 | Ikon | **Sprite SVG Lucide/custom** — JANGAN emoji standar |
| 2.9 | Output laporan | `.docx` + `.pdf`; data `.csv`/`.xlsx` |
| 2.10 | Etika | Wajib label **"data simulasi"** di semua keluaran |

---

## 3. MODUL (6 buah)

| # | Modul | Isi | Status |
|---|---|---|---|
| A | 📚 **BELAJAR** | Kamus interaktif berslider **8 istilah** (hetero, β, p-value, R², VIF, alpha, uji t, normalitas) — **3 tab**: *Materi & Kamus* · *Ruang Uji* · ⭐**Baca Grafik** | ✅ **LIVE 20Sep26** |
| B | 🧪 **BUAT DATA** | Setelan → generate → verifikasi hasil · **13 bentuk model terbuka** di UI (Tahap 1.3) | **mesin selesai** |
| C | 🩺 **KLINIK / DIAGNOSIS DATA** | Unggah `.sav`/`.csv`/`.xlsx` → 6 uji SPSS + 5 uji SmartPLS + 11 nasihat; **grafik hidup** dari data | ✅ **LIVE 20Sep26** |
| D | 🎓 **UJIAN** | Soal AI, individual & kelompok, 3 mode | belum |
| E | 🧭 **PEMILIH ALAT** | Kasus → pilih SPSS/PLS/Kualitatif + alasannya | belum |
| F | ⚙️ **PENGATURAN** | **Tombol AI ON/OFF** ✅ sudah ada sejak Fase 1 · **login** belum | sebagian |
| — | Kualitatif | Transkrip/tema/keabsahan | **menyusul** |

---

## 4. ARSITEKTUR MESIN DATA (INTI — SUDAH TUNTAS)

### 4.1 Alur

```
LEMBAR SETELAN  →  BANGUN BERURUTAN  →  TURUN KE ITEM  →  RASA LAPANGAN  →  VERIFIKASI
   (Bos isi)        (induk→anak)        (Likert 1-5)      (bolong/asak)     (ukur ulang)
```

### 4.2 Modul mesin

| Berkas | Fungsi | Status |
|---|---|---|
| `app/hitung/berurutan.py` | **INTI** — bangun dari induk ke anak + koreksi atenuasi | ✅ FINAL |
| `app/hitung/kalibrasi_jalur.py` | **INTI** — kalibrasi iteratif per-jalur, 2 mode, **menerima `interaksi`** | ✅ FINAL |
| `app/hitung/spek_pembangun.py` | **INTI (BARU)** — `bangun_dari_spek(spek)` bentuk **apa pun** + interaksi di **target mana pun** | ✅ FINAL |
| `app/hitung/kelayakan.py` | Pemeriksa kelayakan setelan (R², VIF, saran β) | ✅ FINAL |
| `app/hitung/mesin.py` | Pembaca hasil (SPSS & PLS), matriks korelasi (pendekatan lama) | dipakai untuk `uji_spss`/`uji_pls` |
| `app/hitung/generator.py` | Pendekatan v3 (matriks korelasi tervalidasi) — dipertahankan sebagai alternatif | arsip teknis |
| `app/hitung/struktural.py`, `kalibrasi.py`, `setel.py` | Pendekatan lama (matriks korelasi, kalibrasi global) | **arsip** — jangan dipakai untuk hal baru |

### 4.3 EMPAT AKAR YANG HARUS DIINGAT (semua TERUKUR)

> Empat ini yang membuat 18 putaran gagal, lalu berhasil. **JANGAN diubah tanpa mengulang uji.**

**(A) Bangun BERURUTAN, bukan dari satu matriks korelasi.**
Membangun semua variabel sekaligus dari satu matriks korelasi membuat matriks itu **mendesak batas positive-definite** saat koefisien/korelasi besar → koefisien bergeser tak terkendali (*suppression effect*). Terukur: minta 0,35/0,45/0,30 keluar 0,30/0,40/0,09.

**(B) JANGAN standardisasi ulang variabel ENDOGEN.**
`Y = lin + error` lalu dibagi `SD(Y)` membuat **semua koefisien menyusut proporsional** — dan susutnya beda tiap konstruk sehingga **tak bisa ditutup satu rumus**.
✅ Yang benar: eksogen `X` terstandardisasi (varians 1); endogen `M`/`Y` **dibiarkan apa adanya**; sumber berskala 1 → koefisien terbaca = bobot yang dipasang.

**(C) TIAP konstruk WAJIB punya generator acak (`rng`) SENDIRI.**
Kalau semua memakai `rng` bersama, urutan pemanggilan `rng.normal()` membuat derau antar-konstruk **saling bergeser** → **koefisien BERPINDAH KOLOM**.
Terukur: `M1->Y` keluar **0,0013** padahal minta 0,35; nilai **0,35 muncul di M2**, nilai **0,20 muncul di M3**.
Setelah rng dipisah: **0,3509 / 0,1978 / −0,1491** (galat < 0,003).

**(D) Derau OTOMATIS dari struktur model.**
Kalau beberapa variabel lahir dari **INDUK yang sama** (mis. `X→M1`, `X→M2`), mereka jadi **hampir kembar** bila derau kecil → regresi berganda **tidak bisa memisahkan** → bobot **mentok di batas** (terukur: bobot M1 mentok 0,98, hasil tetap 0,2948 padahal minta 0,40).
✅ Perbesar derau sesuai jumlah "saudara": **1 saudara → 0,5 · 2 saudara → 1,0 · 3 saudara → 1,2**.
Terukur: derau 0,5 → galat **0,1052** (gagal) vs derau 1,0 → galat **0,0099** (berhasil, 6 putaran).

### 4.4 KOREKSI ATENUASI (rumus inti)

Masuk ke item Likert **menyusutkan** koefisien dengan rasio **seragam ~0,78** (terukur: a 0,60→0,4732 = 0,789 · b 0,40→0,3056 = 0,764).
Mendekati **√(alpha)**. Maka:

```
b_bangun = b_minta / ρ      dengan ρ = √(alpha_sumber · alpha_target)
```

**Alpha ditentukan DI AWAL** (`alpha_rencana`) dan **DIPAKSA tetap** antar-putaran kalibrasi — kalau alpha berubah tiap putaran, kalibrasi **tidak akan pernah konvergen**.

### 4.5 DUA MODE (ACC Bos — Opsi C)

| Mode | Cara | Galat terukur | Kegunaan |
|---|---|---|---|
| 🎯 **PRESISI** | `kalibrasi_per_jalur()` — ukur → koreksi → ulangi | **0,029** (model 12 hipotesis) | Bikin soal & **kunci jawaban** |
| 🌿 **NATURAL** | sekali bangun, tanpa kalibrasi | ±0,19 (arah tetap benar) | Mengajar **galat pensampelan** |

Masuk lewat `bangun_dengan_mode(mode, **kw)`.

### 4.6 KALIBRASI PER-JALUR (cara yang bekerja)

```
1. Kelompokkan langkah per TARGET (satu target = satu regresi).
2. Urutkan: target dengan sumber paling sedikit didahulukan.
3. Bangun → UKUR pakai ukur_jalur() (skor item → regresi terstandardisasi = cara SPSS).
4. Geser bobot 0,85 × galat (clip ±0,98).
5. Ulangi sampai galat maks ≤ toleransi atau batas putaran.
```

**Kenapa per-jalur, bukan global:** pada 17 putaran sebelumnya, mengoreksi semua bobot bersamaan **membaikkan satu jalur & merusakkan yang lain** (= menambal). Mengukur per-jalur memberi **ukuran tunggal** yang menunjukkan mana yang harus digeser.

---

## 5. HASIL UJI (BUKTI NYATA)

### 5.1 `uji_kalibrasi_jalur.py` — 29 LULUS / 0 GAGAL

| Model | Status |
|---|---|
| Regresi linear sederhana (1 X) | ✅ |
| Regresi linear berganda (3 X) | ✅ |
| Mediasi tunggal (X→M→Y) | ✅ |
| Dual mediasi paralel | ✅ |
| Mediasi berjenjang (X→M1→M2→Y) | ✅ |

### 5.2 MODEL JURNAL BOS — 13/13 jalur, galat maks **0,029**

Model: *Model of Goal-Directed Student Decision Quality in Choosing a University*
9 konstruk · 12 hipotesis · 4 tingkat · 1 jalur NH · 2 keluaran paralel

| Jalur | Minta | Terukur | Galat |
|---|---|---|---|
| SelfEfficacy→Mastery | 0,45 | 0,4212 | −0,0288 |
| SelfEfficacy→PerfApproach | 0,35 | 0,3432 | −0,0068 |
| SelfEfficacy→PerfAvoid (NH) | 0,10 | 0,1008 | +0,0008 |
| Mastery→PosAffect | 0,35 | 0,3565 | +0,0065 |
| PerfApproach→PosAffect | 0,20 | 0,1975 | −0,0025 |
| PerfAvoid→PosAffect | −0,15 | −0,1500 | +0,0000 |
| Mastery→DecConf | 0,30 | 0,2988 | −0,0012 |
| PerfApproach→DecConf | 0,25 | 0,2501 | +0,0001 |
| PerfAvoid→DecConf | −0,20 | −0,2081 | −0,0081 |
| PosAffect→DecSatis | 0,40 | 0,4002 | +0,0002 |
| DecConf→DecSatis | 0,35 | 0,3610 | +0,0110 |
| DecSatis→Loyalty | 0,50 | 0,5010 | +0,0010 |
| DecSatis→Switching | −0,30 | −0,3025 | −0,0025 |

**Selesai dalam 4 putaran.**

### 5.3 `uji_penutup.py` — 7 LULUS / 0 GAGAL

Mode Presisi (galat 0,029) · Mode Natural (arah benar) · Sampel kecil 50/100/150/200 (**signifikansi SELALU benar**).

| n | Galat maks (presisi) | Signifikansi |
|---|---|---|
| 50 | 0,0991 | ✅ BENAR |
| 100 | 0,0180 | ✅ BENAR |
| 150 | 0,0161 | ✅ BENAR |
| 200 | 0,0207 | ✅ BENAR |

---

## 6. BATAS JUJUR (sampaikan terbuka di aplikasi)

### 6.1 BISA ✅ — **10 BENTUK TERUKUR** (`audit_mesin.py`, 10 LULUS / 0 GAGAL)

| Bentuk | Galat maks |
|---|---|
| Regresi sederhana (1 X → Y) | 0,0067 |
| Regresi berganda (n X → Y) | 0,0026 |
| Mediasi tunggal (X → M → Y) | 0,0171 |
| Dual mediasi **paralel** | 0,0049 |
| Mediasi **berjenjang** (X→M1→M2→Y) | 0,0092 |
| Moderasi **MRA** (X, Z, X×Z → Y) | 0,0081 |
| **Dual** moderasi (X×Z1 & X×Z2 → Y) | 0,0130 |
| **Moderated** mediation (M×Z → Y) | 0,0258 |
| Moderasi di **jalur-a** (X×Z → M) | 0,0075 |
| Model **4 tingkat**, 2 keluaran | 0,0044 |

Plus: PLS-SEM reflektif · path analysis · multi-group · konstruk formatif ·
second-order (HOC) · 2–8 X · **30–2.000 responden**.

✅ **WEB sudah membuka 13 bentuk** (Tahap 1.3, 19Sep26): Regresi 3 sub · Mediasi 4 sub ·
Moderasi 6 sub · Campuran (`?model=gabungan`). Mesin sanggup **lebih dari 13** —
yang belum dibuka sebagai pintu: MANOVA (bahasan ditutup, lihat `RUANG_MANOVA.md`).

⚠️ **PERUBAHAN 21Sep26 — kartu Regresi DISUSUN ULANG (ACC Bos, N1+R1+P1):**
Dari 3 sub (sederhana/berganda/berantai) → **2 sub**:
- ① **Parsial** — banyak X → Y, diuji satu-satu (X1→Y, X2→Y, … X8→Y)
- ② **Berganda** — **Parsial + Simultan** (dua-duanya ditampilkan)

Kartu **"berantai" DIARSIPKAN** (bukan dihapus): kode `cara='berantai'` tetap ada di
mesin dan `gerbang_s3.py` tetap SAH, hanya **tidak ditampilkan** di pintu.
Alasan: "berantai" lahir dari kebingungan mencari **parsial** yang tak pernah
ditampilkan — bukan dari kebutuhan keilmuan. Detail: `KEPUTUSAN_PARSIAL_SIMULTAN_21SEP2026.md`.

⚠️ **UJI F BELUM ADA di mesin** (grep `uji_f|anova|f_stat` = kosong; yang ada hanya R²).
Rencana: ditambahkan sebagai **Langkah 2** keputusan 21Sep26. Selama belum ada,
kartu ② **belum bisa** mengatakan "semua X secara simultan berpengaruh".

### 6.2 TIDAK BISA ❌
Kualitatif (di modul A — modul B menyusul) · longitudinal/panel · multilevel · SEM kovarians (AMOS/LISREL) · survival analysis · mix-method · Monte Carlo penuh · meta-analisis.

### 6.3 BATAS YANG HARUS DIKATAKAN TERBUKA

- **Rentang responden: 30–2.000** (web sudah mendukung sampai 2.000).
- **Sampel kecil (<100):** **signifikansi** dijamin benar; **koefisien** bergeser ±0,06–0,10.
  Alasannya **hukum statistik**: σ koefisien ≈ 1/√n. Pada n=50 → ±0,14 kemungkinan.
  *Ini justru pelajaran berharga* — data lapangan asli pun begitu.
- **Koefisien persis di n kecil = mustahil** (bukan kelemahan aplikasi).
- **Multikolinearitas** (korelasi antar-X > 0,6) → koefisien tidak stabil. Itu masalah **nyata**, bukan bug. Tampilkan peringatan VIF.

### 6.4 ETIKA

- **Natural** (meniru kerumitan data nyata) = **SAH**.
- **"Dipoles"** (mengubah kesimpulan) = **FABRIKASI** — dilarang.
- Wajib label **"data simulasi"** di setiap keluaran.
- Default: **1–2 dari 5 hipotesis sengaja tidak signifikan** (supaya realistis).

---

## 7. LEMBAR SETELAN (5 bagian)

1. **Model** — X **1–8** (slider; sederhana terkunci 1) · **M (perantara)** ikut kartu model yang dipilih (maks **2**: paralel M1+M2 / berjenjang M1→M2) · Z (moderasi) Ya/Tidak · hipotesis otomatis
2. **Pengukuran** — item 3/4/5 · Likert 1-5 / 1-7 · responden **30–2.000**
3. **Hasil per jalur** — SIGNIFIKAN · MARGINAL · TIDAK SIGNIFIKAN · SANGAT SIGNIFIKAN
4. **Rasa lapangan** — derau 25–35% · straight-lining 5–10% · data kosong 1–3% · ekstrem 2–5%
5. **Sakit sengaja** — alpha 0,55 · VIF>10 · tidak normal · heteroskedastisitas · loading<0,7 · outlier · heterogen multigroup

**Ambang signifikansi:**

| Sebutan | p | t |
|---|---|---|
| SANGAT SIGNIFIKAN | < 0,001 | > 3,3 |
| SIGNIFIKAN | < 0,05 | > 1,96 |
| **MARGINAL** | 0,05–0,10 | 1,65–1,96 |
| TIDAK SIGNIFIKAN | > 0,10 | < 1,65 |

---

## 8. KELUARAN PAKET

`data_spss.csv` / `.xlsx` · `data_pls.csv` · `LAPORAN.docx` / `.pdf` (tabel + interpretasi + R²/Q²/f²/VIF + uji asumsi) · **`KUNCI_JAWABAN.docx`** (khusus pengajar) · `LEMBAR_SETELAN.pdf` · opsional `bahan_ajar.pptx` · `kode_uji.R`/`.py`

---

## 9. URUTAN TAHAP

| Tahap | Isi | Status |
|---|---|---|
| 1 | Kontainer + beranda + BELAJAR + BUAT DATA (3X+1Y) | ✅ **SELESAI 17Sep26** |
| 2 | Periksa Syarat: grafik hidup + tab "Baca Grafik" (SPSS & PLS) | ✅ **2.1 SELESAI & LIVE 20Sep26** |
| 3 | Klinik data sakit + kunci jawaban | ⬜ berikutnya (2.2 Linearitas · 2.4 Khas PLS) |
| 4 | **Pemilih alat** — mahasiswa tahu pilih SPSS atau SmartPLS | ⬜ |
| 5 | Ujian (individual/kelompok) | ⬜ |
| 6 | Modul kualitatif | ⬜ |
| 7 | Login | ⬜ |

> ⚠️ **Urutan ini DISAMAKAN dengan `TAHAP_PENYELESAIAN.md`** (20Sep26).
> Sebelumnya berkas ini menaruh Ujian di 4, Pemilih alat di 5, Login di 6,
> Kualitatif di 7 — **bertabrakan** dengan `TAHAP_PENYELESAIAN.md`.
> Alasan urutan sekarang: **Pemilih alat = tujuan utama Bos sejak awal**
> (*"mahasiswa tahu pilih SPSS atau PLS"*) → dikerjakan lebih dulu;
> **Login paling akhir** karena Bos: *"login tidak dibatasi saat develop,
> saat sudah fix baru dipasang login."*
> SOT (`sot.py --periksa`) **menjaga** kedua dokumen tetap sama.

---

## 10. CARA MENJALANKAN UJI

```bash
cd /opt/data/services/statistik-lab

# ⭐ SOT — keadaan terkini (DIHITUNG dari kode, bukan dihafal)
.venv/bin/python sot.py            # cetak ringkasan
.venv/bin/python sot.py --periksa  # + periksa dokumen selaras kode

# audit mesin — 10 bentuk model (10 LULUS / 0 GAGAL)
.venv/bin/python audit_mesin.py

# inti — semua model (29 LULUS / 0 GAGAL)
.venv/bin/python uji_kalibrasi_jalur.py

# model jurnal Bos (12 hipotesis)
.venv/bin/python uji_jurnal.py

# penutup — 2 mode + sampel kecil (7 LULUS / 0 GAGAL)
.venv/bin/python uji_penutup.py
```

**Tentukan LULUS/GAGAL dari EXIT CODE** (0 = aman), JANGAN grep teks.

---

## 11. ARSIP — PENDEKATAN YANG GAGAL (jangan diulang)

| Pendekatan | Berkas | Kenapa gagal |
|---|---|---|
| Matriks korelasi langsung | `mesin.py` | Mendesak batas positive-definite |
| Model struktural langsung | `struktural.py` | Y distandardisasi setelah error → menyusut |
| Kalibrasi global iteratif | `kalibrasi.py` | **BERAYUN** — bolak-balik 2 nilai, tidak konvergen |
| Matriks tervalidasi + pilih seed | `generator.py` | Koreksi saling berebut antar variabel |
| Kalibrasi global atas skor item | `setel.py` | Memperbaiki satu, merusak yang lain |

**Pelajaran:** selama **17 putaran**, Wulan mengubah **rumus koreksi** — padahal masalahnya di **urutan pembangunan** & **rng bersama**. **Ganti pendekatan, bukan menambal.**
