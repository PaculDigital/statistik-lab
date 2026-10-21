# CATATAN — Jembatan EduAi Fase 1 (21 Okt 2026)

Branch: `agen/wulan/jembatan-bab4` · Pengerja: Wulan, atas perintah Bos
("Gas — mulai Fase 1"). Rancangan induk: `DOKUMENTASI_BAB4_RANCANGAN_FINAL_21OKT2026.md`
di repo eduai-publishing (§11 Opsi B).

## Yang dibangun

1. **`app/jembatan.py`** (baru):
   - `GET /api/jembatan/status` — tanpa kunci; `{layanan, ok, kunci_terpasang}`.
   - `POST /api/jembatan/hitung` — WAJIB header `X-Kunci-Layanan`.
     Kunci dibandingkan (compare_digest) dengan env `JEMBATAN_KUNCI_LAYANAN`.
     Env belum dipasang → **503** (pintu tertutup, bukan terbuka).
     Kunci salah/tidak ada → **401**.
   - Payload tahap utama: `{mode: spss|pls, tahap: "utama", baris: [{kolom: nilai}],
     kolom_x, kolom_y, kolom_m, kolom_z, peran, konstruk, kolom_y_konstruk,
     missing, bentuk_mediasi}` — data dikirim sebagai baris JSON, TIDAK disimpan.
   - Payload pra-survei: `{tahap: "pra-survei", baris: [...], konstruk?|peran?}`.
     Tanpa konstruk/peran, butir dikelompokkan dari pola nama kolom
     (`Nama_Variabel_Nomor` / `KP1`).
   - `periksa_pra_survei()`: per variabel → Cronbach Alpha memakai `_alpha`
     dari `app/diagnosis.py` (rumus TIDAK diduplikasi); per butir →
     korelasi butir–total TERKOREKSI vs r kritis (sebaran t, df=n−2, 5%);
     `lolos` per butir, `lolos_alpha` (≥0,60), `semua_lolos`, catatan bila n<10.
2. **`app/main.py`** (sentuhan kecil): blok penghias hasil rute lama
   diekstrak menjadi `_hias_hasil(r, mode)` dan dipakai BERSAMA oleh
   `/api/diagnosis/periksa` dan pintu jembatan — satu sumber, hasil kedua
   pintu untuk data yang sama tidak mungkin berbeda. Router jembatan
   didaftarkan di ekor berkas. Alur lama tidak berubah perilaku.

## Bukti uji (`uji_jembatan.py`, semua lulus)

- SPSS lama vs jembatan: r2, r2_adj, vif_maks, dw, koefisien b & p semua
  jalur, dan daftar masalah — **persis sama**.
- PLS lama vs jembatan: CR/alpha per konstruk — **sama**.
- Tanpa kunci 401 · kunci salah 401 · kunci server belum dipasang 503.
- Pra-survei: kelompok otomatis benar; butir acak (sampah) terdeteksi
  TIDAK lolos; alpha keluar untuk semua variabel.
- Regresi: `uji_kaitan.py` lulus. `uji_diagnosis.py` gagal di pembacaan
  .sav — **sudah gagal juga di master bersih** (lingkungan uji tak punya
  pembaca .sav), bukan akibat perubahan ini.

## Belum / catatan pemilik

- Kunci `JEMBATAN_KUNCI_LAYANAN` BELUM dipasang di server produksi —
  itu tindakan pemilik saat deploy (nilainya tidak ditulis di repo).
- Belum deploy, belum push (menunggu perintah Bos). Deploy = keputusan Bos.
- Fase berikutnya (repo EduAi): fondasi hasil berversi + modul
  `app/bab4.py` + `app/jembatan_statistik.py`.

## Perbaikan dari review agen Bos (21 Okt 2026, sore)

Review luar menjalankan 28 uji tambahan → 4 bug, semuanya DIPERBAIKI
(commit b8e7f46) + branch disusulkan ke master (merge 8c1e9cc):

1. **Branch tertinggal master** (footer brand, SEO favicon/sitemap/robots,
   gerbang Chrome, STATUS.md) → origin/master di-merge masuk, TANPA konflik;
   sesudah merge /favicon.ico, /sitemap.xml, /robots.txt semua 200 dan
   uji jembatan tetap lulus semua.
2. **Kunci non-ASCII → 500** → kunci kini dibandingkan sebagai bytes UTF-8;
   kunci aneh apa pun ditolak 401.
3. **Kolom merangkap dua peran diterima** → pagar `_cek_tumpang_tindih`:
   perpotongan X/M/Z/Y (SPSS) dan butir di dua konstruk (PLS) ditolak 400.
4. **Nama kolom tanpa nomor salah kelompok** → pengelompokan awalan KETAT:
   kolom tak berpola ditolak 400 dengan pesan yang menyebut polanya.
+ Uji rotasi kunci env (kunci lama mati, kunci baru jalan) membuktikan
  kunci dibaca dari env, bukan tertanam di kode.
Catatan tersisa (bukan bug): timeout panggilan adalah urusan klien
EduAi di Fase 2 — terukur 5.000 baris ≈ 0,23 detik, belum mendesak.

## Review kedua agen Bos (21 Okt, 15:22) — BUG 3 diperdalam

Vonis agen: BUG 3 BELUM tuntas. Benar — pagar versi pertama hanya
membaca bentuk eksplisit (kolom_x/kolom_y), buta untuk bentuk `peran`
yang justru dipakai. Dibuktikan agen dengan uji mutasi, dan Wulan
membuktikan ulang sesudah perbaikan: pagar dimatikan → kiriman
variabel-terbelah kembali **200 dan dihitung** (r2 keluar); pagar hidup
→ ditolak 400.

Perbaikan (pagar 3 lapis di `_cek_tumpang_tindih`):
- A. Bentuk tunggal: `peran` dan kolom eksplisit tidak boleh dicampur.
- B. Belah variabel: butir satu variabel induk (pola Nama_Nomor) tidak
  boleh terbelah ke keluarga peran X/M/Z/Y berbeda, maupun antar
  konstruk PLS.
- C. Tumpang tindih persis seperti sebelumnya, KINI juga dipanggil
  sekali lagi pada payload EFEKTIF hasil `gabung_peran` — persis yang
  dihitung mesin.
Uji bagian 6 di `uji_jembatan.py` bersifat bergigi (gagal bila pagar
dicabut), dan klien uji memakai raise_server_exceptions=False supaya
kegagalan terbaca sebagai asersi, bukan crash.

---

## VONIS REVIEW KETIGA — LULUS, SIAP MERGE (21 Okt 2026)

Reviewer: Wulan (pemegang kendali `main`). Branch yang diperiksa:
`agen/wulan/jembatan-bab4` @ **848c0d0**. Metode: baca kode baris-per-baris
+ jalankan uji bawaan + **38 uji tepi independen** + **uji mutasi**
(pagar dimatikan untuk membuktikan uji bisa GAGAL).

### Status 4 bug

| # | Bug | Status | Bukti |
|---|---|---|---|
| 1 | Branch tertinggal master (SEO hilang) | ✅ TUNTAS | `8c1e9cc` merge; `main.py` memuat ulang favicon/sitemap/robots (13 kemunculan) |
| 2 | Kunci non-ASCII → 500 | ✅ TUNTAS | header raw bytes `kunci-\xea` → **401** (bukan 500) |
| 3 | Peran tumpang tindih diterima | ✅ TUNTAS + BERGIGI | `peran` terbelah X/Y → **400**; pagar dimatikan → **200** (uji menangkap) |
| 4 | Kolom tanpa nomor salah kelompok | ✅ TUNTAS | `Kualitas, Harga, Minat` → **400** + pesan menyebut pola |

### Uji mutasi (bukti uji tidak hijau palsu)

| Keadaan pagar | `peran` terbelah |
|---|---|
| Kode asli | 400 ✅ |
| Pagar dimatikan total | **200** ← tertangkap |
| Pagar buta untuk bentuk `peran` (bug versi pertama) | **200** ← tertangkap |
| Dipulihkan | 400 ✅ |

### Hasil angka

- `uji_jembatan.py`: **26/26 LULUS** (termasuk 5 asersi regresi + 4 asersi bentuk `peran`).
- Uji tepi reviewer: **38 kasus** — semua berperilaku benar. Dua yang
  tampak "gagal" BUKAN bug aplikasi: (a) header non-ASCII ditolak
  pustaka klien (httpx), server sudah benar; (b) kolom tanpa nomor
  memang SENGAJA ditolak 400 sekarang.
- Opsi B (tanpa simpan): sesi mesin **0 → 0** sesudah 5000 baris.
- Kinerja: 5000 baris = **0,24 detik**.
- Determinstik: dua panggilan identik → hasil identik.

### Syarat sebelum/sesudah deploy (BUKAN bug kode)

1. Env `JEMBATAN_KUNCI_LAYANAN` **belum dipasang** di produksi → pintu
   masih 503 (aman tertutup). Nilai kunci = keputusan pemilik, tidak
   ditulis di repo.
2. Pintu **kualitatif** (§11.2 butir 2: koding + triangulasi/SWOT)
   belum ada — memang fase berikutnya, bukan syarat Fase 1.
3. `DOKUMENTASI_BAB4_RANCANGAN_FINAL` §10.2 (waktu bayar campuran)
   masih **[USULAN]**, bukan keputusan.

**VONIS: LULUS — layak masuk `master`.**
