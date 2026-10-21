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
