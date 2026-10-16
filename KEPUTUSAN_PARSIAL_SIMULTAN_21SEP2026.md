# 📐 KEPUTUSAN: SEDERHANA = PARSIAL · BERGANDA = PARSIAL + SIMULTAN

**Tanggal:** 21 September 2026
**Status:** ✅ ACC BOS — dikerjakan bertahap, **SELESAI & TERBUKTI (gerbang 60 grup LULUS)** saat berkas ini ditulis
**Keputusan nomor:** N1 + R1 + P1 (lihat §4) · **+ Opsi B aturan jawaban kosong (lihat §8)**

---

## §1. LATAR — KENAPA BERKAS INI ADA

Bos menanyakan **kenapa kartu "Berganda-berantai" terasa aneh** dan **kenapa tidak
ada parsial**. Dari pertanyaan itu, akar sebenarnya terbuka:

> **ARAH BOS (verbatim, 21Sep26):**
> *"Sebenarnya berantai itu tidak ada, karena saat itu saya kebingungan nyari
> parsialnya kok ga ada, maka saya ciptakan berantai."*

⇒ **"Berantai" lahir dari KEKEBINGUNGAN, bukan dari kebutuhan keilmuan.**
Yang Bos cari sejak awal = **PARSIAL** — dan parsial itu sudah ada di mesin,
hanya **tidak pernah ditampilkan** ke user.

---

## §2. KOREKSI KEILMUAN (WAJIB DIBACA SEBELUM MENGUBAH APA PUN)

Bos menanyakan arti **regresi linear berganda**, **parsial**, dan **simultan**.
Jawaban yang dipakai di proyek ini:

| Istilah | Arti | Uji |
|---|---|---|
| **Parsial** | tiap X diuji **sendiri-sendiri** ke Y. X lain **dibuang**. | **Uji t** |
| **Simultan** | **semua** X masuk **satu rumus sekaligus**. Tidak ada yang dibuang. | **Uji F** |
| **Regresi linear sederhana** | **1 X** → Y | uji t |
| **Regresi linear berganda** | **banyak X → Y, SIMULTAN** | uji F + uji t |

⚠️ **PENTING:** "Regresi linear berganda" dalam statistik baku = **SIMULTAN**.
Kalau banyak X tapi dihitung satu-satu, itu **BUKAN** regresi berganda — itu
**beberapa regresi sederhana** (parsial).

⚠️ **Parsial & simultan BUKAN dua jenis regresi.** Keduanya lahir dari **SATU**
regresi berganda: **uji t** menghasilkan parsial, **uji F** menghasilkan simultan.
(Konfirmasi Bos dari sumber luar, 21Sep26 — kata kunci: "Pengujian ini menggunakan
Uji F" / "Uji t".)

---

## §3. KEADAAN MESIN SEBELUM KEPUTUSAN INI (TERUKUR, bukan dugaan)

Diukur langsung dari `app/berkas_kerja.py` (21Sep26):

| Kartu | Yang DIHITUNG mesin | Yang DITAMPILKAN |
|---|---|---|
| Sederhana | `terpisah` (parsial, 1 X) | parsial |
| Berganda | `terpisah` + `bersama` | **hanya `bersama` (simultan)** |
| Berganda-berantai | `terpisah` + `bersama` + `rantai` | `bersama` + `rantai` |

⇒ **Parsial SUDAH DIHITUNG di Berganda & Berantai, tapi TIDAK DITAMPILKAN.**
Itu akar kebingungan Bos.

### Uji F — BELUM ADA

Hasil grep seluruh `app/`: kata `uji_f`, `F_hitung`, `anova`, `f_stat` = **KOSONG**.
Yang ada hanya **R²** (`app/berkas_kerja.py` baris 73).
⇒ Mesin bisa bilang *"45% keragaman dijelaskan"*, tapi **tidak bisa** bilang
*"semua X secara simultan berpengaruh"* (p-value uji F).

### Hasil UKUR NYATA — Berganda vs Berantai BEDA (21Sep26)

`_sketsa/` — 3 X, β 0,30/0,25/0,20, n=200, seed=777:

| | Berganda | Berantai |
|---|---|---|
| Harga → Y (simultan) | 0,2970 | 0,2933 |
| Harga → Y (parsial) | 0,3971 | 0,5118 |
| R² | 0,2543 | 0,3680 |
| Rantai antar-X | — | Harga↔Promosi 0,55 |

⇒ Hasilnya **BEDA** — jadi "berantai" bukan duplikat Berganda. Tapi keberadaannya
**tidak diperlukan** untuk menjawab kebutuhan Bos (parsial).

---

## §4. KEPUTUSAN BOS (21Sep26)

### Struktur kartu — **N1**

| Kartu | Isi | Gambar |
|---|---|---|
| **① Sederhana** | banyak X → Y, **PARSIAL saja** (X1→Y, X2→Y, … X8→Y) | panah lurus, **TANPA** panah sudut |
| **② Berganda** | **PARSIAL + SIMULTAN** (dua-duanya lengkap) | panah lurus **+** panah sudut ke Y (gambar "berantai" sekarang) |

Nama resmi di kartu: **"Parsial"** & **"Berganda (Parsial + Simultan)"**.
Kata "Sederhana" tetap dipakai sebagai **keterangan** kalau X = 1.

### Nasib "Berantai" — **R1 (ARSIPKAN)**

- Kode `cara='berantai'` **TETAP ADA di mesin** — **DILARANG DIHAPUS**
- Hanya **tidak ditampilkan** di pintu (`/buat-data` & `/kuantitatif`)
- Uji lama (`gerbang_s3.py` dkk) **tetap sah** — mesin berantai masih utuh
- Alasannya: sesuai aturan Bos **"jangan ubah yang tidak salah"** + risiko nol
  pembongkaran. Kalau Bos berubah pikiran → tinggal munculkan lagi kartunya.

### Cara hitung — **P1 (NOL PERUBAHAN MESIN)**

Kartu ① tetap memakai `cara='sederhana'` yang **sudah ada**. Kalau user pilih
3 X, mesin otomatis menjalankan 3 uji parsial. **Tidak ada cabang kode baru.**

---

## §5. RISIKO YANG SUDAH DISEBUT KE BOS

| Risiko | Penanganan |
|---|---|
| Nama "Regresi Berganda" = taruhan besar | Kartu ② **tetap** memakai kata "Berganda" + keterangan "(Parsial + Simultan)" |
| Kode lama jadi mati | `berantai` **diarsipkan**, bukan dihapus → bisa dihidupkan lagi |
| Uji & dokumen lama goyah | `gerbang_s3.py` (33 uji) tetap **sah** — tidak ada yang dihapus |
| Gerbang 33 grup bisa rusak | Pintu tidak disentuh gerbang → **mesin tidak diubah** |

---

## §6. URUTAN KERJA (bertahap — tiap langkah DIUKUR dulu)

| # | Langkah | Bukti yang wajib ada |
|---|---|---|
| **1** | **CATAT** keputusan ini ke dokumen + memory + SOT | `sot.py --periksa` EXIT 0 |
| **2** | **UJI F + tabel ANOVA** — murni MENAMBAH fungsi | gerbang baru: uji F **terbukti BISA GAGAL** |
| **3** | **PINTU**: kartu ① = Sederhana(Parsial) · kartu ② = Berganda(Parsial+Simultan) · kartu berantai disembunyikan · **tabel parsial ditampilkan** | gerbang lama tetap **EXIT 0** |

⏸️ **Tiap langkah BERHENTI dan LAPOR ke Bos** — tidak menembak terus.

---

## §7. YANG BELUM DIPUTUSKAN (jangan dikerjakan diam-diam)

1. Uji t & F untuk **model mediasi & moderasi** — Bos sudah setuju arahnya
   (jawaban: **BISA**, sebab semua model disusun dari regresi), tapi
   **dikerjakan SETELAH** regresi beres. Mediasi punya **2 persamaan** →
   perlu **2 set** tabel, tidak boleh satu tabel saja.
2. Nama teknis `cara` di kode: tetap `'sederhana'` (P1) — **jangan** bikin
   `'parsial'` baru.
3. Nasib berkas `RANCANGAN_SEMUA_MODEL_DI_WEB.md` & `RUANG_MANOVA.md` yang
   menyebut "berantai" — belum dibersihkan, **menunggu putusan Bos**.

---

## §7. KEPUTUSAN BARU (21Sep26) — TOMBOL "HASIL" + TOKEN PEMBIMBING

**Status:** 🟡 DISKUSI SELESAI, BELUM DIKODING (rencana saja)

### Latar
Kunci jawaban diperlukan pengajar untuk mencocokkan hasil olah data mahasiswa.
Tapi kunci **tidak boleh terbuka bebas** — kalau mahasiswa melihatnya, latihan
jadi batal (tinggal menyalin, tidak lagi mengolah).

### Putusan Bos (VERBATIM — JANGAN diubah tanpa ACC)
1. Tombolnya bertulis **"Hasil"** — **DILARANG** memakai kata **"Jawaban"**.
   Alasan: kata "jawaban" membocorkan bahwa ada yang bisa diintip.
2. Sebutan pengguna = **"pembimbing"** — **DILARANG** memakai kata **"dosen"**.
3. Cara kerja: tombol **"Hasil"** diklik → muncul **1 kotak token** → pembimbing
   isi token → kunci terbuka, dan pembimbing yang menentukan kapan mahasiswa
   boleh mencocokkan.

### Rencana teknis (belum dikoding)
| # | Hal | Putusan/Usulan |
|---|---|---|
| 1 | Tempat token | **`.env`** (mis. `TOKEN_KUNCI`). ⛔ DILARANG ditulis di kode, dokumen, skill, atau memory |
| 2 | Rute | `/api/kunci` — kunci **hanya dikirim bila token cocok** |
| 3 | Bentuk | Tombol "Hasil" + 1 kotak isian di halaman hasil |
| 4 | Uji wajib | **tanpa token → DITOLAK** (uji harus terbukti BISA GAGAL) |
| 5 | Mode Natural | kunci diberi tanda jujur: **"β terbaca ≠ setelan"** (memang begitu mode Natural) |

### Kalimat layar (nada HANGAT, tidak menuduh — aturan Bos)
- Sebelum token: 🔒 *"Hasil hanya untuk pembimbing. Masukkan token dari pembimbing kamu."*
- Sesudah benar: ✅ *"Hasil terbuka. Cocokkan jawabanmu — tanyakan ke pembimbing kalau ada yang beda."*

### ⚠️ BATAS JUJUR (jangan dijanjikan lebih)
Selama kunci **dikirim ke browser**, dia **ada di browser**. Mahasiswa yang paham
teknis bisa menangkapnya lewat Inspect Element **setelah token benar**. Yang bisa
dijamin: kunci **TIDAK PERNAH dikirim** bila token salah. **JANGAN bilang "aman"
kalau bukan.**

### ⛔ CELAH BELUM TERPECAHKAN (jujur)
Kalau tokennya **satu untuk semua**, pembimbing A bisa melihat latihan pembimbing
B. Belum ada putusan untuk ini.

### 📌 BAHAN KUNCI — SUDAH ADA DI MESIN (terukur 21Sep26)
Tidak perlu mesin baru; cukup dirangkum:
- `bersama[]` → `diminta`, `terbaca`, `t`, `p`, `r2` (uji t / PARSIAL)
- `f` → `ss_regresi`, `ss_residu`, `ss_total`, `df_*`, `ms_*`, `F`, `p` (ANOVA / SIMULTAN)
- `f_terpisah[]` → uji F per-X (padanan SPSS)
- `r2`, `r2_terpisah`, `ranta_setel`, `galat_maks`, `mode_label`

### ⛔ BELUM MENCAKUP (jujur)
Hanya **regresi** (parsial + simultan). **Mediasi & moderasi** belum punya uji
t/F per jalur dalam bentuk siap-saji — pekerjaan lanjutan.

---

## §7. KEPUTUSAN BARU (21Sep26) — IDENTIFIKASI DATA di `/klinik`

**Status:** ✅ **ACC BOS (21Sep26)** — DISKUSI SELESAI, BELUM DIKODING

### Latar (ARAH BOS verbatim)
> *"Ini masalah identifikasi data. Karena harus ada yang menjelaskan ini data apa
> yang di upload mhs. Mesin harus tau agar tidak salah analisa dan hitungan.
> Serta tidak salah memberikan rekomendasi juga."*

Akar: berkas data cuma ANGKA — tidak ada keterangan mana X, mana M, mana Y.
⇒ Mesin & mahasiswa TIDAK satu bahasa.

### Putusan Bos (VERBATIM — JANGAN diubah tanpa ACC)

**① MAHASISWA yang menandai peran setiap kolom.**
> *"Yang paling baik, mahasiswa identifikasi kolom ini X1 kolom ini X2 dst.
> Kolom ini M1, kolom ini M2 dst.. begitu juga Z dan Y, Y1, Y2 dst."*
+ *"Klik klik saja."* → **DROPDOWN per kolom**, bukan mengetik.

**② VERIFIKASI dulu, baru PROSES.**
> *"Sebelum proses tampilkan kondisi yang telah di parsing benar atau tidak?
> Kalau tidak minta beberapa hal untuk mhs verifikasi."*
+ *"Lebih bagus lagi kalo kesalahan itu terdeteksi script dan suruh ulang yg benar"*

**③ Kalau ada >1 M atau >1 Z → TANYA paralel / berjenjang** (1 pertanyaan).

**④ Urutan kerja:** dropdown peran DULU → mesin hitung per-konstruk menyusul.

**⑤ Bentuk kolom banyak → OPSI A (ACC Bos 21Sep26): SEMUA kolom ditampilkan, di-SCROLL.**
Jangan dikelompokkan otomatis, jangan dipotong 10. Alasan: supaya **tidak ada
kolom yang terlewat** — itu masalah utama yang mau diselesaikan.
(Ditolak: B=kelompok otomatis dari nama; C=10 dulu + tombol lihat semua.)

**⑥ Langkah 3 lama "Tunjuk kolomnya" → DIGANTI bentuk peran (OPSI A, ACC Bos 21Sep26).**
JANGAN ditambah jadi langkah baru (mahasiswa akan menunjuk 2× = bingung).
Alasan: Bos mau **satu bahasa** — kalau ada 2 cara menunjuk, justru tidak seragam.
⚠️ RISIKO yang diakui: `/klinik` sudah LIVE & punya uji web → **WAJIB jalankan
gerbang penuh** setelah diubah, jangan sampai memecahkan uji lama.

**⑦ SELESAI DIKODING 21Sep26 — bukti:**
- `periksa_peran()` di `app/diagnosis.py` — **34 LULUS / 0 GAGAL** (uji_peran_kolom.py)
- Rute `POST /api/diagnosis/periksa-peran` (main.py) — **30 LULUS / 0 GAGAL**
  (uji_peran_web.py, HTTP sungguhan + 8 pagar)
- Alur halaman penuh: unggah → peran → "Cek dulu" → "Periksa sekarang"
  — **20 LULUS / 0 GAGAL** (uji_peran_alur.py, Chrome CDP sungguhan)
- **TERBUKTI BISA GAGAL:** kembalikan `baris-x` yatim → 2 / 10 / 8 uji menangkap, EXIT 1
- Mesin hitung **TIDAK diubah** — `periksa()` menerjemahkan peran (X1/M1/Y1) →
  `kolom_x/kolom_y/kolom_m` yang sudah jalan.

**🔴 AKAR YANG DITEMUKAN (penting — jangan diulang):**
Waktu mengganti langkah 3, Wulan menghapus `<div id="baris-x">` & `<div id="baris-m">`
dari HTML, **tapi lupa kode JS yang memanggilnya**. Akibatnya `null.innerHTML`
→ galat SENYAP → **seluruh jalur "setelah unggah" MATI**, dan `catch` melaporkannya
sebagai *"Koneksi ke server terputus"* — **pesan MENYESATKAN** (server hidup).
Aturan: **elemen dihapus → WAJIB cari & buang SEMUA JS yang menunjuknya.**
Bukti: `grep baris-x` harus 0. Cara ketemu: uji "apa adanya" (unggah sungguhan),
bukan menyuntik kolom tiruan — suntikan Wulan **menyembunyikan** cacat ini.

**⑧ Cacat tampilan yang ditemukan VISION & diperbaiki:**
① nama kolom lebar **0px** (tidak kelihatan) → flex salah → kini **125px**;
② ringkasan **dobel** (ditulis di 2 tempat) → kini **sekali**;
③ istilah beda: mesin bilang "bebas (X)", halaman bilang "penyebab (X)" → diselaraskan.
⚠️ Sisa yang **bukan cacat kode**: teks `<option>` panjang terpotong di dropdown
sempit (bawaan browser) — teks di sumber LENGKAP.

**🛠️ PRASARANA ≠ MESIN — KODE LEWAT 77 (ACC Bos 21Sep26, Opsi A) — SELESAI:**
Chrome CDP mati dulu dilaporkan "7 GRUP GAGAL" → Wulan mengejar bug yang tidak ada.
Perbaikan akar: `prasarana_uji.py` BARU (`pastikan_chrome()` → None/77) +
`KODE_LEWAT = 77` di `gerbang_uji.py` (rc 77 = ⏭️ LEWAT prasarana, bukan GAGAL) +
6 berkas uji browser disambungkan.
Bukti 2 arah: Chrome MATI → gerbang **EXIT 0** "38 grup · 6 lewat karena prasarana" ✅ ·
GAGAL asli disuntik → gerbang **EXIT 1** "1 GRUP GAGAL" ✅.
🚨 **Chrome TIDAK BISA dilepas dari gateway** — terukur 4 cara, semua gagal
(`Popen` biasa · `start_new_session` · double-fork · double-fork+setsid → dbus).
PPID 160 = SYARAT HIDUP. JANGAN bikin watchdog cron (cron ≠ anak Hermes → gagal).

**⏭️ LANJUT (Opsi A, ACC Bos): MESIN HITUNG PER-KONSTRUK** — gabung beberapa kolom
peran sama (X1 = 3 kolom) jadi SATU skor sebelum dihitung. `/klinik` sekarang masih
hitung PER KOLOM.

**⑨ BELUM (jujur):** mesin hitung **per-konstruk** (gabung 3 kolom X1 jadi 1 skor)
belum ada — `/klinik` masih hitung per kolom. Deploy belum di-ACC.

**🔴 AKAR KE-2 — 7 GRUP GERBANG GAGAL PALSU (21Sep26, terukur, BUKAN bug app):**
Gejala: 7 grup gagal berurutan, semuanya grup **berbrowser**; 31 grup lain lolos.
Diukur: `curl 127.0.0.1:9333/json/version` → **000 (MATI)**; `curl :8122` → **200 (hidup)**.
Galat asli: `ConnectionRefusedError [Errno 111]` — **BUKAN** salah port, **BUKAN** kode app.
Sebab: **Chrome CDP :9333 mati** (Wulan hanya menyalakan server uji :8122).
Bukti pulih: `uji_sub_regresi` 45/0 · `uji_normalitas` 57/0 · `uji_web_grafik` EXIT 0.
⇒ **ATURAN: sebelum gerbang, pastikan CDP :9333 HIDUP** (`curl :9333/json/version`).
   Gerbang TIDAK menyalakan Chrome sendiri (Popen gagal dbus) — nyalakan dulu,
   lewat terminal background, **JANGAN pkill**.
   Kalau ada 7 grup browser gagal beruntun & sisanya lolos → **curigai CDP mati dulu**,
   jangan curigai kode. (Ini pola yang sama seperti "tab yatim": prasarana, bukan app.)

**✅ Uji ke-13 BARU (penjaga permanen):** `uji_peran_kolom.py` §13 memeriksa
**tidak ada tag penutup mentah di dalam string JS** (mis. `'</div>'`) — harus `'<\/div>'`.
Bukti bergigi: kembalikan 1 tag mentah → **1 GAGAL, EXIT 1**; dipulihkan → **35/0 EXIT 0**.

### ⚠️ ISTILAH WAJIB (jangan dilanggar)
- Kata **"pembimbing"** — **DILARANG** "dosen".
- Kata **"Hasil"** — **DILARANG** "jawaban".
- Tombol token/kunci: **DIBATALKAN** untuk fitur ini — sebab ini **LATIHAN**,
  mahasiswa memang harus bisa lihat. Bos: *"Kan bukan ujian ini?"*

### 🔒 BEBERAPA HAL YANG DIBATALKAN (jangan dihidupkan lagi tanpa ACC)
| Dibuat Wulan | Status |
|---|---|
| Kode ujian (`A7K2`) | ❌ BUANG |
| Token pembimbing | ❌ BUANG |
| Database ujian | ❌ BUANG |
| Modul UJIAN penuh (Tahap 5) | ⏸️ **beda hal** — TIDAK dibatalkan, tapi BUKAN ini |
| Sheet 3/4/5 | ❌ BUANG (khayalan Wulan, Bos sendiri bilang "saya hanya berkhayal") |

### 📋 ALUR yang disetujui
```
1. Mahasiswa unggah berkas (csv / xlsx / sav) — boleh data SENDIRI
2. Mesin baca kolomnya → tampilkan SEMUA kolom
3. Mahasiswa beri peran via DROPDOWN: [X1][X2][M1][M2][Z1][Y1][Y2]
4. MESIN CEK SENDIRI → ada janggal? protes, minta perbaiki
   (kolom belum ditandai · dobel peran · tidak ada Y · nomor melompat)
5. Kalau >1 M / >1 Z → tanya SEKALI: paralel atau berjenjang?
6. BARU proses: periksa syarat + hitung
7. Hasil (terbuka untuk mahasiswa)
```

### 🛑 KENAPA **BUKAN** AI / AGEN (putusan Wulan, sudah disetujui arah)
- `/klinik` murni **hitungan lokal tanpa AI** (janji desain awal) — jangan diubah.
- AI = berbiaya + bisa mati (tombol ON/OFF) + **tidak bisa dipertanggungjawabkan**.
- Parsing itu **jawaban PASTI** → pakai aturan tetap; AI hanya untuk yang TIDAK pasti.

### ⚠️ BATAS JUJUR (jujur — jangan dijanjikan lebih)
1. **Mesin hitung per-konstruk BELUM ada di `/klinik`.** Sekarang `/klinik`
   hitung **per kolom**. Kalau 3 kolom ditandai `X1`, mesin harus **gabung jadi
   1 skor** dulu (seperti `Compute Variable` di SPSS) — **belum diuji ada/tidak**.
2. **`/klinik` belum tahu model** — terukur: `pred = kolom_x + kolom_m` (baris 202
   `app/diagnosis.py`). M cuma digabung jadi prediktor, **tidak diperlakukan
   sebagai perantara**.
3. **`.csv` tidak bisa multi-sheet** → kalau nanti perlu kartu, format ini
   butuh cara lain. **Belum terpecahkan.**
4. **"Seharusnya berapa"** (`β` asli) belum sampai ke `/klinik` — inilah kenapa
   bagian "banding hitungan" belum bisa jalan.

### 📌 BAHAN YANG SUDAH ADA DI MESIN (terukur 21Sep26)
- `baca_berkas()` — bisa `.csv` `.xlsx`/`.xls` `.sav` (+label SPSS). ✅
- `periksa_spss(df, kolom_x, kolom_y, kolom_m)` — terima M ✅
- `periksa_pls(df, konstruk, kolom_y_konstruk)` — `konstruk` = dict nama→item ✅
- Mesin bangun data 13 bentuk ✅ · Y ganda ✅ · 14 jalur ✅ (galat 0,0222)

---

## §8. KEPUTUSAN BARU (21Sep26, kedua) — ATURAN JAWABAN KOSONG = **OPSI B**

**Konteks:** saat menyambung **SKOR KONSTRUK** (`X1` = 3 kolom → 1 skor,
ACC Bos pada sesi yang sama), muncul pertanyaan statistik: *kalau mahasiswa
mengosongkan sebagian item, skornya berapa?* Wulan **berhenti dan bertanya** —
ini keputusan metodologi, bukan teknis.

### 3 opsi yang disodorkan (semua + akibatnya)

| # | Aturan | Akibat |
|---|---|---|
| A | ada 1 kosong → skor KOSONG | responden yang cuma kurang 1 item **dibuang** dari analisis |
| **B** ⭐ | `rata-rata item terjawab × jumlah item seluruhnya` | responden tetap ikut, skala sama dengan yang lengkap → **adil** |
| C | SPSS `SUM` melompati kosong | **BAHAYA:** jawab 1 dari 2 → skor 2,0 **seolah lengkap** (skor terlalu kecil yang kelihatan sah) |

### ✅ PUTUSAN BOS: **OPSI B**

    X1 = 3 item · dijawab 2 (skor 4 dan 5) → (4+5)/2 × 3 = 13,5
    Semua item kosong → skor KOSONG (NaN), BUKAN 0

**Alasan:** mahasiswa memakai kuesioner lapangan (bukan eksperimen terkendali);
responden yang kosong 1-2 item itu biasa dan **sayang dibuang**. Opsi C ditolak
karena menghasilkan skor yang **kelihatan sah padahal terlalu kecil** — jebakan
klasik yang membuat hasil analisis salah tanpa ada yang sadar.

### Implementasi (satu tempat, jangan ditulis dua kali)
`app/diagnosis.py::skor_konstruk(df, peran)`:
```python
dijawab = angka.sum(axis=1, min_count=1)      # NaN kalau SEMUA kosong
jml_dijawab = angka.notna().sum(axis=1)
skor[nama] = (dijawab / jml_dijawab) * len(ada)
```
**BUKTI:** `uji_skor_konstruk.py` **35/0** — *terbukti bisa gagal*: aturan
dikembalikan ke cara SPSS (`sum` biasa) → **7 uji menangkap** ("dapat 2.0,
harusnya 4.0").

---

## §9. CARA BALIK

Bos bilang **"lanjut statistik"** → baca `FLAG_LANJUT_DISINI.md` blok teratas
(berkas ini tertaut di sana) → `.venv/bin/python sot.py` → `bash gerbang_uji.sh`.
