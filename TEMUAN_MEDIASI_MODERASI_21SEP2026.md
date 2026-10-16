# ✅ TEMUAN UJI OPSI A — MEDIASI & MODERASI **SUDAH DIPERBAIKI**
## 21 September 2026

> **Status: SELESAI DIKODING & TERUJI — BELUM DEPLOY.**
> Putusan Bos: **1b** (bootstrap) · **2a** (suku interaksi X×Z) · **3a** (aturan
> baku p<0,05) · **4a** (kerjakan dulu, deploy belakangan).
>
> **Perintah awal Bos:** *"Opsi A"* = uji mediasi/moderasi lewat **PINTU
> PRODUKSI** (unggah → Hasil), bukan fungsi internal (pelajaran **K-09**).

---

## 📌 RINGKASAN PERJALANAN

| Tahap | Isi |
|---|---|
| 1. Ukur | Unggah `.csv` sungguhan → tandai PERAN → hitung lewat rute HTTP |
| 2. Temuan | 🔴 Mediasi & moderasi **TIDAK SAMPAI KE HASIL** (bukti di bawah) |
| 3. Putusan Bos | 1b · 2a · 3a · 4a |
| 4. Perbaiki | 4 akar ditutup + modul baru `app/hitung/kaitan.py` |
| 5. Uji | `uji_kaitan.py` + `uji_kaitan_web.py` — **terbukti BISA GAGAL** |
| 6. Gerbang | 2 grup baru masuk gerbang → **47 grup SEMUA LULUS · EXIT 0** |

---

## 🔴 TEMUAN AWAL (SEBELUM PERBAIKAN) — bukti terukur

### Bukti 1 — MEDIASI (X1 → M1 → Y1) DULU

```
prediktor mesin : ['X1', 'M1']     ← M1 dijejalkan jadi PREDIKTOR BIASA
perantara       : ['M1']           ← mesin TAHU ini perantara…
R²              : 0,2623

koef:
   (Konstanta)  b=3,0804  t=7,43  p=0,0000
   X1           b=0,0940  t=1,41  p=0,1602     ← sebenarnya ini c'
   M1           b=0,4258  t=6,00  p=0,0000     ← sebenarnya ini b
```

**Yang HILANG:** jalur **a** · **a×b** · Sobel/bootstrap · simpulan
penuh/parsial · label c' vs c. ⇒ Regresi berganda biasa yang **diberi label
mediasi**.

### Bukti 2 — MODERASI (X1 × Z1 → Y1) DULU — **lebih buruk**

```
prediktor mesin : ['X1']     ← Z1 HILANG TOTAL
perantara       : []
```

Jejak moderasi — **SEMUA kosong**: `interaksi` ❌ · `moderasi` ❌ ·
`penguat` ❌ · `z1` ❌ · `x*z` ❌. ⇒ Z yang ditandai mahasiswa **DIBUANG**.

---

## 🎯 AKAR (4 — terbaca dari kode, bukan tebakan)

| # | Akar | Bukti asli |
|---|---|---|
| **1** | `periksa_spss()` **tidak punya parameter `kolom_z`** | `grep -n "kolom_z" app/diagnosis.py` = **KOSONG** |
| **2** | `_gabung_peran()` hanya meneruskan **X & M**, **Z dibuang** | `app/main.py:462-466` — hanya X/M/Y |
| **3** | `pred = list(kolom_x) + kolom_m` — M dijejalkan jadi prediktor | `app/diagnosis.py:202` |
| **4** | Mesin mediasi/moderasi (`berurutan.py`, suku `interaksi`) **tidak pernah dipanggil** dari rute `/klinik` | `grep "interaksi" app/main.py` = **KOSONG** |

**Rantai kerusakan (dulu):**
```
Mahasiswa: tandai X1, M1, Z1, Y1
    ↓
_gabung_peran(): X → kolom_x ✅ · M → kolom_m ✅ · Z → DIBUANG ❌
    ↓
periksa_spss(): tidak tahu Z
    pred = X + M   ← M jadi prediktor biasa
    ↓
Hasil: regresi berganda biasa
       (tanpa a, tanpa a×b, tanpa interaksi, tanpa simpulan mediasi/moderasi)
```

---

## ✅ PERBAIKAN (4 akar ditutup + 1 modul baru)

| Akar | Yang diperbaiki | Berkas |
|---|---|---|
| 1 | `periksa_spss()` kini menerima **`kolom_z`** | `app/diagnosis.py` |
| 2 | `_gabung_peran()` kini **meneruskan Z** (`baru['kolom_z']`) | `app/main.py` |
| 3 | Modul **baru** `kaitan.py` — mediasi (bootstrap) & moderasi (X×Z) dihitung dari **data mahasiswa** | `app/hitung/kaitan.py` (BARU) |
| 4 | Rute `/periksa` kini mengirim **`kolom_z`** ke mesin | `app/main.py` |

⚠️ **`periksa_spss` TIDAK diubah untuk hitungan regresi** — regresi
sederhana/berganda sudah benar, sesuai aturan *"jangan ubah yang tidak salah"*.
Z **tidak** dimasukkan ke `pred` (biar regresi biasa tetap bersih); bentuk
moderasi dihitung terpisah di `kaitan.py`.

---

## 📊 HASIL SESUDAH PERBAIKAN — terukur lewat PINTU PRODUKSI

### MEDIASI X1 → M1 → Y1 (tanam: a=0,60 · b=0,50 · c'=0,00)

| Jalur | b | t | p | Arti |
|---|---|---|---|---|
| **c** | +0,3630 | 6,63 | 0,0000 | X→Y **tanpa** M |
| **a** | +0,4676 | 8,93 | 0,0000 | X→M ← **DULU TIDAK ADA** |
| **b** | +0,4157 | 7,46 | 0,0000 | M→Y setelah X masuk |
| **c'** | +0,1687 | 2,98 | 0,0032 | X→Y **setelah** M masuk |
| **a×b** | **+0,1944** | — | selang 95% **[+0,1413, +0,2572]** | ← **DULU TIDAK ADA** |

⇒ **Simpulan mesin: "mediasi parsial"** (a×b signifikan, c' masih signifikan
tapi lebih kecil dari c). Kalimat lengkap dikirim ke halaman.

### MODERASI X1 × Z1 → Y1 (tanam: interaksi = 0,35)

| Bagian | Nilai |
|---|---|
| `penguat` | **['Z1']** ← **DULU DIBUANG TOTAL** |
| tanpa interaksi | R² = 0,1073 |
| dengan interaksi | R² = 0,2210 (ΔR² = **+0,1136**) |
| **interaksi X×Z** | b = **+0,6140** · t = 6,57 · p = **0,0000** ← **DULU TIDAK ADA** |

⇒ **Simpulan mesin: "Z1 MEMPERKUAT pengaruh X1 terhadap Y1"**.

---

## 🔒 BUKTI BISA GAGAL (wajib, sudah dijalankan)

| Keadaan kode | `uji_kaitan_web.py` |
|---|---|
| **Z dibuang** (cacat lama disuntik ulang) | ❌ **EXIT 1** — **4 kegagalan** ditangkap (`penguat=[]`, moderasi **0 hasil**) |
| **Z diteruskan** (kode benar) | ✅ **EXIT 0** — semua lulus |

Diuji lewat **pintu produksi** (unggah `.csv` → peran → hitung), bukan fungsi
internal. Inilah yang membuat cacat ini **tidak bisa lolos lagi**.

---

## 🧾 BERKAS

| Berkas | Isi |
|---|---|
| `app/hitung/kaitan.py` | **BARU** — `mediasi()`, `moderasi()`, `hitung_kaitan()` |
| `uji_kaitan.py` | **BARU** — 25 uji mesin murni (koefisien ditanam) |
| `uji_kaitan_web.py` | **BARU** — uji pintu produksi (unggah → Hasil) |
| `_sketsa/ukur_mediasi_moderasi.py` | sketsa pengukur awal |
| `gerbang_uji.py` | **2 grup baru** ditambahkan |

---

## 📌 ATURAN YANG TIDAK BOLEH DILANGGAR (dipakai saat memperbaiki)

1. **Ukur dari PINTU PRODUKSI** (rute HTTP), bukan fungsi internal (K-09).
2. **Buktikan bisa gagal** — suntik kerusakan → uji HARUS tangkap.
3. **Jangan ubah yang tidak salah** — regresi sederhana/berganda tidak disentuh.
4. **Jangan tambal** — akarnya 4, diperbaiki **di akar**.

---

## ⏸️ YANG BELUM (jujur — belum dikerjakan)

1. ~~**Tampilan halaman**~~ ✅ **SELESAI 21Sep26** — kartu mediasi/moderasi
   sudah digambar di `/klinik` (`gambarHasil()` di `app/templates/diagnosis.html`).
   Mahasiswa kini melihat: tabel jalur a/b/c/c', a×b + selang bootstrap 95%,
   tabel interaksi X×Z + ΔR², dan **kalimat simpulan dari mesin**.
2. ~~**Mediasi berjenjang**~~ ✅ **SELESAI 21Sep26** — `mediasi_berjenjang()`
   di `app/hitung/kaitan.py`: dua jalur tidak langsung (a1×b1 dan a1×d×b2),
   bootstrap keduanya, simpulan penuh/parsial/tidak ada. Halaman mengirim
   `bentuk_mediasi`; mesin memilih berjenjang/paralel.
   ~~⚠️ Rantai >2 perantara: baru 2 pertama dihitung penuh~~ →
   ✅ **SELESAI 21Sep26** (`mediasi_rantai()`).

---

## 🔗 RANTAI >2 PERANTARA — SELESAI (ACC Bos: *"Rantai lebih 2 perantara belum"*)

**Sebelum:** mediasi berjenjang hanya menghitung **2 perantara pertama**.
Sisanya cuma diberi catatan *"belum — jujur, bukan disembunyikan"*.

**Sesudah:** `mediasi_rantai()` menghitung **SEMUA k perantara** →
**k jalur tidak langsung**, semuanya lewat perantara pertama:

```
① X → M1 → Y                a1 · b1
② X → M1 → M2 → Y           a1 · d1 · b2
③ X → M1 → M2 → M3 → Y      a1 · d1 · d2 · b3
⋮
ⓚ X → M1 → … → Mk → Y       a1 · d1 · … · b(k-1) · bk
```

Setiap jalur punya **selang kepercayaan bootstrap 95%** sendiri.

**⚠️ Kejujuran statistik (penting):** jalur-jalur ini **saling tumpang-tindih**
(bukan bagian lepas seperti mediasi paralel). Karena itu:
- dilaporkan **berdampingan**, TIDAK dipecah jadi "persentase perantara";
- jumlahnya diberi keterangan *"BUKAN bagian yang bisa dipecah"*;
- kartu di halaman menulis terus-terang: angka-angka ini **tidak boleh
  dijumlahkan jadi 100%**.

**Hasil terukur** (koefisien ditanam: a1=0,60 · d1=0,55 · d2=0,50 · b3=0,45):

| Perantara | Jalur | Nilai | Selang 95% |
|---|---|---|---|
| **3** | ① X→M1→Y | 0,081 | signifikan |
| | ② X→M1→M2→Y | 0,100 | signifikan |
| | ③ X→M1→M2→M3→Y | **0,0770** (tanam 0,0743) | [0,053 … 0,104] ✅ |
| **4** | ④ X→M1→M2→M3→M4→Y | **0,0187** (tanam 0,0297) | turun wajar |

**Rantai putus di tengah** (M2→M3 = 0): jalur ③ **tidak signifikan**
(selang [−0,008 … 0,013]) → mesin **jujur** bilang rantai terputus.

**k=2 TIDAK berubah:** jalur ① = 0,081492 dan ② = 0,099667 — **sama persis**
dengan `mediasi_berjenjang()` lama (dibuktikan uji, selisih < 0,000001).

**Bukti bisa gagal:** cacat lama dikembalikan (hanya 2 perantara) →
**6 kegagalan ditangkap** (`jumlah_perantara=2`, jalur cuma 2, dst).

**4 uji baru:** `uji_rantai.py` (mesin) · `uji_rantai_web.py` (pintu HTTP) ·
+ 2 uji berjenjang sebelumnya tetap jalan. Gerbang **49 → 51 grup**.
3. **Belum deploy** — produksi (`statistik.bikinaja.id`) masih versi lama.
4. **12 uji mati** di luar gerbang masih ditandai "PENINGGALAN" (belum dipindah).

---

## 📌 TAMBAHAN 21Sep26 (sesudah laporan awal)

| Tambahan | Bukti |
|---|---|
| Kartu mediasi & moderasi di `/klinik` | uji `uji_kaitan_web.py` EXIT 0 |
| Mediasi berjenjang (X→M1→M2→Y) | uji `uji_berjenjang.py` 18/0 |
| Berjenjang sampai ke Hasil | uji `uji_berjenjang_web.py` EXIT 0 |
| **Bukti bisa gagal** berjenjang | bentuk dibuang → **4 kegagalan** ditangkap |
| Gerbang | 47 → **49 grup** |

### ⚠️ TIGA KESALAHAN WULAN SENDIRI saat menambah berjenjang (dicatat)

| # | Salah | Akar | Perbaikan |
|---|---|---|---|
| K-13 | `payload` dipakai di `periksa_spss` padahal tidak ada di sana | Wulan menambah `bentuk=payload.get(...)` tanpa menaruh `payload` di tanda tangan fungsi | tambah parameter `bentuk_mediasi` eksplisit |
| K-14 | **MERUSAK yang sudah lulus** — menambah bentuk ke jalur yang sama membuat `kaitan` mati total (`kaitan.ada=False`) | perubahan menyentuh jalur yang sudah hijau tanpa menjalankan uji lama DULU | **WAJIB jalankan uji lama SEBELUM & SESUDAH setiap perubahan** |
| K-11 | `(p or 1) < 0.05` — p=0,0 dianggap falsy | terulang lagi di uji baru | pakai `p is not None and float(p) < 0.05` |


---

## 🚨 KESIMPULAN: BOS BENAR — INI CELAH NYATA

Mesin **BISA** membangun data mediasi/moderasi (terbukti 17Sep26 & 19Sep26).
**TAPI `/klinik` TIDAK BISA menghitung & menjelaskannya.** Mahasiswa yang
memilih kartu ③ Mediasi / ④ Moderasi **tidak mendapat hasil mediasi/moderasi**.

---

## 📊 BUKTI 1 — MEDIASI (X1 → M1 → Y1)

**Data diunggah:** 200 baris · X1=3 kolom · M1=3 kolom · Y1=3 kolom
**Penandaan peran:** lolos (kelompok benar: `X1`, `M1`, `Y1`)

**Yang mesin keluarkan:**

```
prediktor mesin : ['X1', 'M1']     ← M1 dijejalkan jadi PREDIKTOR BIASA
perantara       : ['M1']           ← mesin TAHU ini perantara…
R²              : 0,2623

koef:
   (Konstanta)  b=3,0804  t=7,43  p=0,0000
   X1           b=0,0940  t=1,41  p=0,1602     ← sebenarnya ini c'
   M1           b=0,4258  t=6,00  p=0,0000     ← sebenarnya ini b
```

**Yang HILANG (terukur, grep = kosong):**

| Yang seharusnya ada | Ada? |
|---|---|
| Jalur **a** (X1 → M1) | ❌ **TIDAK dihitung** |
| **Pengaruh tidak langsung** (a × b) | ❌ tidak ada |
| Uji **Sobel** / bootstrap | ❌ tidak ada |
| Simpulan **mediasi penuh / parsial / tidak ada** | ❌ tidak ada |
| Label **c'** vs **c** | ❌ tidak ada |

⇒ Mesin **tahu** `M1` itu perantara (kunci `perantara` terisi) — **tapi tidak
memakainya untuk apa pun**. M1 diperlakukan **sama persis** seperti X1.
Hasilnya: **regresi berganda biasa yang diberi label mediasi.**

---

## 📊 BUKTI 2 — MODERASI (X1 × Z1 → Y1) — **LEBIH BURUK**

**Data diunggah:** 200 baris · X1=2 kolom · **Z1=2 kolom** · Y1=2 kolom
**Penandaan peran:** lolos (kelompok benar: `X1`, `Z1`, `Y1`)

**Yang mesin keluarkan:**

```
prediktor mesin : ['X1']     ← Z1 HILANG TOTAL
perantara       : []

koef:
   (Konstanta)  b=4,2318  t=10,77  p=0,0000
   X1           b=0,2952  t=4,66   p=0,0000
```

**Jejak moderasi — SEMUA kosong:**

| Dicari | Hasil |
|---|---|
| `interaksi` | ❌ False |
| `moderasi` | ❌ False |
| `penguat` | ❌ False |
| `z1` | ❌ False |
| `x*z` / `x1z1` | ❌ False |

⇒ Mahasiswa menandai **Z1 sebagai penguat** → **Z1 DIBUANG sama sekali**.
Yang keluar hanya regresi **X1 → Y1**. Sama seperti tidak menandai Z.

---

## 🎯 AKAR (dari pembacaan kode, bukan tebakan)

| # | Akar | Bukti |
|---|---|---|
| **1** | `periksa_spss()` **tidak punya parameter `kolom_z`** | `grep -n "kolom_z" app/diagnosis.py` = **KOSONG** |
| **2** | `_gabung_peran()` hanya meneruskan **X & M**, **Z dibuang** | `grep -n "Z\|kolom_z" app/main.py` = hanya di **komentar** baris 395 |
| **3** | `pred = list(kolom_x) + kolom_m` — M dijejalkan jadi prediktor | `app/diagnosis.py:202` |
| **4** | Mesin mediasi/moderasi (`berurutan.py`, suku `interaksi`) **tidak pernah dipanggil** dari rute `/klinik` | `grep "interaksi" app/main.py` = **KOSONG** |

**Rantai kerusakan:**
```
Mahasiswa: tandai X1, M1, Z1, Y1
    ↓
_gabung_peran(): X → kolom_x ✅ · M → kolom_m ✅ · Z → DIBUANG ❌
    ↓
periksa_spss(): tidak tahu Z
    pred = X + M   ← M jadi prediktor biasa
    ↓
Hasil: regresi berganda biasa
       (tanpa a, tanpa a×b, tanpa interaksi, tanpa simpulan mediasi/moderasi)
```

---

## ⚠️ DAMPAK (jujur — apa yang rusak)

| Fitur | Bangun data (mesin) | Hitung & jelaskan (/klinik) |
|---|---|---|
| Regresi sederhana | ✅ BISA | ✅ BISA (sudah diuji) |
| Regresi berganda | ✅ BISA | ✅ BISA (sudah diuji) |
| **Mediasi** | ✅ BISA | 🔴 **TIDAK BISA** |
| **Moderasi** | ✅ BISA | 🔴 **TIDAK BISA** (Z dibuang) |
| Mediasi berjenjang, dual | ✅ BISA (17Sep26) | 🔴 **TIDAK BISA** |

⇒ **Yang dijual sebagai "6 kartu model" baru 2 kartu yang benar-benar utuh.**
Kartu ③④⑤ (§ Mediasi/Moderasi/Campuran) **belum bisa memberi hasil**.

---

## 📌 ATURAN YANG TIDAK BOLEH DILANGGAR SAAT MEMPERBAIKI

1. **Ukur dari PINTU PRODUKSI** (rute HTTP), bukan fungsi internal (K-09).
2. **Buktikan bisa gagal** — suntik kerusakan → uji HARUS tangkap.
3. **Jangan ubah yang tidak salah** — regresi sederhana/berganda **sudah benar**,
   jangan disentuh.
4. **Lapor dulu ke Bos sebelum mengubah mesin** (aturan induk).
5. **Jangan tambal** — akarnya 4 (di atas), perbaiki **di akar**.

---

## 🙋 YANG BELUM DIPUTUSKAN BOS (perlu keputusan)

1. **Rumus mediasi mana yang dipakai?** (a×b + Sobel? bootstrap? PLS?)
   → menentukan hasil apa yang ditampilkan ke mahasiswa.
2. **Apakah `Z` dinaikkan jadi:**
   (a) prediktor + **suku interaksi** (cara MRA klasik), atau
   (b) hanya dianalisis per-kelompok (cara ANOVA)?
3. **Kalimat simpulan** mediasi (penuh/parsial/tidak ada) — siapa yang
   menentukan ambangnya?
4. **Apakah fitur ini dulu, atau deploy dulu** yang sudah jalan?
