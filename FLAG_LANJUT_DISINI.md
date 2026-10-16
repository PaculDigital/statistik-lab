## 🛑 22 Sep 2026 — **TITIK HENTI** (kata Bos: *"saya cukup dulu sampai disini, kita lanjut kapan kapan"*)

> **BOS MENYURUH BERHENTI DI SINI.** Semua pekerjaan sesi 22Sep26 **SELESAI
> & LIVE**. Tidak ada pekerjaan yang menggantung separuh jalan.

### 🔖 CARA BALIK (kalau Bos bilang *"lanjut statistik"* / *"buka flag"*)

```bash
cd /opt/data/services/statistik-lab
.venv/bin/python sot.py --periksa        # 1. dokumen selaras kode?
.venv/bin/python sot.py                  # 2. keadaan terkini DIHITUNG dari kode
read FLAG_LANJUT_DISINI.md               # 3. blok ini (paling atas)
bash gerbang_uji.sh                      # 4. 60 grup, EXIT 0 = aman
```
**Prasarana dulu (jangan lupa):**
```bash
curl -s -o /dev/null -w "9333 -> %{http_code}\n" --max-time 4 http://127.0.0.1:9333/json/version
```

### ✅ KEADAAN TERKUNCI (jangan dikerjakan ulang)

| Hal | Nilai |
|---|---|
| Produksi | `statistik.bikinaja.id` — image `simulasi-olah-data:20260922_051533-statlab` |
| Kontainer | `simulasi-olah-data` · **healthy** · port 8120 |
| Gerbang | **60 GRUP · SEMUA LULUS · EXIT 0** |
| SOT | ✅ **SELARAS** |
| Uji terkait | `uji_manova.py` 53 ✅ · `uji_manova_halaman.py` 22 ✅ · verifikasi produksi MANOVA 9 ✅ |
| Image lama | sudah **dihapus** (sisa 2: tag baru + `:terkini`) |

### 🗺️ PETA KERJA YANG SELESAI (22Sep26)

1. **Ruang MANOVA dibuka & LIVE** — kartu ke-5 "Banding kelompok" di
   `/kuantitatif` (lebar penuh) + panel di `/buat-data?model=banding-kelompok`.
2. **K-22 ditutup** — kolom "Nilai" berisi **nilai statistik** (dulu berisi F →
   `Pillai = 57,224` mustahil). F dipisah ke kolomnya sendiri.
3. **K-23 ditutup** — kolom `df` terisi untuk **keempat** ukuran
   (Wilks `2,117` · Pillai/Hotelling/Roy `2,236`).
4. **K-24 ditutup** — `gerbang_bahasa.py` tak lagi **gagal palsu** gara-gara
   komentar Jinja `{# … #}`.
5. **Tata letak** — kartu "Campuran" → **lebar penuh** (putusan Bos: "Geser").
6. **K-25 dicatat** — verifikasi jangan menuntut **bentuk yang ditebak**.

### ⏭️ BELUM DIKERJAKAN (menunggu putusan Bos — JANGAN mulai sendiri)

| # | Hal | Perlu apa |
|---|---|---|
| 1 | **Mardia p=0,0000** ("tidak normal") | Wajar untuk data berkelompok, tapi mahasiswa **perlu penjelasan** supaya tidak dikira data rusak |
| 2 | **12 uji mati "PENINGGALAN"** | Putusan Bos: **hapus** atau pelihara? |
| 3 | Potret mata terbaru | Sudah diperiksa mata 1× (df terisi); potret final menyusul |
| 4 | `RUANG_MANOVA.md` §8b–8d | Masih berlaku sebagai catatan; bahasan MANOVA **DITUTUP** — jangan koding tanpa Bos buka |

### 📚 DOKUMEN WAJIB DIBACA SEBELUM LANJUT

1. `CATATAN_KESALAHAN_21SEP2026.md` — **K-01…K-25** (kesalahan Wulan + cara betulnya)
2. `CATATAN_DISKUSI_VALIDITAS_12_UJI.md` + `CATATAN_DISKUSI_GERBANG_MODEL_Y_GANDA.md`
3. `RUANG_MANOVA.md` · `KEPUTUSAN_PARSIAL_SIMULTAN_21SEP2026.md`
4. Skill: `skill_view(name='statistik-lab')` — bab **RUANG MANOVA**

---

## 📐 22 Sep 2026 — RUANG MANOVA: HASIL TAMPIL & **SUDAH DEPLOY** ✅

**Status:** ✅ **DEPLOY 22Sep26 05:15 UTC** · image
`simulasi-olah-data:20260922_051533-statlab` · kontainer **healthy** ·
`statistik.bikinaja.id/health` **200** · gerbang **60 grup EXIT 0** ·
isi produksi **9 LULUS** (diperiksa dari DALAM kontainer) · SOT **SELARAS** ·
image lama **dihapus** (4 dibuang, sisa 2)

### 🔴 3 BUG YANG DITUTUP HARI INI — SEMUA KETEMU **MATA**, BUKAN UJI TEKS

| # | Bug | Akar | Keadaan |
|---|---|---|---|
| **K-22** | Kolom "Nilai" berisi **F** → `Pillai = 57,224` (mustahil > 1) | `kartuUjiManova()` pakai `q.F` | ✅ kolom "Nilai" = `nilaiStat`, F terpisah |
| **K-23** | Kolom `df` kosong `"—, —"` untuk Pillai/Hotelling/Roy | `_f_dari_statistik()` pakai df tapi tak **menyimpan** | ✅ `df1`/`df2` disimpan + penjaga uji [15] |
| **K-24** | `gerbang_bahasa.py` **gagal palsu** (kata di komentar Jinja `{# #}` dihitung) | `ambil_teks_tampil()` tak buang `{# #}` | ✅ dibuang lebih dulu + `_sketsa/bukti_bahasa_bergigi.py` |

⚠️ **PELAJARAN INDUK HARI INI:** 4 gerbang + 53 asersi **HIJAU**, tapi **MATA**
menemukan 2 bug nyata di tabel yang dilihat mahasiswa. **Uji teks TIDAK melihat
salah kolom.** Untuk yang DILIHAT user → **potret + periksa mata WAJIB.**

⚠️ **PELAJARAN KEDUA:** kata "pagar" **benar-benar terkirim** ke mahasiswa
(id elemen `pagar-${i}` + komentar JS) → gerbang **BENAR**; yang benar-benar
salah hanya 1 (komentar Jinja). **Buktikan dulu sebelum menuduh gerbang.**
Perbaikan akar: id → `perkiraan-${i}` (bukan menambal gerbang).

⚠️ **PELAJARAN KETIGA (K-25):** dua verifikasi produksi pertama **melaporkan
"GAGAL" padahal KODE BENAR** — Wulan menuntut bentuk yang **ditebak**
(`r.statistik[`, dan `split('\\n')` yang jadi literal). **Cetak dulu bentuk
sebenarnya, baru tulis syaratnya.**
Bukti akhir: `_sketsa/verifikasi_produksi_manova.py` **9 LULUS / 0 GAGAL**.

### 🎨 PUTUSAN TATA LETAK BOS 22Sep26
1. **"Ok"** — betulkan kolom Nilai ✅
2. **"Geser"** — kartu **Campuran** → `lebar-penuh` ✅ (terverifikasi mata:
   tidak ada kolom kosong lagi; kartu terkunci "Susun sendiri" tetap 1 kolom)

### 🧭 WAJIB SEBELUM MENULIS JS TAMPILAN
```bash
.venv/bin/python _sketsa/bentuk_manova.py   # CETAK bentuk kunci APA ADANYA
```
Wulan **2× salah** karena menulis JS dari **DUGAAN** bentuk kunci
(`n_kelompok` padahal `isi_kelompok`; `mardia.stat` padahal `mardia.nilai`;
`amanTeks` = fungsi **Jinja**, bukan JS). **Cetak dulu, baru tulis.**

### ➡️ BERIKUTNYA (belum dikerjakan)
1. **Mardia "tidak normal"** (p=0,0000) — wajar untuk data berkelompok,
   tapi **perlu penjelasan ke mahasiswa** supaya tidak dikira data rusak
2. **12 uji mati "PENINGGALAN"** — menunggu putusan Bos (hapus?)
3. **Verifikasi mata potret terakhir** (setelah perbaikan df) — sudah lewat
   mata sekali (df terisi), potret terbaru menunggu

---

## 🏛️ 21 Sep 2026 (KEDUA) — IDENTIFIKASI DATA ✅ + PRASARANA ≠ MESIN ✅

**Status:** ✅ **SUDAH DEPLOY 21Sep26 20:59 UTC** · image `simulasi-olah-data:20260921_205932-statlab` · kontainer **healthy** · domain **statistik.bikinaja.id 200** · gerbang **60 grup EXIT 0** · SOT **SELARAS**

### 🔴 WAJIB DIBACA SEBELUM LANJUT — 3 DOKUMEN

1. `CACAT_MEDIASI_X_BANYAK_21SEP2026.md` — **CACAT TERBUKA (terukur 21Sep26)**
2. `CATATAN_KESALAHAN_21SEP2026.md` — 15 kesalahan Wulan (K-01…K-15)
3. `TEMUAN_MEDIASI_MODERASI_21SEP2026.md` — mediasi/moderasi/berjenjang/rantai

### 🔴 CACAT TERBUKA — mediasi & moderasi hanya pakai **X PERTAMA**

**Ditemukan dari pertanyaan Bos** (*"apakah sudah support x1, x2, x3 dst.
M1, m2 dst. Terhadap y1, y2, y3"*) — **diukur lewat pintu produksi**.

- Terukur: `kaitan.mediasi[0].x = "X1"` — **bukan** `['X1','X2','X3']`
- Akar **4 tempat** di `app/hitung/kaitan.py`: baris **553 · 565 · 569 · 573**
  semuanya `kolom_x[0]`; tanda tangan `mediasi(df, x: str, …)` = satu X
- Dampak: mahasiswa tandai X1,X2,X3 → mesin hitung **hanya X1**;
  **X2 & X3 dibuang diam-diam**, hasil **kelihatan sah** (paling menyesatkan)

**STATUS: DICATAT — BELUM DIPERBAIKI.** ACC Bos 21Sep26:
*"Catat dan kita deploy dulu recreate"* → sengaja dibawa ke deploy,
perbaikan menyusul setelah Bos pilih opsi **A / B / C**.

**Yang SUDAH didukung (terukur):** banyak X di regresi biasa
(`prediktor=['X1','X2','X3','M1','M2']`) · banyak M paralel · M berjenjang ·
rantai >2 perantara · banyak Y diuji satu-satu (R² 0,3512 / 0,334 / 0,252) ·
kolom seperan digabung · Z di mode PLS.


### ① IDENTIFIKASI DATA di `/klinik` — mahasiswa menandai PERAN kolom

**Arah Bos (21Sep26):** *"mahasiswa identifikasi kolom ini X1 kolom ini X2 dst.
Kolom ini M1, kolom ini M2 dst.. begitu juga Z dan Y, Y1, Y2 dst."*
**Latihan, bukan ujian** — tanpa AI, tanpa kunci jawaban, 3 lapis aturan tetap.

Mahasiswa memberi **dropdown peran** tiap kolom (`X1`… `M1`… `Z1`… `Y1`… `Bukan data`).
Mesin memeriksa **5 hal**: kolom belum ditandai · nomor melompat · tanpa X · tanpa Y ·
konstruk cuma 1 kolom. Kalau >1 M / >1 Z → tanya **paralel/berjenjang SEKALI**.

**⭐ YANG BARU (inti): SKOR KONSTRUK** — `X1` = 3 kolom → digabung jadi **SATU skor**
sebelum dihitung. Sebelumnya mesin melihat `X1` sebagai **3 variabel terpisah** (salah).
- `app/diagnosis.py::skor_konstruk(df, peran)` — gabung kolom seperan
- `app/main.py::_gabung_peran(df, payload)` — disambung di rute `/api/diagnosis/periksa`
- **Aturan jawaban kosong = OPSI B (ACC Bos 21Sep26):**
  `skor = RATA-RATA item TERJAWAB × JUMLAH ITEM SELURUHNYA`
  (X1 3 item, dijawab 2 skor 4 & 5 → (9/2)×3 = **13,5**).
  Alasan: Opsi A membuang responden yang cuma kurang 1 item · Opsi C (SPSS `SUM`)
  memberi skor **terlalu kecil yang kelihatan sah** (jawab 1 dari 2 → 2,0). Semua kosong → **NaN, bukan 0**.

**BUKTI (semua terukur):**
- `uji_skor_konstruk.py` **35/0** — *terbukti bisa gagal*: diubah ke cara SPSS → **7 uji menangkap**
- `uji_peran_skor_e2e.py` **15/0** — unggah nyata: prediktor mesin = `['X1','X2']`, **bukan** 5 kolom mentah · R² mesin **0,2543** = hitungan tangan
- `uji_peran_kolom.py` **35/0** · `uji_peran_web.py` **30/0** · `uji_peran_alur.py` **20/0**
- gerbang **60 GRUP EXIT 0**

### ② PRASARANA ≠ MESIN — kode LEWAT 77 (ACC Bos, Opsi A)

**Akar:** Chrome CDP :9333 mati → gerbang melaporkan *"7 GRUP GAGAL"* → Wulan
**mengejar bug aplikasi yang tidak ada**. Yang salah: gerbang **menyamakan**
"prasarana mati" dengan "mesin rusak".

**Perbaikan akar:**
- `prasarana_uji.py` **BARU** — `pastikan_chrome(port)` → `None` (hidup) / `KODE_LEWAT` (mati) + pesan + perintah siap-tempel
- `gerbang_uji.py` — `KODE_LEWAT = 77`: rc 77 = ⏭️ **LEWAT prasarana**, BUKAN GAGAL
- 6 berkas uji browser disambungkan (`uji_sub_regresi`, `uji_normalitas`, `uji_web_grafik`, `uji_tab_baca_grafik`, `uji_web_anova`, `uji_web_pintu`)

**BUKTI 2 ARAH:** Chrome **MATI** → gerbang **EXIT 0** *"60 grup · 6 lewat karena prasarana"* ✅ ·
GAGAL **asli** disuntik → gerbang **EXIT 1** ✅ · Chrome **HIDUP** → **60 grup EXIT 0** ✅

**🚨 CHROME TIDAK BISA DILEPAS DARI GATEWAY — JANGAN COBA-COBA LAGI.**
Terukur **4 cara, SEMUA GAGAL** (`Popen` biasa · `start_new_session=True` ·
double-fork · double-fork+setsid → Chrome kabur dengan galat **dbus**).
Chrome hanya mau hidup kalau dijalankan lewat `terminal(background=true)` Hermes
(PPID = gateway). **PPID itu syarat hidup, bukan kelemahan.**
⇒ **JANGAN** bikin watchdog cron (cron ≠ anak Hermes → dbus gagal) ·
**JANGAN** `pkill` (mematikan shell sendiri) · kalau mati → nyalakan lagi:
`/opt/data/home/.cloakbrowser/chromium-151.0.7922.108.6-pro/chrome --headless=new --no-sandbox --disable-gpu --remote-debugging-port=9333 --remote-allow-origins=*`

**⏸️ BELUM:** deploy (tunggu ACC) · mesin hitung per-konstruk untuk **mediasi/moderasi berjenjang** (baru regresi berganda yang diuji) · `.csv` belum bisa multi-sheet (hanya `.xlsx`).

**📕 WAJIB DIBACA SEBELUM KERJA — 2 berkas:**
1. **`CATATAN_KESALAHAN_21SEP2026.md`** — 9 kesalahan Wulan + **cara memperbaikinya**
   (K-01 salahkan aplikasi padahal prasarana mati · K-02 tebak nama kunci jawaban server ·
   K-03 ambang karangan di uji · K-04 bersihkan data di dalam uji · K-05 salah hitung
   sendiri · K-06 ubah dokumen tanpa jalankan SOT · K-07 putuskan soal statistik sendiri ·
   K-08 kerjakan laporan kedaluwarsa · **K-09 ukur mesin di tengah jalan lalu tuduh cacat**).
2. **`AUDIT_UJI_LUAR_GERBANG_21SEP2026.md`** — 23 uji di luar gerbang: **10 JALAN · 13 RUSAK**.
   Akarnya **BUKAN mesin**, tapi **PINTU UKUR SALAH** (0 dari 13 uji rusak mengukur lewat
   pintu produksi `buat_data()`). Kasus telak: `bangun_dari_spek` langsung → galat **0,134**;
   `buat_data()` → galat **0,0003**. 12 uji sisa sudah **DITANDAI PENINGGALAN** di kepala berkas.

## 🏛️ 20 Sep 2026 — SOT DISERAGAMKAN: **URUTAN TAHAP KINI DIJAGA MESIN**

**Masalah yang ditutup:** `MASTER_PLAN.md §9` dan `TAHAP_PENYELESAIAN.md` memuat
**urutan tahap yang SALING BERLAWANAN** (Ujian / Pemilih alat / Login / Kualitatif
tertukar posisi) — dan `sot.py` **tetap bilang "SELARAS"** karena ia hanya
memeriksa jumlah grup uji.

**KEPUTUSAN BOS (20Sep26):**
1. `MASTER_PLAN.md` tetap **7 TAHAP BESAR** (peta kasar) · `TAHAP_PENYELESAIAN.md` = **rincian**
   (bab tahap + sub-langkah 1.1–1.6, 2.1–2.5). **Dua takaran berbeda dan itu SAH** — jangan dipaksa sama.
2. Urutan resmi: **Klinik → Pemilih alat → Ujian → Kualitatif → Login**
   (Pemilih alat = tujuan utama Bos; Login paling akhir).

**Yang dikerjakan:**
- `MASTER_PLAN.md` — **6 titik basi diperbaiki**: §9 urutan tahap · kepala berkas (status/berikutnya) ·
  §3 tabel MODUL · §6.1 ("web baru membuka 3" → **13 bentuk**) · §0 tanggal+blok Tahap 2.1 · §7 range X/M.
- `sot.py` — **penjaga BARU `_periksa_urutan_tahap()`**: membaca daftar tahap dari **dua bentuk**
  (baris tabel MASTER_PLAN & judul bab TAHAP_PENYELESAIAN), lalu memeriksa
  (a) tahap bernomor sama tidak bertentangan — dengan **peta terjemahan** (T1 buat-data ↔ T1 mesin-model, sah),
  (b) **urutan** klinik→pemilih-alat→ujian→kualitatif→login tidak terbalik.
- `TAHAP_PENYELESAIAN.md` — kalimat bertentangan sendiri dibetulkan
  (dulu: *"SUDAH DEPLOY, tapi deploy menunggu ACC"* → sekarang: sudah LIVE + bukti verifikasi).

**BUKTI:**
- `sot.py --periksa` → **SOT SELARAS**
- `_sketsa/bukti_urutan_tahap.py` → **BERGIGI**: SEHAT EXIT 0 · T4⇄T5 tertukar **EXIT 1** · T6⇄T7 tertukar **EXIT 1**
- gerbang penuh → **60 grup EXIT 0**

## 📐 21 Sep 2026 — KEPUTUSAN BESAR: **SEDERHANA = PARSIAL · BERGANDA = PARSIAL + SIMULTAN**

**Akarnya (dari Bos sendiri):** *"Sebenarnya berantai itu tidak ada, karena saat itu
saya kebingungan nyari parsialnya kok ga ada, maka saya ciptakan berantai."*
⇒ Kartu "berantai" lahir dari **kebingungan**, bukan kebutuhan. Yang Bos cari
sejak awal = **PARSIAL** — dan itu **sudah dihitung mesin**, cuma **tak ditampilkan**.

**KEPUTUSAN BOS (N1 + R1 + P1):**

| Kartu | Isi | Gambar |
|---|---|---|
| **① Sederhana** | banyak X → Y, **PARSIAL saja** | panah lurus, **tanpa** panah sudut |
| **② Berganda** | **PARSIAL + SIMULTAN** (lengkap dua-duanya) | panah lurus **+** panah sudut |

- **R1 — "berantai" DIARSIPKAN**, bukan dihapus: kode `cara='berantai'` tetap ada di
  mesin, `gerbang_s3.py` (33 uji) tetap SAH, hanya **tidak ditampilkan** di pintu.
- **P1 — NOL perubahan mesin**: kartu ① tetap pakai `cara='sederhana'` yang sudah ada.

**TEMUAN TERUKUR (21Sep26):**
- Parsial **sudah dihitung** mesin (`terpisah`) di Berganda & Berantai, tapi **tidak
  ditampilkan** — hanya `bersama` (simultan) yang muncul. **INI AKAR KEKEBINGUNGAN BOS.**
- **Uji F BELUM ADA** — grep `app/` untuk `uji_f|F_hitung|anova|f_stat` = KOSONG.
  Mesin punya R², tapi tidak punya p-value uji F ⇒ belum bisa bilang "semua X
  secara simultan berpengaruh".
- Hasil ukur nyata: Berganda vs Berantai **BEDA** (parsial 0,3971 vs 0,5118 ·
  R² 0,2543 vs 0,3680) — jadi berantai bukan duplikat, tapi tetap **tidak diperlukan**.

**URUTAN KERJA (bertahap, tiap langkah diukur, LAPOR ke Bos):**
1. **CATAT** ← ✅ SELESAI (berkas ini)
2. **UJI F + tabel ANOVA** ← ✅ SELESAI (102 uji fungsi + 16 uji halaman; dua kelompok uji baru masuk gerbang)
3. **PINTU** ← ✅ SELESAI & TERBUKTI DI LAYAR:
   · kartu ① = "Parsial (Sederhana)" · kartu ② = "Berganda (Parsial + Simultan)"
   · kartu "berantai" DISEMBUNYIKAN (kode mesin tetap utuh — Opsi R1)
   · uji_web_pintu.py 17 LULUS/0 GAGAL · penjaga kartu bergigi 5 arah
   · bukti: **GERBANG 60 GRUP SEMUA LULUS, EXIT 0**

**CACAT/CELAH YANG BELUM DITUTUP (jujur):**
· 🆕 **IDENTIFIKASI DATA di `/klinik`** — ✅ **SELESAI DIKODING 21Sep26**, BELUM deploy.
  Mahasiswa tandai peran kolom via DROPDOWN (X1/X2… M1/M2… Z… Y1/Y2…),
  mesin VERIFIKASI dulu sebelum proses. Detail: `KEPUTUSAN_PARSIAL_SIMULTAN_21SEP2026.md` §7.
  Bukti: `uji_peran_kolom` 34/0 · `uji_peran_web` 30/0 · `uji_peran_alur` 20/0 · semua BISA GAGAL.
  ⚠️ ISTILAH WAJIB: **"pembimbing"** (DILARANG "dosen") · **"Hasil"** (DILARANG "jawaban").
  ⛔ Token/kode ujian **DIBATALKAN** — ini LATIHAN, bukan ujian.
  🔴 AKAR (jangan diulang): elemen HTML dihapus → **WAJIB buang semua JS yang menunjuknya**.
  `null.innerHTML` → galat SENYAP → jalur unggah MATI, tapi dilaporkan "koneksi terputus".
  🔴 BELUM: mesin hitung **per-konstruk** (gabung 3 kolom X1 jadi 1 skor) — `/klinik` masih per kolom.
· **Tombol "Hasil" + token pembimbing** → DIBATALKAN (sebab di atas).
· **Belum deploy** — menunggu ACC Bos.
· 4 jebakan UJI yang ditemukan 21Sep26 (semua cacat UJI, bukan cacat app):
  (1) jalur absolut `sys.path` → uji dari salinan tetap baca berkas ASLI;
  (2) `innerText` TIDAK memuat teks `<th>` → "tabel tidak tampil" (palsu);
  (3) `/buat-data` polos SENGAJA `location.replace('/kuantitatif')` (opsi 1B
      19Sep26) → tab berakhir di halaman lain, selector kosong;
  (4) `bukaSub(ev, nama)` BUTUH 2 argumen; dipanggil 1 argumen → Uncaught.
  ATURAN BARU: uji pintu harus lewat `?model=` (jalur NYATA user), bukan
  `/buat-data` polos; dan GREP tanda tangan fungsi sebelum memanggil.

**BUKTI LANGKAH 1 (21Sep26):**
- `sot.py --periksa` → **penjaga BARU `_periksa_kartu_regresi()` terbukti BERGIGI 4 arah**
  (uji-suntik: kartu berantai tampil → protes · kode berantai hilang → protes ·
  kata "Parsial" hilang → protes · kata "Simultan" hilang → protes). Berkas mesin dipulihkan utuh.
- `bash gerbang_uji.sh` → **33 GRUP SEMUA LULUS, EXIT 0** ✅

**🔧 2 GAGAL PALSU yang ikut ditutup (bukan cacat aplikasi):**
Grup "GRAFIK — jalur API" & "GRAFIK — tombol contoh" GAGAL karena server uji :8122
tidak hidup saat gerbang dipanggil langsung. Akar: `uji_tombol_contoh.py` **hanya
memeriksa** server, tidak pernah **menyalakannya** (melanggar aturan "uji wajib
menyiapkan dirinya sendiri").
🚨 JEBAKAN 21Sep26 (2 putaran terbuang): server uji :8122 = **uvicorn dari BERKAS
LOKAL** (`jalankan_uji_normalitas.py`), **BUKAN kontainer Docker**. Wulan sempat
menyalakan kontainer Docker di :8122 → jalan, tapi `127.0.0.1:8122` dari dalam
container Hermes tetap `Connection refused` (lewat IP kontainer 172.17.0.x baru
HTTP 200). ⇒ **PAKAI POLA PROVEN: uvicorn lokal**. Setelah diperbaiki: **15 LULUS/0 GAGAL**.

📄 **Detail penuh:** `KEPUTUSAN_PARSIAL_SIMULTAN_21SEP2026.md`

---

# 📌 FLAG LANJUT DI SINI — Penelitian STATISTIK Lab.

**Cara balik ke proyek:** Bos bilang **"lanjut statistik"** → baca berkas ini dulu
(blok paling atas), lalu ⭐ **`.venv/bin/python sot.py`** (SOT — satu pintu, dibaca
dari KODE), lalu `bash gerbang_uji.sh`.

> ⚠️ **ATURAN SOT (arahan Bos 18Sep26):** sumber kebenaran = **KODE DI DISK**.
> Dokumen ini SALINAN. Kalau berbeda, **kode yang menang** → jalankan
> `.venv/bin/python sot.py --periksa` untuk tahu mana yang usang.

---

## 🔴🔴 ATURAN BOS — 19 Sep 2026 (WAJIB, HARAM DILANGGAR)

> *"Tambah 1 aturan, tidak boleh buru buru, selalu cek dan analisa baca secara utuh.
> Jangan sekali kali coba suntik, tambal sangat haram disini harus cari akar masalahnya."*

**LAHIR DARI KEJADIAN NYATA (19Sep26, `/belajar`):**

| Kejadian | Akar |
|---|---|
| Wulan membaca **5 baris** dari 758 baris `belajar.html`, lalu **langsung menyisipkan** kode | Tidak baca UTUH |
| Tanda Jinja `{% block skrip %}` ditulis **di dalam komentar JS** → `/belajar` **HTTP 500** | Tidak periksa struktur |
| Kode JS ditaruh **DI LUAR `<script>`** → **kode tumpah jadi teks** dilihat mahasiswa | Tidak cek posisi `<script>` |
| Tambah `<script>` padahal **sudah ada** → 2 `<script>` / 1 `</script>` | Tidak hitung tag dulu |
| Setelah rusak → **tambal → rusak lagi → tambal** (3 putaran) | MENAMBAL gejala, bukan cari akar |

### 📏 PERINTAH KERJA (urutannya, jangan dibalik)
1. **BACA UTUH** berkas yang akan disentuh — hitung `<script>`, `{% block %}`, tag seimbang, `<div>` berpasangan
2. **PAHAMI STRUKTUR** — tahu di mana kode boleh ditaruh, di mana TIDAK
3. **CARI AKAR** — kalau ada masalah, tanya "KENAPA", bukan "bagaimana cepat hilang"
4. **PERBAIKI DI AKAR** — satu perbaikan, bukan tambalan bertumpuk
5. **VERIFIKASI** semua gerbang yang relevan **SEBELUM** deploy
6. **BARU LANJUT** — jangan mengerjakan 7 hal sekaligus

### 🚫 YANG DILARANG
- ❌ Sisip kode tanpa baca berkasnya utuh
- ❌ Tambal gejala (turunkan ambang uji, matikan gerbang, hapus pemeriksaan)
- ❌ Jalankan gerbang SETELAH deploy (harus SEBELUM)
- ❌ Mengulang cara yang sama setelah gagal 2× — berhenti & lapor Bos

### ✅ CATATAN KEADAAN 19Sep26 — SUDAH SELESAI (jangan dibaca sebagai keadaan kini)
Catatan LAMA ini (keadaan saat itu: `/belajar` rusak di berkas kerja) **sudah
DITUTUP**. Bukti: `/belajar` LIVE, gerbang **25 grup LULUS** (20Sep26).

> **✅ DIPERBARUI 19Sep26 (malam, setelah teguran Bos):** semua akar sudah ditutup
> & **TAB BELAJAR SUDAH LIVE** — gerbang **24 grup LULUS (saat itu; sekarang 25)**, deploy EXIT 0,
> `uji_pita_tab.py` **22 LULUS / 0 GAGAL**, vision rapi.
> **3 AKAR DITUTUP:** (1) tanda Jinja di komentar JS → HTTP 500 (gerbang_jinja BARU);
> (2) kode JS di luar `<script>` → tumpah jadi teks; (3) uji Wulan sendiri salah ukur
> (hash tidak reload + `href` bukan bagian `textContent`).

### 🚨 TEGURAN BOS 19Sep26 — 2 KESALAHAN WULAN YANG MENYESATKAN USER
> *"Kok rusak data belum ada, malah ke diagnosa data? Dan masih banyak link yang
> kosong atau salah? Jadi membingungkan user"* + *"Kamu baca dokumentasi dulu deh
> jangan suka tebak. Kita selalu Sot single source of truth"*

| Kesalahan | Akar | Perbaikan |
|---|---|---|
| Kartu **"Rusak Data"** disambung ke **`/klinik`** padahal mesinnya BELUM ada | Wulan **melompat ke TAHAP 3** tanpa mesinnya (dokumen Bagian F bilang TAHAP 3 = Ruang Uji) | Kartu DILEPAS → diganti pemberitahuan jujur "Ruang Uji belum dibuka" + 3 pintu ke yang SUDAH jalan |
| Wulan **menebak**, tidak baca dokumen | Wulan mengabaikan **SOT single source of truth** | Wulan WAJIB baca dokumen keputusan + SOT SEBELUM menyentuh apa pun |

**ATURAN BARU (dari teguran ini):** 🚫 Fitur belum jadi JANGAN dipasang walau
berlabel "sedang disiapkan", apalagi dengan tautan ke halaman lain.
✅ Kalau belum ada → tulis jujur "belum dibuka" + arahkan ke yang SUDAH jalan.

---

## ✅ 20 Sep 2026 (PALING AKHIR) — TAHAP 2.4b + 2.6 SELESAI: **FORNELL-LARCKER + HTMT + 2 CACAT GERBANG**

**Status:** ✅ **LIVE DI PRODUKSI** (deploy 20Sep26 kedua, `DEPLOY_EXIT=0`) — kontainer `simulasi-olah-data` Up (healthy) port 8120 · image `20260920_175348-statlab`
**Gerbang:** **60 grup LULUS** · SOT **SELARAS**
**Bukti terukur:**
- `uji_fornell_htmt.py` — **10 LULUS / 0 GAGAL** (rumus, memanggil fungsi ASLI `_fornell_htmt`)
- `uji_web_fornell_htmt.py` — **10 LULUS / 0 GAGAL** (unggah → periksa → kartu HTMT sampai halaman)
- `gerbang_tata_letak.py` — **45 LULUS / 0 GAGAL** lawan KONTAINER (jalur normal)
- `uji_nasihat.py` **68 LULUS** · `uji_web_diagnosis.py` **37 LULUS**

**YANG DITAMBAHKAN (Fornell-Larcker + HTMT):**

| Uji | Arti bagi mahasiswa | Ambang |
|---|---|---|
| **Fornell-Larcker** | tiap variabel lebih erat dengan butirnya sendiri daripada dengan variabel lain | korelasi < akar AVE |
| **HTMT** | dua variabel tidak boleh kembar | < 0,85 aman · 0,85–0,90 catatan · > 0,90 perbaiki |

Nasihat lengkap (arti/kenapa/4 langkah/jangan) ditambahkan ke `nasihat.py` sebagai `HTMT` — bahasa hangat, ada jalan keluar. Angka nyata dari server: korelasi −0,007 < batas 0,917 · HTMT 0,053.

**2 CACAT GERBANG DITUTUP (keduanya GAGAL PALSU, bukan bug aplikasi):**

| # | Cacat | Akar | Fix |
|---|--|---|---|
| 1 | `uji_nasihat.py` & `uji_web_diagnosis.py` memaku **`== 5`** nasihat PLS | HTMT ditambahkan → PLS jadi 6 → uji protes padahal benar | hitung dari KAMUS (`len(nasihat.PLS)`), bukan angka mati |
| 2 | `ukur_tata.html` menembak `/buat-data` **tanpa `?model=`** | Sejak Tahap 1.4, `/buat-data` tanpa `?model=` **SENGAJA dialihkan** ke `/kuantitatif` → iframe pindah → pengukur cari `#x-slider` di halaman yang SALAH | `/buat-data?model=sederhana&uji=x8` |

**⚠️ TEMUAN PENTING — TAB YATIM CDP = GAGAL PALSU 140 DETIK.** Bos yang menemukan: *"Chrome terlalu banyak uji, jadi penuh."* Terukur: **6 tab yatim** (sisa uji sebelumnya: 3× kuantitatif, 2× sketsa, 1× blank) → Chrome menggantung persis **140 detik**. Setelah `/json/close/<id>` **semua** (JANGAN `pkill` — mematikan shell sendiri) → gerbang jalan normal. **Ini kejadian KEDUA** (pertama 27 tab). **ATURAN: kosongkan tab yatim SEBELUM menjalankan gerbang berbrowser.**

**PELAJARAN:** (1) Jangan paku ANGKA di uji — hitung dari sumbernya. (2) Kalau Chrome menggantung, **cek jumlah tab DULU**, jangan langsung tuduh kode. (3) Saat gerbang melaporkan "elemen tidak ditemukan", **periksa halaman mana yang SEBENARNYA diukur** (bisa kena pengalihan).

---

## ✅ 20 Sep 2026 (sebelumnya) — TAHAP 2.1 SELESAI: **GRAFIK HIDUP + TAB "BACA GRAFIK"**

> 📌 Blok di bawah ini **catatan sejarah** — angkanya (31 grup, image `155453`) benar **untuk saat itu**.

**Status:** ✅ **LIVE DI PRODUKSI** (deploy 20Sep26, `DEPLOY_EXIT=0`) — kontainer `simulasi-olah-data` Up (healthy) port 8120 · image `20260920_155453-statlab`
**Gerbang:** **31 grup LULUS** · SOT **SELARAS**
**Verifikasi produksi:** `_sketsa/verifikasi_produksi.py` 18 LULUS · `_sketsa/verifikasi_produksi_tahap2.py` **14 LULUS / 0 GAGAL** (periksa ISI, bukan log)
**Dokumen lengkap:** `DOKUMENTASI_TAHAP_2_GRAFIK_HIDUP_20SEP2026.md`

**APA YANG BERUBAH DI MATA MAHASISWA:**

| # | Sebelum | Sesudah |
|---|---|---|
| ① | 7 grafik di `/syarat` = **gambar SVG statis** (sama untuk semua orang) | **grafik hidup** di `/klinik`, dihitung dari data yang diunggah mahasiswa |
| ② | `/syarat` dan `/klinik` = **dua pintu bingung** | satu jalur: **BELAJAR = KAMUS** (tab ke-3 **"Baca Grafik"**), **KLINIK = ALAT** |
| ③ | mahasiswa harus punya data sendiri dulu | **2 tombol contoh** di Langkah 2: *Contoh sehat* / *Contoh bermasalah* — kolom terisi otomatis |
| ④ | menu 8 pintu | menu **7** (KAMUS GRAFIK keluar; `/syarat` **dialihkan 308**, tidak dihapus) |

**KEPUTUSAN BOS 20Sep26:** nama tab ke-3 = **"Baca Grafik"** (usulan "Interpelasi" DITOLAK — itu istilah DPR; yang benar "Interpretasi"). Sketsa di-ACC penuh (1 Ok / 2 Ok / 3 Ok).

**TERUKUR (bukan klaim):**

| Lapisan | Bukti |
|---|---|
| Mesin (bahan gambar) | `uji_bahan_gambar.py` **33 LULUS** |
| Fungsi gambar | `uji_grafik_hidup.js` **24 LULUS** — corong terukur **1,3× lebih lebar** kanan vs kiri |
| Halaman `/klinik` | `uji_web_grafik.py` **18 LULUS** via unggah → periksa |
| Jalur mahasiswa + tab | `uji_tab_baca_grafik.py` **16 LULUS** |
| Uji gambarnya sendiri | `uji_alat_ukur_grafik.py` **22 LULUS** + **terbukti BERGIGI** (4 kerusakan nyata → EXIT 1) |
| Mata | P-P tampil · **corong terlihat sangat jelas** pada data bermasalah · warna merah saat bermasalah |

**🐛 CACAT NYATA YANG DITEMUKAN & DITUTUP DI AKAR:**

| # | Cacat | Akar jujur | Bahaya |
|---|---|---|---|
| ① | `skala()` **salah rumus** | 2 makna beda dalam satu nama (`dari` = nilai data, `ke` = koordinat tujuan) | titik TUMPAH keluar bingkai (200 titik jatuh di x=9…26, padahal bingkai 34…300) |
| ② | pasangan titik **tertukar** | `sebar()` dipanggil **terpisah** untuk zpred & zresid → titik ke-7 dari baris data BERBEDA | gambar omong kosong yang **"kelihatan masuk akal"** (jenis paling berbahaya — lolos dari mata) |
| ③ | **`n is not defined`** | **BUG LAMA** (ada di cadangan baris 400 SEBELUM Tahap 2) — `const n = d.normalitas` ada di dalam blok SPSS (TDZ) → error ditelan `catch` | halaman **mati** setiap habis unggah; mahasiswa cuma lihat *"Koneksi ke server terputus"* |
| ④ | `#}` dipakai sebagai penutup **komentar JS** | Wulan menyalin gaya komentar Jinja (`{# #}`) ke dalam JavaScript | **1 komentar tak tertutup → SELURUH 26.716 byte skrip MATI** (HTTP 200, konsol cuma 404 favicon) |
| ⑤ | ⭐ **`const n = zp.length` (3 fungsi)** | memakai panjang **satu** larik, padahal dua larik bisa **beda panjang** (ada baris kosong) | titik **`NaN` yang hilang tanpa galat**; dan pada data >500 baris, jumlah titik **melampaui batas jaga 500** (terukur 5000 lingkaran). **Ditemukan dari uji-suntik** yang bilang "kerusakan ini lolos" — BUKAN dari membaca kode. |

**⚠️ JEBAKAN BARU TERUKUR (20Sep26, jangan ulang):**

1. **`(0, eval)` di Node TIDAK membocorkan `const`** — hanya `function`. `BATAS_TITIK` → `undefined`. Yang benar: `vm.runInThisContext` + ekspor **eksplisit** ke `globalThis` (pola `uji_grafik_hidup.js`).
2. **Uji yang hanya MENGHITUNG belum tentu BERGIGI** — uji Wulan sempat melaporkan "petakan() dirusak → LOLOS". Yang salah **skrip pembuktinya**: pakai `sys.executable` (Python LUAR) → `import app.diagnosis` mengambil berkas dari jalur asli, bukan salinan tersuntik. WAJIB pakai `<salinan>/.venv/bin/python` + `cwd=salinan`.
3. **Gerbang TIDAK BOLEH memotret.** `Page.captureScreenshot` pada halaman 6000+ px kena `WebSocketTimeoutException` → grup uji **GAGAL padahal 16 asersinya LULUS**. Potret = untuk mata; gerbang = untuk kode. Potret dipindah ke `_sketsa/potret_tab_baca_grafik.py`.
4. **Gerbang sekarang bisa jalankan `.js`** — `gerbang_uji.py` memakai `node` (lewat `shutil.which`) untuk berkas berakhiran `.js`, Python venv untuk sisanya.
5. **Data contoh harus BENAR-BENAR sehat.** Versi pertama tombol *"Contoh sehat"* memakai derau `sin(i*5.7)` = pola **teratur berulang** → Shapiro p=0,0000 (**GAGAL normalitas**) → **tombolnya berbohong**. Yang benar: **jumlahkan 6 gelombang beda frekuensi** → mendekati normal (SW 0,609) **tetap deterministik** (hasil sama tiap klik, mahasiswa bisa membandingkan).

**PELAJARAN STATISTIK TERUKUR:** Glejser menguji `|sisa|` vs X **secara linear** → corong yang membesar **linear tidak tertangkap** (`1+1,5|x₁|` p=0,44 · `1+3|x₁|` p=0,31 · `1+5|x₁|` p=0,18); yang tertangkap corong **eksponensial** (`exp(1,2·x₁)`, p=0,0000). Layak jadi bahan ajar.

**SISA TAHAP 2:** 2.2 Linearitas · 2.3 VIF + hetero (sebagian sudah) · 2.4 Khas PLS (Outer Loading · AVE · CR) · 2.5 Pemisah jelas mana SPSS mana PLS.

---

## ✅ 20 Sep 2026 — TAHAP 1.6 SELESAI: **NORMALITAS + TOMBOL PINTASAN HETERO**

> 📌 Blok ini **catatan sejarah** — angka 31 grup benar untuk saat itu (sekarang 33).

**Status:** ✅ **LIVE** di `statistik.bikinaja.id/belajar` (tab **Materi & Kamus**)
**Gerbang:** **31 grup LULUS** · deploy `jalankan.sh` **DEPLOY_EXIT=0** · kontainer `Up (healthy)`
**Verifikasi produksi:** `_sketsa/verifikasi_produksi.py` **18 LULUS / 0 GAGAL**
**Dokumen lengkap:** `DOKUMENTASI_TAHAP_1_6_NORMALITAS_20SEP2026.md`

**KEPUTUSAN BOS 20Sep26:**

| # | Pertanyaan | Pilihan |
|---|---|---|
| ① | Judul tab uji t | **`Uji t: masalah uji t`** (1 tempat: tombol kamus) |
| ② | Kartu hetero | **Variasi B** — slider tetap + 2 tombol `Contoh sehat`/`Contoh sakit` |
| ③ | Kartu normalitas | **Variasi 1** — slider **DUA ARAH** (miring kiri ↔ lonceng ↔ miring kanan) |
| ④ | Nama kartu | **`Normalitas`** |
| ⑤ | Uji baru masuk gerbang | **Boleh** → `uji_normalitas.py` + `gerbang_sintaks_js.py` |

**YANG DIPASANG:** 8 tombol kamus (dulu 7, +`Normalitas`) · 2 tombol pintasan ·
fungsi `kalimatTafsir()` (kalimat penegas **HIDUP** mengikuti slider) ·
fungsi `pintasanPasang()` · CSS `.pintasan-baris`/`.pintasan`/`.pintasan.nyala`.

**🚨 AKAR TERBESAR — satu `}` mematikan SELURUH halaman:**
Skrip `sisip_kamus_normalitas.py` Wulan memakai penanda
`P_AKHIR_KAMUS = "  },\n  beta: {\n"` → `replace()` **menghapus penutup entri
`hetero`** → `normalitas: {` jatuh ke dalam hetero → `SyntaxError` →
**SELURUH 50.177 karakter skrip MATI** (termasuk kamus yang sudah jalan
berbulan-bulan). Halaman tetap **HTTP 200**, konsol cuma **404 favicon**.
**Perbaikan di akar:** tambah `},` penutup entri hetero.
**Pelajarannya: `HTTP 200 + konsol bersih ≠ kode jalan.`**

**🚪 GERBANG BARU (grup ke-25): `gerbang_sintaks_js.py`**
Menutup lubang yang **4 gerbang lama tidak sentuh** (`gerbang_jinja` lolos karena
Jinja tak lihat JS · `gerbang_tag_skrip` urusannya tag HTML · `gerbang_galat_js`
hanya berkas `.js` berdiri sendiri · `gerbang_kode_tumpah` hanya teks user).
**Cara:** render Jinja dulu → `node --check` tiap `<script>` inline.
**TERBUKTI BISA GAGAL:** buang 1 `},` → EXIT 1 · dipulihkan → EXIT 0.

**⚠️ 3 KESALAHAN WULAN DI SESI INI (semua TERULANG dari sebelumnya):**

| # | Kesalahan | Akar | Pelajaran |
|---|---|---|---|
| 1 | Pakai ikon **`bell`** yang **TIDAK ADA** di sprite | Wulan **mengarang nama ikon** — **persis** kesalahan 19Sep26 (`--tinta-1`, `arrow-left-right`) | GREP dulu nama apa pun. `gerbang_ikon.py` yang menangkap |
| 2 | Skrip sisip Wulan **merusak berkas** | Penanda `replace()` **menghapus penutup entri lama** | Penanda WAJIB memuat **PEMBUKA + PENUTUP** entri; verifikasi `node --check` **HASIL RENDER** |
| 3 | Uji Wulan **salah ukur** (menuduh aplikasi) | Menuntut slider `0` padahal berkas **ASLI** memang `value="35"` | Periksa **perilaku ASLI di cadangan** dulu sebelum menuduh app |

**⚠️ Wulan juga 2× SALAH SIMPUL soal `</strong>`** — menghitung di SELURUH berkas
(46× sekarang, 32× di cadangan) → menyangka cacat lama. **Padahal hanya tag
DI DALAM `<script>` yang berbahaya.** Cara pasti: jalankan gerbang pada
**cadangan ASLI** di salinan terpisah (hasilnya: 0 pelanggaran, EXIT 0).

**SISA 1.6:** potret layar akhir **belum ada** (Chrome `--screenshot` tidak
berfungsi di lingkungan ini — bukan cacat aplikasi) · kartu **Campuran**
di `/kuantitatif` masih belum punya sub-pilihan (sisa 1.3).

**⚠️ TAMBAHAN: CHROME :9333 DIPAKAI BERSAMA (jangan dimatikan!)**
`uji_normalitas.py` masuk gerbang sebagai **grup ke-26** → awalnya GAGAL.
Akarnya berlapis & semua terukur:
1. `uji_normalitas.py` dulu **tidak berdiri sendiri** (server uji :8122 disiapkan
   berkas LAIN) → dipanggil gerbang langsung = halaman kosong = GAGAL PALSU.
   **FIX:** ia kini menyalakan server-nya sendiri (`_nyalakan_server()`).
2. **JANGAN menyalakan Chrome sendiri** — 3 cara dicoba, GAGAL SEMUA
   (`pkill -f` mematikan shell sendiri · `Popen`+`--user-data-dir` keluar karena
   dbus/GLib · `nohup &` dari shell mati begitu shell selesai). Sebab terukur:
   Chrome yang bertahan (:9333, :9444) punya **`PPID = 1`** — dijalankan lewat
   `terminal(background=true)` Hermes. **PAKAI Chrome :9333 yang SUDAH HIDUP.**
3. **JANGAN tutup semua tab** milik Chrome bersama — `uji_sub_regresi.py`
   **mensyaratkan minimal 1 tab**; kalau ditutup semua → dia gagal "tidak ada tab".
   **FIX:** tutup HANYA tab milik uji sendiri (`self.tab_id`), Chrome-nya jangan
   dimatikan, dan `tab = None` diletakkan SEBELUM `try`.
   Sediakan tab: `curl -s -X PUT "http://127.0.0.1:9333/json/new?about:blank"`.
4. **`sot.py`**: regex `(\d+) grup` dulu MENUDUH semua angka riwayat usang →
   SOT mustahil hijau. Kini ada pengecualian konteks ("saat itu"/"keadaan 20xx")
   dan **terbukti masih bisa gagal** (suntik 25→22 → EXIT 1).

**BUKTI AKHIR:** `uji_normalitas.py` **57 LULUS** · `uji_sub_regresi.py` **46 LULUS**
(berdampingan) · gerbang **31 GRUP · EXIT 0** · SOT **SELARAS**.

**📌 PELAJARAN INDUK BARU:** *"Sumber daya yang DIPAKAI BERSAMA jangan dimatikan
oleh pihak yang tidak memilikinya."*

---

## ✅ 19 Sep 2026 (malam, paling akhir) — TAHAP 1.5 SELESAI: **DIAGNOSIS DATA SPSS & PLS**

**Status:** ✅ **LIVE** di `statistik.bikinaja.id/klinik` (alias `/diagnosis`)
**Gerbang:** **23 grup LULUS (saat itu; keadaan 20Sep26 = 25 grup)** · deploy `jalankan.sh` **EXIT 0**
**Dokumen lengkap:** `DOKUMENTASI_TAHAP_1_5_DIAGNOSIS_19SEP2026.md`

### 🎯 PERINTAH BOS (VERBATIM)
> *"Halaman Syarat, jadikan tool / alat saja. Namanya **Diagnosis Data SPSS & PLS**.
> Isinya user upload data dari spss atau pls, untuk didiagnosa dan cara tulisnya.
> **Benar katakan benar, salah katakan salah** dan beri panduan untuk cara
> membetulkan data."*

### ✅ YANG JADI
- `/diagnosis` = **ALAT**: unggah `.sav`/`.csv`/`.xlsx` (maks 10 MB) → periksa → jawab.
- **Mode SPSS (6 uji):** normalitas, heteroskedastisitas (Glejser),
  multikolinearitas (VIF), linearitas, outlier, autokorelasi (Durbin-Watson).
- **Mode SmartPLS (5 uji):** outer loading, AVE, composite reliability,
  VIF inner, Fornell-Larcker.
- **11 nasihat "cara membetulkan"** (`app/nasihat.py`) — tiap nasihat 5 bagian:
  arti · kenapa · **kapan boleh diabaikan** · langkah bernomor · yang JANGAN dilakukan.
- **Kedua-duanya 200:** `/klinik` (slug menu) + `/diagnosis` (alias enak diketik).

### 🔤 PERUBAHAN NAMA (keputusan Bos)
| Sebelum | Sesudah |
|---|---|
| menu `KLINIK` | **`DIAGNOSIS DATA`** (slug TETAP `klinik`) |
| menu `PERIKSA SYARAT` | **`KAMUS GRAFIK`** (`/syarat` DIBIARKAN) |

⚠️ **Wulan hampir salah mengubah SLUG** `klinik` → `diagnosis`. Keputusan Bos:
**NAMA** berubah, **slug tetap**. Pelajaran: **baca dokumen keputusan dulu**.

### 🚨 4 AKAR YANG DITUTUP (semua terukur)
| Akar | Gejala | Fix |
|---|---|---|
| **A.** `pd` tidak diimpor di route | unggah → **HTTP 500** | tambah `import pandas as pd` |
| **B.** **nama parameter DITEBAK** | periksa → **HTTP 500** (2 putaran) | `grep "^def"` → `buang_kosong`, `kolom_y_konstruk`, `lulus_muat`, `muat` |
| **C.** 22 tag penutup mentah di `<script>` | gerbang GAGAL → **kode TUMPAH jadi teks** | escape → `<\/div>` (skrip `_sketsa/perbaiki_tag_skrip.py`) |
| **D.** 🚨 **GERBANG IKON PALSU ke-2** | `play-circle` (menu MULAI) KOSONG, gerbang bilang aman | gerbang ikut pindai `main.py` → 102 pemakaian (dulu 94) |

**Akar B detail — 9 nama yang Wulan tebak SALAH:**
`missing`→`buang_kosong` · `kolom_target`→`kolom_y_konstruk` · `lulus_cl`→`lulus_muat`
· `loading_min`→`muat` · `n_baris`→`n` (di `/periksa`) · `kolom_y`→`y_konstruk`
· `vif_inner_maks`→(tidak ada).

⚠️ **JEBAKAN KEMBAR:** `/unggah` kirim **`n_baris`**, `/periksa` kirim **`n`**.
Satu halaman, DUA nama beda → uji yang salah nama = GAGAL PALSU.

### ⚖️ PELAJARAN WAJIB (Bos menegur 2×)
> *"Kamu tambah bodoh, cek dulu alat yang dipakai kemarin, jangan buat-buat
> script, semua sudah ada. Cek dulu."*

- **JANGAN tulis alat baru** — cari dulu: `uji_jalur_tampilan.py` (`class Tab`
  proven, socket mentah, TIDAK kena 403), `potret.py`, `tangkap_sketsa_diagnosis.py`.
- `potret.py` kena **403** karena Chrome 9333 lama tidak punya
  `--remote-allow-origins`. **JANGAN ubah** — pakai `Tab` (socket mentah tidak
  kirim header `Origin`).
- `websocket` (paket) **ADA** di venv proyek (1.9.2) — tapi tetap pakai `Tab`.
- **Cara kemarin yang bisa:** `chrome --headless --dump-dom` ke URL app
  sungguhan (pola `uji_halaman.py`), lalu potret.

### 📌 ATURAN BARU
1. **`grep "^def"` sebelum memanggil** — jangan tebak nama parameter.
2. **Sebelum menulis alat: CARI alat yang sudah ada** (aturan Bos, teguran 2×).
3. **Gerbang ikon WAJIB memindai `main.py`** juga, bukan hanya `templates/`.
4. **Baca dokumen keputusan sebelum ganti nama/slug.**

### 📊 BUKTI TERUKUR
| Hal | Angka |
|---|---|
| Mesin diagnosis | 23 LULUS / 0 GAGAL |
| Nasihat | 63 LULUS / 0 GAGAL |
| Jalur web (HTTP) | 37 LULUS / 0 GAGAL |
| Alat ukur uji | 9 LULUS (terbukti bisa gagal) |
| **Gerbang** | **23 GRUP LULUS · EXIT 0** |
| Deploy | EXIT 0 · `/klinik` 200 · `/diagnosis` 200 |
| Vision | *"Sangat rapi, tidak ada tumpang tindih/meluber/kosong"* |

**INTI:** data **bersih** `R²=0,42 · VIF=1,0 · masalah=[]` vs data **sakit**
`VIF=8656 · masalah 3` ⇒ *"benar katakan benar, salah katakan salah"* **terbukti**.

### ⬜ SISA dari 1.5
Tombol **Unduh PDF** · **HTMT/Q²/SRMR** (PLS) · **Fornell-Larcker** di mesin ·
data sakit sengaja + kunci jawaban dosen (masuk TAHAP 3).

---

## ✅ 19 Sep 2026 (malam, lanjutan) — TAHAP 1.4 SELESAI: BAR "MODEL KAMU SEKARANG"

### 🎯 KEPUTUSAN BOS (Wulan jelaskan alur DULU, baru koding)

Bos: *"Tanya dulu apa yang akan dikerjakan 1.4 ini alur kerjanya"* → Wulan
jelaskan alur + 4 hal jujur → Bos pilih **①B** (tanpa model → arahkan balik ke
`/kuantitatif`, JANGAN terka) + **②A** (tombol ganti model MENEMPEL di atas).

### ✅ YANG JADI
- Bar `#bar-model` (HTML, bukan dibuat JS) — label + nama model + tombol Ganti.
- **1B:** `location.replace('/kuantitatif')` bila tanpa `?model=` — ⚠️ sengaja
  `replace` supaya tombol mundur tidak terjebak lingkaran.
- **2A:** bar `position: fixed` + penyeimbang `padding-top` via `:has()`.

### 🚨 AKAR TERPENTING — `sticky` GAGAL (hanya ketemu dari MATA)
Terukur: `top` **258 → −1142** setelah scroll 1400. Akar: **gaya.css baris 554**
`html, body { overflow-x: hidden }` → `<body>` jadi scroll container →
`sticky` mati untuk semua anaknya. ⚖️ Aturan itu **sengaja ada** (cegah halaman
melebar di HP) → **DILARANG dihapus** (menambal satu, merusak lain) →
dipakai `fixed`. Uji penjaga: *"halaman TIDAK bisa digeser ke samping (390 ≤ 390)"*.

### 🐛 9 CACAT DITUTUP (2 kelas baru ditemukan)
- **8 IKON KOSONG** tersembunyi lama (`skull`, `clock`×3, `play-circle`,
  `calendar`, `history`, `message-square`) + `arrow-left-right` ×2 →
  `ikon()` **tidak memvalidasi** nama ke sprite → `<use>` kosong **TANPA galat**.
- **GERBANG PALSU**: regex `ikonKecil?` salah tulis (cocok `ikonKecil`, BUKAN
  `ikon`) → gerbang selalu bilang "semua ADA". BENAR: `(ikonKecil|ikon)`.
  ⚠️ Pelajaran: **gerbang WAJIB diuji bisa GAGAL** (suntik kerusakan → EXIT 1).

### 🔬 BUKTI
`gerbang_uji.sh` **23 grup LULUS (saat itu; keadaan 20Sep26 = 25 grup)** · `uji_bar_model.py` **32 LULUS/0 GAGAL**
(termasuk *"terbukti menempel (top=0 saat scroll)"*) · `gerbang_ikon.py` 87 ikon
vs 86 pemakaian · vision *"bar hijau di paling atas, rapi"* · deploy 21–22 EXIT 0 ·
SOT SELARAS (menangkap 17→19→23→25 grup).

### ⚠️ PELAJARAN INDUK
**Membaca ATRIBUT ≠ mengukur PERILAKU.** Wulan pertama cuma membaca
`position:sticky` dari CSS → bilang LULUS, padahal di halaman nyata bar
TERGULUNG. Sekarang uji mengukur `getBoundingClientRect().top` SETELAH scroll.

### 📌 SISA
Kartu **Campuran** belum punya sub-pilihan · tinggi bar di layar lebar belum
diuji terpisah · **TAHAP 2 = PERIKSA SYARAT** (grafik SPSS + PLS) berikutnya.

📄 `DOKUMENTASI_TAHAP_1_4_19SEP2026.md`

---

## ✅ 19 Sep 2026 (malam) — TAHAP 1.3 SELESAI: PINTU MODEL 3/10 → 13 BENTUK TERBUKA

### 🎯 KEPUTUSAN BOS (diskusi → ACC → koding)

Bos: *"Ok lanjut taham 1.3"* → sub-pilihan **Regresi dulu (opsi 2a)** +
**sub-pilihan di halaman yang sama (opsi 1a)**. Lanjut *"Lanjut langkah B"*
(Mediasi), lalu *"Lanjutkan langkah C"* (Moderasi).

### 🔨 YANG DIKERJAKAN — 4 KARTU INDUK → KLIK → SUB-PILIHAN

| Kartu induk | Sub | Slug |
|---|---|---|
| **Regresi** | 3 | `sederhana` · `berganda` · `berantai` |
| **Ada perantara** (Mediasi) | 4 | `mediasi` · `mediasi-paralel` · `mediasi-berjenjang` · `mediasi-campuran` |
| **Ada yang memperkuat** (Moderasi) | 6 | `moderasi` · `-dual` · `-jalur-a` · `-jalur-b` · `-keduanya` · `-3jalur` |
| **Campuran** | 0 | *(langsung ke `/buat-data?model=gabungan`)* |

**13 bentuk mesin terbuka di UI** (sebelumnya 3). Tombol `bukaSub()`/`tutupSub()`.

### 🎉 TEROBOSAN — 3 BENTUK YANG DULU "BELUM TERUJI" TERBUKTI JALAN

| Bentuk | Status lama | Hasil ukur 19Sep26 |
|---|---|---|
| Moderasi **Jalur B** | ❓ belum pernah | ✅ 0,0148 |
| Moderasi **Keduanya** | ❓ belum pernah | ✅ **0,0062** (terbaik!) |
| Moderasi **3-jalur** | 🔴 pernah GAGAL (bug `item_per`) | ✅ 0,0362 |

**8 dari 8 koefisien interaksi TEPAT** (X×Z→M, M×Z→Y, X×Z→Y, X×Z1→M, M×Z2→Y).
⇒ Bug `item_per` 18Sep26 **sudah tidak menggigit**.

### 🐛 7 JEBAKAN KENA (detail: `DOKUMENTASI_TAHAP_1_3_19SEP2026.md`)

1. **Kelas salah** — hampir pakai `.pintu` (itu kartu `/mulai`); benar `.kartu-pilih`.
2. **Escape dobel** `<\\/strong>` → gerbang tag skrip menangkap 2 pelanggaran.
3. **Uji menyalahkan aplikasi** — "GAGAL: 5 kartu" padahal kartu ke-5 terkunci.
4. **Diagram menyesatkan** (ketemu dari **VISION**) — panah rantai tak bermata
   + hanya X3 punya jalur ke Y padahal teks "bersama-sama ke Y".
5. **Menguji alat yang salah** — mediasi diuji lewat `buat_data` (cuma data mentah).
6. **Salah baca bentuk hasil** — `hasil` = `{"X->M": 0.5498}`, bukan daftar dict.
7. **`sed` GAGAL SENYAP** — dikira sudah ganti, ternyata belum; ketahuan dari
   **ukuran berkas** (144.729 → 135.251 byte).

### 🔬 BUKTI

- `gerbang_uji.sh` → **25 grup LULUS** (19 lama, + uji diagnosis 19Sep26, + gerbang sintaks JS 20Sep26)
- `uji_sub_regresi.py` → **46 LULUS / 0 GAGAL**
- Geometri HP 390px → 6 kartu Moderasi **346×224px** (pas, tidak terpotong)
- Tautan 7 slug Moderasi + 4 slug Mediasi → **semua menerapkan jalur**
- Vision → diagram Regresi, Mediasi, Moderasi **benar**
- Deploy **16–20 EXIT 0**, `/health` ok · SOT selaras

### ⏭️ BERIKUTNYA

**TAHAP 1.4** — tombol ganti model selalu terlihat.
**Sisa:** kartu Campuran belum punya sub · 3-jalur galat 0,0362 dekat batas.

📄 **Dokumen lengkap:** `DOKUMENTASI_TAHAP_1_3_19SEP2026.md`

---

## ✅ 19 Sep 2026 — KARTU UJI t LIVE di /belajar + 3 JEBAKAN BARU DITUTUP

### 🎯 PERMINTAAN BOS (diskusi → ACC → koding, semua di 18-19Sep26)

Bos bertanya: *"sering pada uji t mahasiswa menemukan hasilnya signifikan tapi
nilainya negatif. Bagaimana penjelasan kamu?"*

Lalu berkembang jadi **3 putaran diskusi** dan jadi **1 kartu BELAJAR baru**:

| Putaran | Pertanyaan Bos | Keputusan |
|---|---|---|
| 1 | Kenapa signifikan kok negatif? | 6 sebab (hipotesis berlawanan, skala terbalik, VIF, pencilan, konsep kebalikan, salah Y) |
| 2 | Apa saja keluaran uji t? Bisa tidak signifikan + positif/negatif? | **4 kuadran (Sig × tanda) + marginal** → jadi **5 kotak hasil** |
| 3 | Bisa tunjukkan sebab + cara memperbaiki? Apakah itu curang? | **Lapis ③**: sebab + cara + label ✅SAH/⚠️HATI-HATI/❌CURANG + **5 Cara Hack** |

### 📐 STRUKTUR KARTU — 3 LAPIS (ACC Bos 1A·2A·3A)

```
LAPIS ①  "Hasilmu yang mana?"   5 kotak: 4 kuadran + 1 marginal
LAPIS ②  Arti + contoh penulisan  ✓ Tulis seperti ini / ✗ Jangan menulis
LAPIS ③  Sebab & cara memperbaiki tabel + label SAH/HATI-HATI/CURANG
         + uji lakmus ("karena datanya begini, atau karena tidak suka hasilnya?")
         + KARTU "5 Cara Hack yang Harus Dihindari" (kepala MERAH)
         + tombol "Belum yakin datanya benar?" → daftar periksa 5 langkah
```

### 🎨 KEPUTUSAN TAMPILAN (Bos pilih dari 3 variasi sketsa)
- **Judul**: *"5 Cara Hack yang Harus Dihindari"* (Bos ganti dari "5 cara yang kamu hindari")
- **Kartu HACK**: **strip KEPALA MERAH** `rgb(168,90,90)` — badan tetap putih
  (Bos: *"strip gelap tapi warna merah"*). Kontras tanpa tabrakan dengan tema kertas hangat.
- **Daftar periksa**: pakai **TOMBOL** (tersembunyi dulu, muncul saat diklik)

### 🧠 DUA MISKONSEPSI YANG DITANGANI (bukan satu)
1. *"Sig. 0,003 tapi B negatif"* → disangka tidak berpengaruh. **SALAH** — ada pengaruh nyata, arah berlawanan.
2. *"Sig. 0,142 tapi B positif"* → disangka "positif lemah". **SALAH** — kalau tidak signifikan, **tandanya TIDAK BOLEH ditafsirkan**.

> 📌 Miskonsepsi ke-2 baru muncul karena **Bos yang memancingnya** dengan pertanyaan
> putaran ke-2. Wulan hampir membuat kartu yang hanya menangani satu.

### 🚨 TIGA JEBAKAN BARU (semua TERUKUR, jangan ulang)

**1. URUTAN PEMUATAN SKRIP — kode benar, hasil tetap salah**
- Galat: `ReferenceError: Cannot access 'ujitAktif' before initialization`
- Urutan **baris** sudah benar (deklarasi 1015, panggilan 1138) → tetap galat.
- **AKAR:** `<script src="kartu_uji_t.js">` ditaruh sebelum `</body>`
  → di Jinja letaknya **SETELAH** `{% block skrip %}` → data dimuat **setelah dipakai**.
- **FIX:** pindah ke **`<head>`**. Halaman jadi hidup (5 kotak, tabel, tombol jalan).
- 📌 **ATURAN: kalau kode sudah benar tapi hasil tetap salah, JANGAN ubah kode lagi —
  cari hal lain yang URUTANNYA berbeda.**

**2. TAB YATIM MEMBUAT GERBANG PALSU-GAGAL**
- Gerbang geometri timeout 140 detik padahal kode sehat (deploy9/10/11 lulus).
- **AKAR:** **27 tab tertinggal** di sesi CDP 9333 (20 tab `/belajar`).
- **BUKTI:** setelah dibersihkan → gerbang yang timeout tadi **LULUS 24,9 detik**.
- **CEGAH:** `curl -s localhost:9333/json/list | grep -c '"type": "page"'` dulu.
  **JANGAN `pkill chrome`.**

**3. TANGKAPAN LAYAR CDP GAGAL DI HALAMAN TINGGI**
- `Page.captureScreenshot(captureBeyondViewport=True)` → *"Unable to capture screenshot"*.
- **FIX:** batasi tinggi viewport, screenshot **tanpa** `captureBeyondViewport`;
  wajib cek ukuran berkas >10 KB.

### 📊 HASIL TERUKUR (bukan klaim)
| Uji | Hasil |
|---|---|
| Gerbang utama | ✅ **SEMUA 23 GRUP LULUS** |
| Uji kartu uji t (halaman sungguhan) | ✅ **13 LULUS / 0 GAGAL** |
| Gerbang tag skrip | ✅ 0 pelanggaran (48 tag di-escape) |
| Meluber keluar layar HP | ✅ **0 elemen** |
| Kode tumpah | ✅ **0 kata mencurigakan** |
| Live | ✅ **statistik.bikinaja.id/belajar** |

### 📁 BERKAS BARU
| Berkas | Isi |
|---|---|
| `app/static/kartu_uji_t.js` | data 5 hasil × sebab × cara + 5 cara hack (dibangkitkan) |
| `_sketsa/data_uji_t.py` | **SUMBER** data kartu — ubah di sini, jalankan ulang |
| `_sketsa/css_ujit.css` | CSS kartu uji t (digabung ke `gaya.css`) |
| `_sketsa/escape_tag_belajar.py` | auto-escape tag penutup di dalam `<script>` |
| `_sketsa/sketsa_uji_t{,2,3}.py` | 3 putaran sketsa (riwayat desain) |
| `_sketsa/sketsa_hack.py` | 3 variasi warna kartu HACK |
| `_sketsa/render_sketsa.py` | render sketsa + potong ruang putih otomatis |
| `uji_kartu_ujit.py` | **13 uji** halaman sungguhan di HP |

### ⏭️ BELUM DIKERJAKAN
> ✅ **Diperbarui 20Sep26** — 4 dari 5 sudah SELESAI, hanya tersisa 1.
> Daftar lama masih menulis keempatnya sebagai "belum" → sangat menyesatkan.

| # | Isi | Status |
|---|---|---|
| 1 | Format unduhan **SPSS** (nama panjang) / **PLS** (kode pendek) | ✅ **SELESAI** (Tahap 1.1) |
| 2 | Mode 1-model-1-jalur `/buat-data?model=…` | ✅ **SELESAI** (Tahap 1.2) |
| 3 | Halaman `/kuantitatif` + kartu model bergambar | ✅ **SELESAI** (Tahap 1.3, 14 kartu) |
| 4 | PERIKSA SYARAT (grafik SPSS + PLS) | ✅ **SELESAI** (Tahap 2.1, LIVE 20Sep26) |
| 5 | Lapis 2 (AI) untuk judul ragu | ⬜ **BELUM** — memang belum dikerjakan |

**Sisa proyek yang SEBENARNYA belum (lihat `TAHAP_PENYELESAIAN.md`):**

| # | Isi | Catatan |
|---|---|---|
| 2.2 | **Linearitas** — scatter X vs Y | bahan `titik.xy` **sudah ada** |
| 2.4 | **Khas PLS** — Outer Loading · AVE · Composite Reliability | bahan `konstruk[].muat/ave/cr` **sudah ada** |
| 2.5 | **Pemisah jelas mana SPSS, mana PLS** | tulisan, bukan mesin |
| 3 | **Klinik data sakit + kunci jawaban** | Tahap 3 |
| 4 | **Pemilih alat** (SPSS / SmartPLS) | Tahap 4 — tujuan utama Bos |
| 5 | **Ujian** (soal AI, individual/kelompok) | Tahap 5 |
| 6 | **Modul kualitatif** | Tahap 6 |
| 7 | **Login** | Tahap 7 — paling akhir |
| — | Lapis 2 (AI) untuk judul ragu | kecil, belum dijadwalkan |

### 💬 CATATAN DISKUSI (BUKAN tugas — jangan dikerjakan tanpa Bos buka lagi)
- 📝 **`CATATAN_DISKUSI_VALIDITAS_12_UJI.md`** — validitas & reliabilitas + peta 27 uji
  kuantitatif + usulan 12/13 uji inti + komponen input + 3 opsi tampilan.
  Arahan Bos 19Sep26: *"diskusi saja, kamu catat biasa saja, mungkin nanti setelah
  project bisa kita bahas lagi."* **JANGAN mulai koding dari berkas itu.**
- 🔒 **`RUANG_MANOVA.md`** (19Sep26) — **RUANG DIPESAN untuk MANOVA** + **bahasan gerbang
  model SELESAI (ditutup Bos 19Sep26)**. Perintah Bos: *"kamu perlu siapkan ruang untuk
  manova ini, agar tidak bertumpuk dan menimpa."* Isi: 4 ruang (R1 kelas CSS
  `.pintu.lebar-penuh` **sudah disiapkan**, R2 `?model=banding-kelompok`, R3
  `app/hitung/manova.py`, R4 kolom kelompok **DITAHAN**) · hasil cek mesin ·
  daftar 10 bagian yang perlu dibangun · MANOVA≠software · anak tangga sesudahnya ·
  **§8b–8d keputusan final** (β otomatis · range PROPORSIONAL · mode presisi/natural/
  `presisi_variasi`=campuran SEMUA SUDAH ADA · "math"=presisi) · bukti 14 jalur galat 0,0222.
  **BUKAN tugas — jangan dikoding tanpa Bos buka lagi.**
- 🧭 **`CATATAN_DISKUSI_GERBANG_MODEL_Y_GANDA.md`** (19Sep26) — gerbang model
  bertahap (4 kartu induk → sub-pilihan), istilah+terjemahan, **Y lebih dari satu**,
  **MANOVA belum ada** (bahan mentah lengkap), hasil ukur mesin Y ganda
  (2/3/4 keluaran, galat ≤0,0067). **DISKUSI, bukan tugas.**
- 🗺️ **`TAHAP_PENYELESAIAN.md`** — peta jalan 7 tahap penyelesaian proyek
  (disusun 19Sep26 atas permintaan Bos).
  **PETA JALAN, bukan keputusan** — Bos yang menentukan urutan & ACC.

---

## ✅ 18 Sep 2026 — AUDIT MESIN: 10 BENTUK MODEL TERBUKTI + 1 BUG BESAR DITUTUP

### 🎯 JAWABAN PERTANYAAN BOS: "mesin belum semua diimplementasikan ke UI web?"

**BENAR.** Mesin jauh lebih sakti dari pintunya:

| Lapisan | Kemampuan | Status |
|---|---|---|
| Mesin (`spek_pembangun.bangun_dari_spek`) | bentuk **APA PUN** (tak melingkar), interaksi di target mana pun | ✅ |
| Kalibrasi (`kalibrasi_jalur.kalibrasi_per_jalur`) | setel bobot sampai koefisien = yang diminta | ✅ termasuk interaksi |
| **Pintu web** (`buat_data.html`) | hanya **sederhana / berganda / keduanya** | ❌ **3 dari 10** |

**BUKTI TERUKUR** — `audit_mesin.py`, **10 LULUS / 0 GAGAL**:

| # | Bentuk model | Galat maks |
|---|---|---|
| 1 | Regresi sederhana | 0,0067 |
| 2 | Regresi berganda | 0,0026 |
| 3 | Mediasi tunggal | 0,0171 |
| 4 | Dual mediasi paralel | 0,0049 |
| 5 | Mediasi berjenjang | 0,0092 |
| 6 | Moderasi MRA | 0,0081 |
| 7 | Dual moderasi | 0,0130 |
| 8 | Moderated mediation | 0,0258 |
| 9 | Moderasi jalur-a | 0,0075 |
| 10 | Model 4 tingkat, 2 keluaran | 0,0044 |

### 🚨 BUG TERSEMBUNYI BERHARI-HARI — `item_per` dari NILAI BAWAAN

```
app/hitung/berurutan.py  :228   rl = dict(..., item_per=4)   ← BAWAAN
app/hitung/generator.py  :251   rl = dict(..., item_per=4)   ← SALINAN
app/hitung/struktural.py :210   rl = dict(..., item_per=4)   ← SALINAN
```

Kalau pemanggil memakai **`item_per=3`** → indeks acak naik ke **3** → kolom ke-4
tidak ada → `IndexError: index 3 is out of bounds for axis 1 with size 3`.

**Kenapa tersembunyi:** semua uji lama memakai `item_per=4` (bawaan). Akibatnya
**4 bentuk moderasi mustahil dibangun** dan **tidak ada yang tahu**.

**Ditutup di 3 berkas** — `item_per` sekarang **DIUKUR dari bentuk matriks item**,
dan pemilih variabel acak **hanya memilih variabel yang punya kolom selebar itu**.

**Pelajaran: JANGAN percaya nilai bawaan — UKUR dari data.**

### 🛠️ BERKAS BARU 18Sep26

| Berkas | Isi |
|---|---|
| `sot.py` | ⭐ **SOT — satu pintu informasi** (hitung dari kode, `--periksa`, `--json`) |
| `audit_mesin.py` | uji 10 bentuk model (jadi grup gerbang) |
| `periksa_halaman_sungguhan.py` | ukur halaman LIVE + suntik CSS + tanya CSSOM |
| `RANCANGAN_SEMUA_MODEL_DI_WEB.md` | rancangan membuka mediasi/moderasi di web |

### 📌 GERBANG UJI: 23 GRUP

Ditambah: **SOT** (urutan pertama) · **10 bentuk model** (`audit_mesin.py`).

---

## ✅ FASE 1 SELESAI — 17 Sep 2026 (16 LULUS / 0 GAGAL, EXIT 0)

**Kontainer `simulasi-olah-data` LIVE** di port **8120** (→ kontainer 8000),
`restart unless-stopped`, status **healthy**. Bridge default (cloudflared di host).
Image bertanda `-statlab`. Deploy **WAJIB** `bash jalankan.sh`.

### Yang sudah jadi

| Berkas | Isi |
|---|---|
| `Dockerfile` | python:3.13-slim + fastapi/uvicorn/jinja2/numpy/scipy/pandas/openpyxl/pyreadstat |
| `jalankan.sh` | gerbang uji → build image → ganti kontainer → verifikasi `/health` |
| `app/main.py` | FastAPI, 6 rute halaman + `/api/buat-data` + `/api/unduh` + `/api/ai` |
| `app/berkas_kerja.py` | jembatan web→mesin, ukur-ulang-sendiri, simpan CSV/XLSX |
| `app/templates/dasar.html` | kerangka + sprite ikon inline + nav |
| `app/templates/beranda.html` | 6 kartu modul, kartu BISA/BELUM, alur 5 langkah |
| `app/templates/belajar.html` | **kamus interaktif berslider — 6 istilah** |
| `app/templates/buat_data.html` | setelan 5 langkah + **pagar signifikansi hidup** |
| `app/templates/pengaturan.html` | saklar AI ON/OFF + info mesin |
| `app/templates/segera.html` | halaman "belum siap" per modul |
| `app/static/gaya.css` | tema **terang-warm** (kertas hangat, tinta coklat) |
| `app/static/lucide.svg` | **sprite 87 ikon** (dibangun `scripts/bangun_sprite_ikon.py`) |
| `uji_web_container.sh` + `uji_web_data.py` | uji E2E dari DALAM kontainer |

### Jebakan yang sudah kena (JANGAN ulang)

- ⚠️ **Uji unduhan HARUS buat data dulu** di proses yang sama — kalau tidak, 404
  dan itu **bukan bug aplikasi**.
- ⚠️ **`curl 127.0.0.1:8120` dari Wulan SELALU gagal** (loopback berbeda).
  Pakai **IP kontainer** (`docker inspect`) atau `docker exec`.
- ⚠️ **Proses uvicorn lokal bisa menahan port 8120** → cek `docker port` dulu.
- ⚠️ Heredoc Python di dalam `$( )` bikin sintaks rusak → tulis ke berkas.
- ⚠️ **FastAPI versi baru**: `TemplateResponse(request, nama, konteks)` — bentuk
  lama bikin **SEMUA halaman HTTP 500**. Akar dari **LOG SERVER**, bukan tebakan.
- ⚠️ **Halaman diuji lewat `file://`** → `/static/gaya.css` tidak termuat →
  `display:inline` **PALSU**. Suntik CSS-nya (lihat `periksa_halaman_sungguhan.py`).
- ⚠️ **Spesifisitas CSS menang atas urutan** — `.medan label` (0,1,1) mengalahkan
  `.pilih-cara` (0,1,0). Naikkan jadi `label.pilih-cara`.

---

## ⏭️ BERIKUTNYA — BUKA MEDIASI & MODERASI DI WEB

Rancangan lengkap: **`RANCANGAN_SEMUA_MODEL_DI_WEB.md`**

Ringkas:
1. **Tangga 1** — 4 kartu awam: *Langsung · Lewat perantara · Ada yang
   menguatkan/melemahkan · Keduanya* (bukan 8 istilah teknis).
2. **Tangga 2** — begitu bentuk dipilih, **baris M / Z muncul otomatis** di tabel.
3. **Tombol "+ perantara" / "+ penguat"** → membuka **dual mediasi paralel**,
   **berjenjang**, **dual moderasi**, **moderated mediation** sekaligus.
4. **Tangga 3** — halaman hasil: tambah **a×b** (pengaruh tak langsung) +
   label **"mediasi penuh/sebagian"** + **grafik 2 garis** untuk moderasi.

**⚠️ 6 CELAH BELUM TERPECAHKAN** (jujur, jangan disembunyikan):
1. Bentuk tabel **a×b** & kalimat "mediasi penuh/sebagian" — belum dirancang.
2. Ambang **"a×b wajar"** — tidak ada baku seperti R².
3. **Grafik moderasi 2 garis** — belum dirancang.
4. **Mediasi berjenjang** — tabelnya lebih panjang.
5. Moderasi kalau **X cuma 1** — Z muncul kolom baru?
6. **Uji lewat web** belum ada (baru uji mesin).

**❓ MENUNGGU KEPUTUSAN BOS:** (a) tangga 4 kartu vs 8 pilihan · (b) mulai dari
mediasi tunggal atau langsung mediasi+moderasi · (c) diksi awam · (d) grafik
moderasi di Fase 1 atau nanti.

---

## 📋 RENCANA FASE (ACC Bos)

| Fase | Isi | Status |
|---|---|---|
| **1** | Kerangka + beranda + BELAJAR + BUAT DATA 3X+1Y | ✅ **SELESAI** |
| **2** | Mediasi/moderasi + uji jalur + 3 mode | ⏭️ berikutnya (rancangan siap) |
| **3** | ⭐ KLINIK data sakit + **KLINIK DATA LAPANGAN** (upload `.sav`/`.csv`/`.xlsx`/`.por`) + Klinik Hasil + kunci jawaban | di-ACC |
| **4** | UJIAN (individual/kelompok) | |
| **5** | PEMILIH ALAT (SPSS vs PLS) | |
| **6** | Login + tombol AI ON/OFF | |
| **7** | Modul Kualitatif | |
| — | Domain `statistik.bikinaja.id` | ✅ **LIVE** |

## 📌 KEPUTUSAN TERKUNCI

- **3 MODE OUTPUT** (ACC Bos): 🎯 Presisi · 🌿 Natural · ⚖️ Presisi-p-variasi ✅
- **Pagar signifikansi** dihitung dari **β DAN jumlah responden** ✅
- **Tombol "Saya mau hasilnya X"** ✅
- **File SPSS .sav + CSV/XLSX WAJIB didukung** ✅ (`pyreadstat`)
- **File proyek SmartPLS `.splsm` TIDAK bisa** — tapi **ekspor hasil .xlsx BISA**
- **Opsi 1 (ACC 18Sep26)**: **jumlah X ≠ jenis analisis** — 3 X boleh **3 regresi
  sederhana terpisah** atau **1 regresi berganda**; halaman hasil bisa **2 tabel**
- **Diksi (ACC 18Sep26)**: **"Konsistensi jawaban"** (bukan "keandalan") · **R²**
  diperbesar+dipertebal + *"seberapa besar X menerangkan Y"* · **"Prediksi"**
  (BUKAN "ramalan") · larangan kata *"pagar"* & *"geser nilainya"* di UI user
- Tema **terang-warm**, ikon **sprite SVG** (bukan emoji), bahasa **Indonesia akademik**
- **Data simulasi WAJIB dilabeli** di setiap keluaran
