# KEPUTUSAN BOS — DIAGNOSIS DATA + RUANG UJI (19Sep26)

> Dibuat 19Sep26. Semua keputusan sudah **ACC Bos**. Wulan mulai koding.
> Kalau sesi reset: baca berkas ini + FLAG_LANJUT_DISINI.md.

---

## BAGIAN A — HALAMAN `/syarat` → ALAT "DIAGNOSIS DATA SPSS & PLS"

### Perintah Bos (VERBATIM)
> *"Halaman Syarat, jadikan tool / alat saja. Namanya Diagnosis Data SPSS & PLS
> Isinya user upload data dari spss atau pls, untuk di diaknosa dan cara tulisnya.
> Benar katakan benar salah katakan salah dan beri panduan untuk cara membetulkan data."*

### Keputusan teknis (VERBATIM: "1. B (xlsx, csv, sav) 2. A 3. A")
| # | Keputusan |
|---|---|
| 1 | **B** — format: **`.xlsx` + `.csv` + `.sav`** |
| 2 | **A** — user **TUNJUK KOLOM MANUAL** (dropdown), mesin TIDAK menebak |
| 3 | **A** — **7 kartu bacaan** di `/syarat` **PINDAH ke BELAJAR** |

### Yang diperiksa
- **Mode SPSS (6):** Normalitas (K-S + skewness) · Heteroskedastisitas (Glejser) ·
  Multikolinearitas (VIF) · Linearitas · Outlier (IQR) · Durbin-Watson
- **Mode SmartPLS (5):** Outer Loading · AVE · Composite Reliability · VIF inner ·
  Fornell-Larcker
- **BELUM (tulis jujur di halaman):** HTMT · Q²/PLSpredict · SRMR

---

## BAGIAN B — TAB DI HALAMAN BELAJAR

### Keputusan Bos (VERBATIM)
> *"Di kategori belajar bikinsaja tab diatas, bikin2 tab halaman, satu yang sekarang,
> satu lagi rencana kita ini."*

| # | Keputusan |
|---|---|
| 1 | Nama tab ke-2: **"Ruang Uji"** |
| 2 | Di dalam Ruang Uji: **2 KARTU saja** (opsi B) — **Rusak Data** + **Kuis Pilih Alat** |
| 3 | **Kamus Grafik** (7 kartu pindahan) → **digabung ke TAB 1** (Materi & Kamus) |

### Struktur akhir
```
/belajar
├── TAB 1 — MATERI & KAMUS   (yang SEKARANG + 7 kartu pindahan dari /syarat)
└── TAB 2 — RUANG UJI
    ├── 🧪 RUSAK DATA        (tuas geser → grafik rusak → user tebak)
    └── 🎯 KUIS PILIH ALAT   (8 soal, skor, animasi emotikon)
```

### Nama "Rusak Data"
Bos (VERBATIM): *"Kata coba sakitkan tidak tepat ganti Rusak Data"*

---

## BAGIAN C — KUIS PILIH ALAT

### Keputusan Bos
| # | Pertanyaan | Jawaban |
|---|---|---|
| 1 | Sumber soal | **A** — bank soal offline + AI ganti angka kalau saklar nyala |
| 2 | Jumlah soal sekali main | **A** — **8 soal** (diacak dari bank) |
| 3 | AI boleh apa | **A** — **ganti ANGKA saja** (konsep tidak berubah) |
| 4 | Jumlah bank soal | **50 soal** — dikerjakan **BERTAHAP** (10 dulu) |
| 5 | Skor | **A** — **disimpan di browser** (localStorage) + tombol "Mulai Ulang Skor" |
| 6 | Animasi | **WAJIB** — emotikon sesuai skor (jelek/bagus), seperti kuis |

### Mengapa AI hanya GANTI ANGKA (alasan Wulan, disetujui)
Soal statistik yang SALAH = mahasiswa belajar yang salah. Konsep dari bank soal
yang sudah diperiksa; AI hanya mengganti angka/nama penelitian dari pola tetap.

### Mengapa bank soal ditulis tangan
Kalau AI dimatikan / 9router mati → kuis **tidak boleh kosong**.
Bank soal = jaring pengaman yang SELALU ada (Rp 0).

---

## BAGIAN D — SKOR & "SEASON" (jawaban Wulan, TERUKUR)

### Pertanyaan Bos
> *"soal nilai selaku di reset atau bagaimana? Bagaimana dengan season dan cookies apakah menyimpan?"*

### Keadaan TERUKUR aplikasi (grep kode, bukan dugaan)
| Cek | Hasil |
|---|---|
| Cookie / session server | ❌ **TIDAK ADA** (nol) |
| localStorage | ✅ ADA — dipakai `/mulai` (riwayat judul, maks 50) |
| Jatah harian | ✅ ADA — `app/jatah.py`, berkas server, kunci **tanggal** |

### Jawaban
- **Skor** → disimpan di **localStorage** (browser user). Bertahan; **hilang kalau ganti HP**.
- **Cookie** → **tidak dipakai sama sekali**. Server tidak menyimpan skor.
- **"Season"** → **TIDAK BISA** tanpa login. Papan peringkat butuh **identitas**
  (siapa yang menang). Login = **Tahap 7**.

⚠️ **Yang Bos sebut "season"** kemungkinan **`session_reset` Hermes** (04.00 UTC) —
itu **obrolan Wulan ↔ Bos**, BUKAN aplikasi statistik. Aplikasi punya penyimpanannya sendiri.

---

## BAGIAN E — YANG SUDAH TERUKUR (bahan, tidak perlu dibangun ulang)

| Kebutuhan | Status |
|---|---|
| Baca `.csv` | ✅ **TERBUKTI** (pandas 3.0.5) |
| Baca `.xlsx` | ✅ **TERBUKTI** (openpyxl 3.1.5) |
| Baca `.sav` | ✅ **TERBUKTI** (pyreadstat 1.3.6) — + label kolom & label nilai |
| `uji_spss()` | ✅ ADA di `app/hitung/mesin.py` |
| `uji_pls()` | ✅ ADA — path coef, bootstrap, AVE, CR, loading |
| `alpha_cronbach()` | ✅ ADA |
| `tambah_rasa_lapangan()` | ✅ ADA (derau, data bolong, outlier) |
| Slider yang jalan | ✅ ADA (`/belajar`, `/buat-data`) |
| Saklar AI ON/OFF | ✅ ADA (`data/ai_aktif.txt`, `/api/ai`) |
| **AI ke 9router** | ❌ **BELUM tersambung** (grep: nol panggilan) |
| **Bank soal** | ❌ **BELUM ADA** |
| **CSS tab** | ❌ **BELUM ADA** — pakai variasi `.pilih` yang sudah ada |

---

## BAGIAN G — OPSI 1 DIPILIH: MENU KLINIK JADI "DIAGNOSIS DATA"

### Temuan Wulan sebelum koding (TERUKUR)
Menu `klinik` di `app/main.py` SUDAH terdaftar dengan ringkas:
> *"Unggah data lapangan (.sav/.csv/.xlsx) — periksa & jelaskan cara memperbaikinya."*

⇒ ISINYA HAMPIR SAMA dengan permintaan Bos → kalau Wulan bikin `/diagnosis` baru,
DUA MENU akan saling menimpa. Bentrok ini Wulan sampaikan ke Bos SEBELUM koding.

### Keputusan Bos (VERBATIM: "1. Opsi 1  2. A")
| # | Keputusan |
|---|---|
| 1 | **OPSI 1** — menu **KLINIK diganti nama jadi "DIAGNOSIS DATA"** + diisi alat unggah. **Sekaligus menyelesaikan Tahap 3** (data sakit + kunci jawaban dosen). |
| 2 | **A** — halaman `/syarat` **DIBIARKAN** + ganti nama jadi **"Kamus Grafik"** |

### Struktur menu jadi
```
MULAI · BELAJAR(+Ruang Uji) · BUAT DATA · 🩺 DIAGNOSIS DATA (dulu KLINIK)
· PERIKSA SYARAT/Kamus Grafik · UJIAN · PEMILIH ALAT · PENGATURAN
```

---

## BAGIAN H — KUIS: 4 KATEGORI (BUKAN cuma grafik)

### Arahan Bos (VERBATIM)
> *"Kuis tidak hanya masalah grafik statistik saja tapi ada teori dan metodologi penelitian"*

⇒ Wulan SETUJU — terukur: kamus `/belajar` cuma punya 6 istilah, **SEMUANYA statistik**
(`hetero, beta, pvalue, vif, alpha, ujit`). **Tidak ada teori/metodologi** — itu lubang nyata.

### Keputusan Bos (VERBATIM: "1. A  2. A  3. A")
| # | Keputusan |
|---|---|
| 1 | **A** — **4 KATEGORI**: 🧭 Metodologi (15) · 📚 Teori (10) · 📊 Statistik (15) · 🛠️ Pilih Alat (10) = **50 soal** |
| 2 | **A** — **PILIHAN GANDA SEMUA** (Rp 0, dinilai otomatis, adil) |
| 3 | **A** — **BELAJAR = LATIHAN** (santai, boleh ulang, tak dinilai) · **UJIAN = DINILAI** (Tahap 5, individual/kelompok) |

### Beda BELAJAR ↔ UJIAN (penting, jangan tercampur lagi)
| | BELAJAR → Ruang Uji → Kuis | MENU UJIAN (Tahap 5) |
|---|---|---|
| Sifat | **Latihan** | **Ujian sungguhan** |
| Dinilai? | ❌ tidak | ✅ ya |
| Boleh ulang? | ✅ bebas | ❌ sekali |
| Individual/kelompok | tidak ada | ✅ ada |
| Soal | bank soal tetap | AI + bank soal |

### Bank soal: dikerjakan BERTAHAP
Bos minta **50 soal**, tapi Wulan usul **bertahap** (10 per kategori dulu = 40 soal)
supaya kuis bisa jalan lebih cepat. Target akhir tetap 50.

### ⚠️ Risiko yang Wulan sebut (Bos perlu tahu)
Soal **TEORI** memuat **nama & tahun teori** — kalau Wulan salah tulis, mahasiswa
belajar yang salah. **Wulan minta Bos periksa** bagian teori setelah ditulis.

---

## BAGIAN F — URUTAN KERJA (dipecah, lapor tiap tahap)

1. **TAHAP 1** — Halaman `/diagnosis` (alat unggah + tunjuk kolom + hasil)
2. **TAHAP 2** — Tab BELAJAR + pindahkan 7 kartu
3. **TAHAP 3** — Ruang Uji: Rusak Data + Kuis Pilih Alat
4. **TAHAP 3b** — Bank soal 10 dulu (target 50)
5. **TAHAP 4** — Gerbang uji + deploy + tangkapan layar

---

## CATATAN JUJUR (jangan disembunyikan)

1. **AI belum tersambung** — kalau Bos mau kuis dari AI, itu kerja tambahan.
2. **`.sav` dari SmartPLS tidak ada** — SmartPLS pakai `.csv`/`.xlsx`. Aman.
3. **Batas 10 MB belum diuji** — diukur nanti.
4. **Grafik hidup butuh dihitung di browser** — sekarang gambar tangan (`cy=` manual).
5. **Sketsa sudah dibuat & dilihat Bos**: `_sketsa/diagnosis_sketsa.html`,
   `_sketsa/belajar_tab_sketsa.html` (tangkapan HP 390px di `/tmp/`).
