# 🗺️ RANCANGAN: SEMUA KOMBINASI MODEL DI WEB

**Dibuat:** 18 Sep 2026 · **Dasar:** AUDIT MESIN TERUKUR (`audit_mesin.py`) — 10 LULUS / 0 GAGAL
**Status:** RANCANGAN (belum dikoding) · **Menunggu keputusan Bos**

---

## 1. JAWABAN PERTANYAAN BOS

> *"Jadi script/mesin kamu termasuk, belum semua diimplementasikan ke UI web?"*

**BENAR.** Mesin jauh lebih sakti daripada pintunya. Berikut keadaan terukurnya:

| Lapisan | Kemampuan | Status |
|---|---|---|
| **Mesin hitung** (`bangun_dari_spek`) | Bentuk model **apa pun** (tak melingkar), interaksi di target mana pun | ✅ **10/10 LULUS** |
| **Kalibrasi** (`kalibrasi_per_jalur`) | Menyetel bobot sampai koefisien **= yang diminta** (toleransi 0,02) | ✅ termasuk interaksi |
| **Pintu web** (`buat_data.html`) | Hanya **sederhana / berganda** | ❌ **3 dari 8 bentuk** |
| **Halaman hasil** | Hanya tabel β + R² | ❌ belum bisa baca a↳b mediasi |

**Terukur 18Sep26 (galat maksimum tiap bentuk):**

| # | Bentuk model | Galat maks | Status |
|---|---|---|---|
| 1 | Regresi sederhana | 0,0067 | ✅ |
| 2 | Regresi berganda | 0,0026 | ✅ |
| 3 | Mediasi tunggal | 0,0171 | ✅ |
| 4 | Dual mediasi **paralel** | 0,0049 | ✅ |
| 5 | Mediasi **berjenjang** | 0,0092 | ✅ |
| 6 | Moderasi **MRA** | 0,0081 | ✅ |
| 7 | **Dual** moderasi | 0,0130 | ✅ |
| 8 | **Moderated** mediation | 0,0258 | ✅ |
| 9 | Moderasi di **jalur-a** | 0,0075 | ✅ |
| 10 | Model 4 tingkat, 2 keluaran | 0,0044 | ✅ |

---

## 2. 🔴 CACAT MESIN YANG DITEMUKAN AUDIT INI (sudah diperbaiki)

**Bug tersembunyi berhari-hari** — semua uji lama memakai `item_per=4` (bawaan),
sehingga tidak pernah kena:

```
app/hitung/berurutan.py  :228   rl = dict(..., item_per=4)   ← BAWAAN 4
app/hitung/generator.py  :251   rl = dict(..., item_per=4)   ← SALINAN
app/hitung/struktural.py :210   rl = dict(..., item_per=4)   ← SALINAN
```

Kalau pemanggil memakai **`item_per=3`** → indeks acak naik sampai **3** →
kolom ke-4 tidak ada → `IndexError: index 3 is out of bounds for axis 1 with size 3`.

**PERBAIKAN:** `item_per` **DIUKUR dari bentuk matriks item**, bukan dari nilai
bawaan. Sudah ditutup di **3 berkas**. Setelah perbaikan: **moderasi 4/4 LULUS**
(sebelumnya 0/4).

**Pelajaran:** **jangan percaya nilai bawaan; ukur dari data.**

---

## 3. BENTUK MODEL YANG HARUS MASUK WEB

Mesin menerima **`jalur` + `interaksi`**. Semua bentuk di bawah ini hanya
**variasi isi dua daftar itu**:

### Kelompok A — Sudah ada di web ✅

| Bentuk | `jalur` | `interaksi` |
|---|---|---|
| A1. Sederhana | `[{Y: {X1: β}}]` × N (N uji terpisah) | — |
| A2. Berganda | `[{Y: {X1: β1, X2: β2, ...}}]` | — |

### Kelompok B — BELUM ada (mediasi)

| Bentuk | `jalur` | `interaksi` |
|---|---|---|
| **B1. Mediasi tunggal** | `[{M: {X: a}}, {Y: {X: c′, M: b}}]` | — |
| **B2. Dual mediasi paralel** | `[{M1: {X: a1}}, {M2: {X: a2}}, {Y: {X: c′, M1: b1, M2: b2}}]` | — |
| **B3. Mediasi berjenjang** | `[{M1: {X: a1}}, {M2: {M1: d}}, {Y: {X: c′, M2: b2}}]` | — |

### Kelompok C — BELUM ada (moderasi)

| Bentuk | `jalur` | `interaksi` |
|---|---|---|
| **C1. Moderasi MRA** | `[{Y: {X: bx, Z: bz}}]` | `[{Y, X, Z, b_int}]` |
| **C2. Dual moderasi** | `[{Y: {X, Z1, Z2}}]` | `[{Y,X,Z1,i1}, {Y,X,Z2,i2}]` |
| **C3. Moderasi jalur-a** | `[{M: {X, Z}}, {Y: {X: c′, M: b}}]` | `[{M, X, Z, i}]` |

### Kelompok D — BELUM ada (gabungan)

| Bentuk | `jalur` | `interaksi` |
|---|---|---|
| **D1. Moderated mediation** | `[{M:{X:a}}, {Y:{X:c′, M:b, Z:0}}]` | `[{Y, M, Z, i}]` |
| **D2. Model bertingkat** | berapa pun target, urut induk→anak | berapa pun |

**⇨ Kesimpulan: mesin sudah menerima SEMUA ini. Yang kurang = cara user MEMILIH.**

---

## 4. USULAN UI — TANGGA (bukan langsung semua)

**Prinsip (arahan Bos):** SIMPLE & MUDAH DIMENGERTI. Jangan tampilkan 8 pilihan
sekaligus — bikin bingung.

### 🪜 TANGGA 1 — "BENTUK HUBUNGAN" (paling sederhana)

Satu pertanyaan awam, **4 kartu** (bukan 8):

```
BAGAIMANA X BERHUBUNGAN DENGAN Y?
┌────────────────────┬────────────────────┐
│ ✓ Langsung         │   Lewat perantara  │
│   X → Y            │   X → M → Y        │
├────────────────────┼────────────────────┤
│   Ada yang         │   Keduanya         │
│   menguatkan/      │   (perantara +     │
│   melemahkan       │   penguat)         │
└────────────────────┴────────────────────┘
```

**Kenapa 4 kartu saja:** bentuk B2/B3/C2/C3/D2 = **variasi dari 4 ini**
(ditentukan oleh **berapa M** dan **berapa Z** yang user isi).

### 🪜 TANGGA 2 — VARIABEL MUNCUL OTOMATIS

Begitu bentuk dipilih, **tabel berubah sendiri**:

| Bentuk | Tabel yang muncul |
|---|---|
| **Langsung** | X1…Xn → Y |
| **Lewat perantara** | Tambah **baris M** + kolom **"pengaruh X ke M"** dan **"pengaruh M ke Y"** |
| **Ada penguat** | Tambah **baris Z** + kolom **"pengaruh X×Z"** |
| **Keduanya** | Tambah **M** dan **Z** + kolom interaksi |

**Tombol "+ perantara" / "+ penguat"** → user bisa tambah M2, Z2 sendiri
(→ otomatis jadi **dual mediasi paralel** / **dual moderasi**).

### 🪜 TANGGA 3 — HALAMAN HASIL MENYESUAIKAN

| Bentuk | Isi halaman hasil |
|---|---|
| Langsung | Tabel β (2 tabel kalau "dua-duanya") |
| **Mediasi** | Tabel β **+ kotak "Pengaruh tak langsung" (a×b)** + label **"mediasi penuh/sebagian"** |
| **Moderasi** | Tabel β **+ grafik garis 2 tingkat Z** (Z rendah vs Z tinggi) |
| **Keduanya** | Semua di atas |

---

## 5. ⚠️ CELAH YANG BELUM TERPECAHKAN (jujur, jangan disembunyikan)

### Celah 1 — **Mediasi butuh 1 kolom hasil BARU: a×b**
β saja **tidak cukup** untuk mediasi. User harus lihat:
- **a** (X→M), **b** (M→Y), **c′** (X→Y langsung)
- **a×b** = pengaruh tak langsung
- **Penuh** kalau c′ **tidak** signifikan · **Sebagian** kalau c′ masih signifikan

**Wulan BELUM rancang bentuk tabel & kalimatnya.** Perlu keputusan Bos.

### Celah 2 — **Seberapa besar a×b yang "wajar"?**
Tidak ada ambang baku seperti R². Wulan usul pakai **perbandingan**:
"pengaruh lewat M **lebih besar** / **lebih kecil** dari pengaruh langsung".
**Butuh ACC Bos.**

### Celah 3 — **Moderasi: mengajar lewat grafik, bukan angka**
Moderasi **tidak bisa dipahami dari β saja**. Harus ada **grafik garis**:
sumbu X = X, sumbu Y = Y, **2 garis untuk Z rendah & Z tinggi**. Kalau kedua
garis **tidak sejajar** → ada moderasi. **Wulan belum rancang grafik ini.**

### Celah 4 — **Mediasi berjenjang (B3): M1→M2→Y**
Butuh **2 mediator berurut**. Tabelnya lebih panjang. **Belum dirancang.**

### Celah 5 — **Kalau X cuma 1, moderasi jadi aneh**
Moderasi butuh **X dan Z**. Kalau user pilih moderasi tapi hanya punya 1 kolom X
→ Z muncul sebagai **kolom baru**. **Belum diputuskan Bos.**

### Celah 6 — **Uji terukur belum ada untuk bentuk GABUNGAN**
Wulan sudah uji 10 bentuk **di mesin**. Tapi **belum** uji **lewat web**
(API → halaman → tampilan). Tanpa itu, Wulan **cuma menebak**.

---

## 6. URUTAN PENGERJAAN (usulan Wulan)

| Fase | Isi | Alasan |
|---|---|---|
| **1** | **Mediasi tunggal** (B1) di web + tabel a, b, c′ + a×b | Paling sering dipakai skripsi/tesis |
| **2** | **Moderasi MRA** (C1) + grafik 2 garis | Kedua tersering |
| **3** | **Tombol "+ perantara" / "+ penguat"** → B2, B3, C2, C3, D1 otomatis | Sekali bangun, 5 bentuk terbuka |
| **4** | Gerbang uji tiap bentuk **lewat web sungguhan** | Wajib, jangan menebak |

---

## 7. ❓ YANG WULAN BUTUH DARI BOS

1. **Tangga 1 (4 kartu) — setuju?** Atau Bos mau langsung 8 pilihan?
2. **Diksi awam** untuk mediasi & moderasi — Wulan usul:
   - Mediasi → **"lewat perantara"**
   - Moderasi → **"ada yang menguatkan/melemahkan"**
   - Moderated mediation → **"perantara yang dikuatkan"**
3. **Celah 1 (tabel a×b)** — bagaimana bentuk yang Bos mau?
4. **Celah 3 (grafik moderasi)** — perlu atau tidak untuk Fase 1?
5. **Fase 1 = mediasi tunggal saja dulu**, atau langsung mediasi + moderasi?

---

## 8. BERKAS TERKAIT

- `audit_mesin.py` — **bukti terukur** 10 bentuk (baru, 18Sep26)
- `app/hitung/spek_pembangun.py:35` — `bangun_dari_spek(spek, ...)`
- `app/hitung/kalibrasi_jalur.py:158` — `kalibrasi_per_jalur(jalur, ..., interaksi=...)`
- `app/hitung/berurutan.py:217` — `tambah_rasa_lapangan` (bug `item_per` DITUTUP)
- `app/hitung/berurutan.py:257-318` — pabrik skenario (8 fungsi siap pakai)
- `alat_spek.py` — jalankan spek dari berkas JSON
- `KANVAS_MODEL_RANCANGAN.md` — rancangan kanvas ketuk-sambung (belum dikoding)
