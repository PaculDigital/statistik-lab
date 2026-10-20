# 🗺️ TAHAP PENYELESAIAN — PENELITIAN STATISTIK LAB.

> Disusun 19 Sep 2026 dari **fakta kode** (`sot.py`, `audit_mesin.py`, rute `app/main.py`).
> Berkas ini **PETA JALAN**, bukan keputusan. Bos yang menentukan urutan & ACC.

---

## 📊 POSISI KINI (terukur 21 Sep 2026, kedua)

> ⚠️ **Baris di bawah INI dulu "POSISI AWAL 19Sep26"** — sudah usang.
> Diperbarui 21Sep26 dari fakta kode. **Jangan** pakai angka lama.

| Lapisan | Keadaan |
|---|---|
| **Mesin** | ✅ **sangat sakti** — 10 bentuk model terbukti (`audit_mesin.py` 10 LULUS/0 GAGAL, galat 0,0026–0,0258) |
| **Halaman jadi** | ✅ **8 halaman LIVE** (`/` `/mulai` `/kuantitatif` `/belajar` `/buat-data` `/klinik` `/pengaturan` + `/segera/*`) |
| **Menu kosong** | ❌ **UJIAN** · **PEMILIH ALAT** (2 dari 7 modul) |
| **KLINIK** | ✅ **LIVE sejak Tahap 1.5** — unggah .sav/.csv/.xlsx (maks 10 MB) → **6 uji SPSS + 6 uji PLS** + 11 nasihat · **+ IDENTIFIKASI DATA** (mahasiswa tandai PERAN kolom, 21Sep26) |
| **Gerbang uji** | ✅ **60 grup EXIT 0** · rc **77 = LEWAT prasarana** (bukan GAGAL) |
| **Pintu web** | ✅ **14 bentuk terbuka** (bukan lagi 3) — 4 kartu induk → sub-pilihan |
| **/syarat** | ✅ dialihkan **308 → `/belajar#tab-3`** (tab ke-3 "Baca Grafik") — **JANGAN dihapus** |
| **Beranda** | ✅ **ringkas** (21Sep26) — alur 5 langkah & kartu simulasi DIBUANG · "Tujuh modul, satu atap" |
| **Skor konstruk** | ✅ **per-konstruk** (21Sep26) — `X1` = 3 kolom → **1 skor**. Jawaban kosong = **Opsi B** (rata² terjawab × jumlah item). Belum deploy |

**Diagnosis:** *pintu sudah lebar; yang kurang = **KLINIK isi (data sakit + kunci jawaban)** dan 2 menu kosong.*

> 📌 **Asal baris usang (untuk jejak):** "5 halaman · menu kosong KLINIK · 3 dari 10 bentuk · 23 grup" — itu keadaan **19Sep26**, benar saat itu.

---

# 🎯 TAHAP 1 — LEBARKAN PINTU (mesin → layar)

**Sasaran:** mahasiswa bisa memakai **semua 10 bentuk model** dari web, bukan cuma 3.

| Langkah | Kerjaan | Bukti selesai |
|---|---|---|
| 1.1 | ✅ **Format unduhan SPSS / PLS** — pilih: nama panjang (SPSS) atau kode pendek (PLS: KP1, H1, Y1) + pemisah kolom | unduh 2 format, isinya beda & benar |
| 1.2 | ✅ **Mode 1-model-1-jalur** `/buat-data?model=mediasi` — sembunyikan yang tak perlu, tampilkan hanya jalur model itu | tiap kartu `/kuantitatif` membawa ke form yang BEDA |
| 1.3 | ✅ **SELESAI 19Sep26** — **13 bentuk terbuka** (dari 3): 4 kartu induk → klik → sub-pilihan. Regresi 3 · Mediasi 4 · Moderasi 6 | `uji_sub_regresi.py` **46 LULUS/0 GAGAL**; gerbang **19 grup LULUS (saat itu)**; 11 slug terbukti menerapkan jalur; deploy 16–20 EXIT 0 |
| 1.4 | ✅ **SELESAI 19Sep26** — **Bar "Model kamu sekarang" + tombol Ganti model** selalu terlihat (menempel). Tanpa `?model=` → diarahkan balik ke `/kuantitatif` (JANGAN terka) | `uji_bar_model.py` **32 LULUS/0 GAGAL**; *terbukti menempel top=0 saat scroll*; vision OK; halaman tidak bisa digeser samping (390 ≤ 390). **+ 8 ikon kosong ditutup** (gerbang ikon baru) |
| 1.5 | ✅ **SELESAI 19Sep26** — **DIAGNOSIS DATA SPSS & PLS**: menu KLINIK diganti nama + diisi ALAT unggah data (`.sav`/`.csv`/`.xlsx`) → diagnosa (6 uji SPSS + 5 uji PLS) → **cara membetulkan** (11 masalah). Menu PERIKSA SYARAT → **KAMUS GRAFIK** | `uji_diagnosis.py` **23 LULUS** · `uji_nasihat.py` **63 LULUS** · `uji_web_diagnosis.py` **37 LULUS** · `uji_alat_ukur.py` **9 LULUS** · gerbang **23 GRUP · EXIT 0** (saat itu) · deploy EXIT 0 · vision rapi · data bersih (0 masalah) vs sakit (3 masalah) **terbukti berbeda**. Dok: `DOKUMENTASI_TAHAP_1_5_DIAGNOSIS_19SEP2026.md` |
| 1.6 | ✅ **SELESAI 20Sep26** — **NORMALITAS + TOMBOL PINTASAN HETERO**: kamus jadi **8 tombol** (+`Normalitas`, slider **dua arah** −100…+100) · hetero dapat **2 tombol pintasan** `Contoh sehat`/`Contoh sakit` · **kalimat penegas HIDUP** (`kalimatTafsir()`) *"tidak ada corong/kemiringan — justru ini yang bagus"* · judul tab uji t → `Uji t: masalah uji t` | `uji_normalitas.py` **57 LULUS/0 GAGAL** · `gerbang_sintaks_js.py` **14 LULUS** (grup ke-25, **terbukti bisa gagal**) · gerbang **26 GRUP · EXIT 0** · deploy **EXIT 0** · verifikasi produksi **18 LULUS**. Dok: `DOKUMENTASI_TAHAP_1_6_NORMALITAS_20SEP2026.md` |

**Catatan 1.3 (19Sep26):** kartu **Campuran** belum punya sub-pilihan (masih langsung
ke `/buat-data?model=gabungan`). Tiga bentuk moderasi yang dulu "belum teruji"
(**jalur-b**, **keduanya**, **3-jalur**) kini **TERBUKTI JALAN** — bug `item_per`
18Sep26 sudah tidak menggigit. Moderasi 3-jalur galat 0,0362 (dekat batas 0,04).
📄 Detail: `DOKUMENTASI_TAHAP_1_3_19SEP2026.md`

**Tahap 1 selesai =** mahasiswa awam bisa membuat data untuk model apa pun tanpa tahu istilah β.

---

# 🎯 TAHAP 2 — PERIKSA SYARAT LENGKAP

**Sasaran:** halaman PERIKSA SYARAT menampilkan **grafik SPSS + khas PLS** dengan cara membacanya.

| Langkah | Kerjaan | Bukti selesai |
|---|---|---|
| **2.1a** ✅ | **Mesin bahan gambar** — `titik.pp/hist/xy/zpred/zresid` dihitung dari angka yang sudah ada | ✅ `uji_bahan_gambar.py` **33 LULUS** (20Sep26) |
| **2.1b** ✅ | **Fungsi gambar hidup** — `app/static/grafik_hidup.js` (SVG dari data user) | ✅ `uji_grafik_hidup.js` **24 LULUS** · corong 1,3× lebih lebar (20Sep26) |
| **2.1c** ✅ | **Grafik sampai ke `/klinik`** — di bawah tabel angka, dari data yang diunggah | ✅ `uji_web_grafik.py` **18 LULUS** · mata: corong terlihat jelas (20Sep26) |
| **2.1d** ✅ | **2 tombol contoh** (sehat / bermasalah) + kolom terisi otomatis | ✅ `uji_tombol_contoh.py` **15 LULUS** (20Sep26) |
| **2.1e** ✅ | **Tab ke-3 BELAJAR "Baca Grafik"** — 7 kartu pindah dari `/syarat`; `/syarat` dialihkan 308; menu 8→7 | ✅ `uji_tab_baca_grafik.py` **16 LULUS** (20Sep26) |
| *(2.1)* | **Normalitas** — P-P/Q-Q plot + histogram residu | ✅ **grafik tampil** + tafsir "baca begini" |
| ~~2.2~~ ✅ | **Linearitas — scatter X vs Y** | ✅ **SUDAH ADA sejak Tahap 1.5** — `svgLinear` + tafsir + *"Cara membacanya"*; diuji di `uji_web_grafik.py` (baris 247 & 253) |
| ~~2.3~~ ✅ | **VIF + hetero** | ✅ **SUDAH ADA** — VIF SPSS (`vif_maks`) + VIF antar-variabel PLS (`vif_inner`) |
| ~~2.4~~ ✅ | **Khas PLS** — Outer Loading · AVE · Composite Reliability | ✅ **SUDAH ADA sejak Tahap 1.5** — tabel per konstruk + ambang (≥0,70 / ≥0,50 / ≥0,70) + daftar butir lemah |
| **2.4b** ✅ | **Fornell-Larcker + HTMT** | ✅ **SELESAI 20Sep26** — `uji_fornell_htmt.py` **10 LULUS/0 GAGAL** (rumus, fungsi asli) · `uji_web_fornell_htmt.py` **10 LULUS/0 GAGAL** (sampai `/klinik`) · kartu HTMT + nasihat *"Cara membacanya"* |
| **2.6** ✅ | **GERBANG BOCOR — 2 cacat uji ditutup** | ✅ **20Sep26** — (a) `uji_nasihat.py` & `uji_web_diagnosis.py` memaku angka **5 nasihat PLS** → GAGAL PALSU setelah HTMT masuk; kini menghitung dari KAMUS. (b) `ukur_tata.html` menembak `/buat-data` **tanpa `?model=`** → DIALIHKAN ke `/kuantitatif` (aturan Tahap 1.4) → pengukur mencari `#x-slider` di halaman yang salah → **"tombol tidak ditemukan" GAGAL PALSU 140 dtk**. Fix: `/buat-data?model=sederhana&uji=x8` |
| **2.7** ✅ | **IDENTIFIKASI DATA di `/klinik`** — mahasiswa **menandai PERAN** tiap kolom lewat dropdown (X1/X2… M1/M2… Z1/Z2… Y1/Y2…) → mesin **periksa 5 hal** → **SKOR KONSTRUK**: kolom seperan digabung jadi **satu skor** | ✅ **21Sep26** — `uji_peran_kolom.py` **35/0** · `uji_skor_konstruk.py` **35/0** · `uji_peran_web.py` **30/0** · `uji_peran_alur.py` **20/0** · `uji_peran_skor_e2e.py` **15/0** · gerbang **60 grup EXIT 0** · SOT selaras. **Terbukti:** prediktor mesin jadi `['X1','X2']` — **bukan** 5 kolom mentah · R² mesin 0,2543 = hitungan tangan |
| **2.8** ✅ | **PRASARANA ≠ MESIN** — Chrome CDP mati dulu dilaporkan *"GAGAL"* (Wulan mengejar bug yang tak ada) | ✅ **21Sep26** — `prasarana_uji.py` + `KODE_LEWAT = 77`. Chrome mati → gerbang **EXIT 0** *"60 grup · 6 lewat karena prasarana"*; GAGAL asli tetap **EXIT 1** |
| 2.5 | **Pemisah jelas: mana SPSS, mana PLS** | ⬜ tulisan, bukan mesin → jalan ke Tahap 4 |

> ⚠️ **KOREKSI 20Sep26:** 2.2, 2.3, 2.4 dulu ditandai ⬜ "belum" padahal **kode + halaman SUDAH memuatnya** sejak Tahap 1.5.
> Terbukti dari `_sketsa/ukur_tahap2.py` — 7 dari 7 fitur terdeteksi ADA.
> **PELAJARAN: jangan percaya tanda ⬜ di dokumen — UKUR dulu dari kode/halaman.**

**Tahap 2 selesai =** mahasiswa paham *"dataku memenuhi syarat atau tidak, dan kalau tidak, kenapa."*

> ✅ **Tahap 2.1 SUDAH DEPLOY** (20Sep26) — gerbang **33 grup EXIT 0** saat itu
> (sekarang **60 grup** — angka 33 benar untuk tanggal itu). SOT selaras.
> Kontainer `simulasi-olah-data` **healthy** · `DEPLOY_EXIT=0` ·
> verifikasi isi produksi `_sketsa/verifikasi_produksi_tahap2.py` **14 LULUS / 0 GAGAL**.
> Perubahan **sudah LIVE**, bukan lagi di berkas kerja.

---

# 🎯 TAHAP 3 — KLINIK (data sakit)

**Sasaran:** menu **KLINIK** berisi — bukan lagi halaman "segera".

| Langkah | Kerjaan | Bukti selesai |
|---|---|---|
| 3.1 | **Unggah data lapangan** (.sav/.csv/.xlsx/.por) | berkas sungguhan terbaca |
| 3.2 | **Data SAKIT sengaja** — tombol buat data yang MELANGGAR asumsi | data jelek terdeteksi, bukan lolos |
| 3.3 | **Kunci jawaban** — untuk Bos mengajar (tersembunyi dari mahasiswa) | dosen bisa pakai jadi bahan ajar |
| 3.4 | **Sambung ke PERIKSA SYARAT** — data sakit → grafik yang menunjukkan masalahnya | 1 alur utuh: unggah → periksa → perbaiki |

**Tahap 3 selesai =** mahasiswa **belajar dari data yang bermasalah** — bukan cuma lihat data bagus.

⚠️ **Ini tahap paling bernilai untuk mengajar.** Data simulasi yang selalu "aman" kurang berguna.

---

# 🎯 TAHAP 4 — PEMILIH ALAT (tujuan akhir Bos)

**Sasaran:** mahasiswa **tahu pilih SPSS atau SmartPLS** — tujuan yang Bos sebut sejak awal.

| Langkah | Kerjaan | Bukti selesai |
|---|---|---|
| 4.1 | **Pohon keputusan** — jawab beberapa pertanyaan → dapat rekomendasi alat | hasil masuk akal di 10 kasus uji |
| 4.2 | **Jelaskan ALASANNYA** — jangan cuma "pakai SPSS" | tiap rekomendasi ada alasan + contoh |
| 4.3 | **Kaitkan ke PERIKSA SYARAT** | setelah tahu alat → tahu syaratnya |

**Tahap 4 selesai =** mahasiswa **tidak bingung lagi** mau pakai alat apa.

---

# 🎯 TAHAP 5 — UJIAN (soal AI)

**Sasaran:** menu **UJIAN** berisi — latihan soal individual & kelompok.

| Langkah | Kerjaan | Bukti selesai |
|---|---|---|
| 5.1 | **Soal dari AI** (9router, ikut saklar ON/OFF) | soal muncul, mutunya wajar |
| 5.2 | **Bank soal statis** — pengaman kalau AI MATI | AI OFF ≠ aplikasi mati |
| 5.3 | **Penilaian otomatis** — kunci + rubrik, bukan menggantung | esai dinilai, ada umpan balik |
| 5.4 | **Mode kelompok** | 1 soal bisa dikerjakan beramai-ramai |

---

# 🎯 TAHAP 6 — MODUL KUALITATIF

**Sasaran:** pintu **KUALITATIF** di `/mulai` hidup (sekarang tampil tapi belum jalan).

| Langkah | Kerjaan | Catatan |
|---|---|---|
| 6.1 | **Mesin kualitatif** | ❌ **belum ada sama sekali** — ini kerjaan besar |
| 6.2 | Panduan per jenis (fenomenologi, studi kasus, grounded theory) | |
| 6.3 | Alat bantu: koding, tema, matriks | |

⚠️ **Paling berat** — mesinnya belum ada. Sebaiknya **paling akhir**.

---

# 🎯 TAHAP 7 — LOGIN + PENUTUP

| Langkah | Kerjaan |
|---|---|
| 7.1 | **Login** — supaya jatah/batas presisi per orang (sekarang hanya per-browser) |
| 7.2 | Riwayat lintas perangkat |
| 7.3 | Paket & kuota (kalau mau dijadikan produk) |

---

## 📋 RINGKASAN — 1 HALAMAN

| Tahap | Isi | Bobot | Kenapa di sini |
|---|---|---|---|
| **1** | Lebarkan pintu (unduhan SPSS/PLS + 10 model ke UI) | 🟡 sedang | menyambung yang SUDAH ADA, hasil cepat kelihatan |
| **2** | Periksa Syarat lengkap (SPSS + PLS) | 🟡 sedang | sudah setengah jalan |
| **3** | KLINIK (data sakit + kunci jawaban) | 🔴 besar | **paling bernilai untuk mengajar** |
| **4** | PEMILIH ALAT | 🟢 kecil | **tujuan akhir Bos** |
| **5** | UJIAN (soal AI) | 🔴 besar | butuh AI |
| **6** | Kualitatif | 🔴 **sangat besar** | mesin belum ada |
| **7** | Login + penutup | 🟡 sedang | penyempurna |

---

## 💬 CATATAN DISKUSI (BUKAN tugas — jangan dikerjakan)

📝 **Validitas & Reliabilitas + 12 uji** → `CATATAN_DISKUSI_VALIDITAS_12_UJI.md`
Arahan Bos 19Sep26: *"diskusi saja, kamu catat biasa saja, mungkin nanti setelah
project bisa kita bahas lagi."* → **JANGAN mulai koding dari berkas itu.**

Kaitan: kalau nanti dikerjakan, **masuknya di Tahap 2** (PERIKSA SYARAT) — dan
**sangat perlu Tahap 3** (data sakit) supaya ada yang salah untuk dilatih.

---

## ⚠️ 3 PRINSIP YANG TIDAK BOLEH DILANGGAR

1. **Jangan bongkar yang sudah ada** — *"sambungkan komponen yang SUDAH ADA, jangan bangun mesin baru"* (aturan Bos).
2. **Tiap tahap wajib ada gerbang uji + deploy `jalankan.sh`** — bukan "kira-kira jalan".
3. **Mesin sudah sakti** — pekerjaan utama adalah **membuka pintu**, bukan membuat mesin baru.
