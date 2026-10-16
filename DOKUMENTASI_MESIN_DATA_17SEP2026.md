# DOKUMENTASI MESIN DATA — Penelitian STATISTIK Lab.
### Riwayat 18 putaran: dari gagal → terbukti presisi
**Tanggal:** 17 September 2026 · **Status akhir:** 29 LULUS / 0 GAGAL

---

## 1. MASALAH AWAL

Bos meminta alat yang bisa **membuat data penelitian sesuai setelan**. Contoh setelan:
> "X1 → Y = 0,35 · X2 → Y = 0,45 · X3 → Y = 0,30"

Masalahnya: **selalu meleset**. X3 khususnya **tidak pernah** mencapai 0,30 — mau dinaikkan berapa pun, mentok di 0,15–0,31.

---

## 2. DELAPAN AKAR YANG DITEMUKAN SATU PER SATU (semua TERUKUR)

| # | Akar | Bukti terukur | Perbaikan |
|---|---|---|---|
| 1 | Menyetel **korelasi mentah**, bukan **koefisien regresi** | X1 minta 0,35 keluar 0,07 | `_korelasi_dari_beta()` |
| 2 | **Derau** menyusutkan koefisien beraturan | β 0,45 → 0,333 saat derau 30% | `koreksi_derau()` |
| 3 | **Batas muat item** mentok 0,866 | `clip(0,15–0,75)` → muat maks 0,866 | perbaiki pembangkit item |
| 4 | **Pembulatan Likert** meredam sinyal | skala 1–5 → hanya 5 nilai | perbaiki pembulatan |
| 5 | **`_std(y)`** mengecilkan semua koefisien | β 0,45 → 0,333 seragam | JANGAN std pada Y |
| 6 | **Atenuasi reliabilitas** | a 0,60→0,4732 (rasio 0,789) | bagi √(alpha) |
| 7 | **`rng` bersama** → koefisien berpindah kolom | M1→Y keluar **0,0013** padahal minta 0,35 | rng **terpisah** tiap konstruk |
| 8 | **Derau terlalu kecil** untuk variabel "kembar" | bobot M1 **mentok 0,98**, hasil tetap 0,2948 | **derau otomatis** dari struktur |

---

## 3. LIMA PENDEKATAN YANG DICOBA (4 gagal, 1 berhasil)

### ❌ Pendekatan 1 — Matriks korelasi (`mesin.py`)
Bangun semua variabel dari **satu matriks korelasi**, hitung balik dari β.
**Gagal karena:** matriks **mendesak batas positive-definite** saat koefisien besar → koefisien bergeser tak terkendali (*suppression effect*). Minta 0,35/0,45/0,30 → keluar 0,30/0,40/0,09.

### ❌ Pendekatan 2 — Model struktural langsung (`struktural.py`)
`Y = b·X + error`, lalu turun ke item. **Dua perbaikan penting ditemukan di sini:**
1. X **harus** distandardisasi (z-skor) **sebelum** Y dihitung.
2. Y **tidak boleh** distandardisasi **setelah** error ditambahkan.

Hasil di skor konstruk: **0,3481 / 0,4501 / 0,3043** ✅ — tapi **setelah jadi item Likert meleset ~0,12**.

### ❌ Pendekatan 3 — Kalibrasi global iteratif (`kalibrasi.py`)
Cari koefisien via optimasi numerik. **Gagal karena BERAYUN:**
```
p115: b = 0,35/0,45/0,30 → hasil 0,308/0,459/0,078
p116: b = 0,65/0,75/0,60 → hasil 0,331/0,461/0,147
p117: b = 0,35/0,45/0,30 → hasil 0,308/0,459/0,078   ← KEMBALI
```
Mengubah **semua bobot bersamaan** tapi **hanya punya satu ukuran gabungan** → tidak tahu mana yang harus digeser.

### ❌ Pendekatan 4 — Matriks tervalidasi + pilih seed (`generator.py`)
Matriks korelasi **divalidasi** (eigen-min > 0) + pilih seed terbaik.
**Gagal karena:** koreksi **saling berebut** antar variabel; memperbaiki X1 → merusak X3.

### ✅ Pendekatan 5 — BANGUN BERURUTAN + KALIBRASI PER-JALUR (`berurutan.py` + `kalibrasi_jalur.py`)
**INILAH YANG BERHASIL.**

---

## 4. CARA YANG BERHASIL — PENJELASAN LENGKAP

### 4.1 Bangun berurutan (induk → anak)

```
X1, X2, X3   ← eksogen, terstandardisasi (varians 1), saling berkorelasi 0,2
M  = a·X + e ← derau berskala TETAP (tidak distandardisasi!)
Y  = c'·X + b·M + e
```

**Kenapa berhasil:** koefisien pada **skor konstruk = yang dipasang** (galat ~0,01), karena:
- Sumber berskala 1 → `b_i = cov(sumber, target)`
- Target **tidak dibagi SD-nya** → skala apa adanya

**Bukti (n=200.000):** `0,3488 / 0,4499 / 0,3019` vs minta `0,35 / 0,45 / 0,30`.

### 4.2 Koreksi atenuasi

Masuk ke item Likert menyusutkan koefisien dengan **rasio seragam ~0,78**:

```
rasio terukur: a 0,60 → 0,4732  (0,789)
               b 0,40 → 0,3056  (0,764)
```

Mendekati **√(alpha)**. Maka:

```
b_bangun = b_minta / √(alpha_sumber · alpha_target)
```

**WAJIB:** alpha ditentukan **di awal** (`alpha_rencana`) dan **DIPAKSA tetap** antar-putaran — kalau alpha berubah, kalibrasi tidak konvergen.

### 4.3 Kalibrasi per-jalur

```
untuk setiap TARGET (satu target = satu regresi):
    bangun → UKUR (skor item → regresi terstandardisasi, cara SPSS)
    geser bobot = 0,85 × galat   (clip ±0,98)
ulangi sampai galat maks ≤ toleransi
```

**Kenapa per-jalur:** mengukur per-jalur memberi **sinyal tunggal** yang menunjukkan **mana** yang harus digeser. Kalibrasi global tidak punya itu.

### 4.4 Derau otomatis

Kalau 2+ variabel lahir dari **induk yang sama**, mereka "kembar" bila derau kecil → regresi tak bisa memisahkan → bobot **mentok 0,98**.

| Jumlah "saudara" | Derau |
|---|---|
| 1 | 0,5 |
| 2 | **1,0** |
| 3 | 1,2 |

**Bukti:** derau 0,5 → galat **0,1052** (mentok) · derau 1,0 → galat **0,0099** ✅

---

## 5. HASIL AKHIR — MODEL JURNAL BOS

*Model of Goal-Directed Student Decision Quality in Choosing a University*
9 konstruk · 12 hipotesis · 4 tingkat · 1 jalur NH · 2 keluaran paralel

```
putaran = 4 | galat maks = 0,0288 | tercapai = TRUE
```

**13/13 jalur OK** — termasuk **jalur NH** (0,10 → 0,1008, galat 0,0008) dan **jalur negatif** (DecSatis→Switching −0,30 → −0,3025).

---

## 6. PELAJARAN METODOLOGIS (untuk diajarkan ke mahasiswa)

1. **Koefisien regresi berganda ≠ korelasi.** β = pengaruh **murni** setelah variabel lain dikeluarkan. Karena itu β berganda **selalu lebih kecil** dari r sederhana.
2. **Makin besar korelasi antar-X → makin tidak stabil koefisien** (multikolinearitas). Terukur: dengan korelasi antar-X 0,2 → galat 0,016; dengan 0,6 → galat 0,076.
3. **Atenuasi:** korelasi antar **skor terukur** selalu **lebih kecil** dari korelasi **konstruk sebenarnya** — karena setiap pengukuran mengandung galat. Faktor = reliabilitas.
4. **Galat pensampelan:** σ koefisien ≈ 1/√n. n=50 → ±0,14 · n=2000 → ±0,013.
   **Konsekuensi mengajar:** hasil lapangan **tidak akan pernah** persis sama dengan harapan peneliti. Itu **normal**, bukan kesalahan.
5. **Data yang "terlalu persis" justru curiga.** Koefisien 0,350/0,450/0,300 bulat sempurna di n=50 = **tanda dibuat-buat**.

---

## 7. PELAJARAN CARA KERJA (untuk Wulan di masa depan)

> **17 putaran gagal karena Wulan mengubah RUMUS KOREKSI.**
> Masalah sebenarnya ada di **URUTAN PEMBANGUNAN** dan **`rng` BERSAMA** — bukan di rumus.

- Setiap "perbaikan" yang **membaikkan satu jalur & merusakkan jalur lain** = **tanda menambal**, bukan menyembuhkan. **Berhenti & ganti pendekatan.**
- **Kalau hasil IDENTIK padahal kode diubah** → perubahan **tidak berpengaruh**; cari **akar lain** (itu petunjuk terkuat).
- **Uji TERISOLASI** sebelum uji penuh: kalau 1 jalur bisa persis tapi model penuh tidak → masalahnya di **GABUNGAN**, bukan komponennya.
- **Jangan `_std()`** pada apa pun yang koefisiennya diukur.
- **Satu `rng` untuk satu variabel.**

---

## 8. CARA MENJALANKAN

```bash
cd /opt/data/services/statistik-lab

.venv/bin/python uji_kalibrasi_jalur.py   # 29 LULUS / 0 GAGAL
.venv/bin/python uji_jurnal.py            # model jurnal Bos
.venv/bin/python uji_penutup.py           # 2 mode + sampel kecil
```

**Nilai dari EXIT CODE, bukan grep teks.**
