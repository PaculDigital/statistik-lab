# DOKUMENTASI TAHAP 1.3 — PINTU MODEL DIBUKA (19Sep26)

> **Status: SELESAI & LIVE.** Deploy 16–20 · Gerbang utama **18 grup LULUS** ·
> `uji_sub_regresi.py` **46 LULUS / 0 GAGAL** · 13 bentuk mesin terbuka di UI.

---

## 1. MASALAH YANG DIPECAHKAN

**Diagnosis (dari `TAHAP_PENYELESAIAN.md`):** mesin sudah sangat sanggup
(10 bentuk + Y ganda), **tapi pintu web cuma membuka 3 dari 10**.
Pekerjaan utama = **melebarkan pintu**, BUKAN membuat mesin baru.

**Keputusan Bos 19Sep26 (verbatim):**
> "1. A nanti kalo sudah beres, kamu catat dulu, tapi kamu perlu siapkan ruang
> untuk manova ini, agar tidak bertumpuk dan menimpa. 2. A"

Diturunkan menjadi: ① **4 kartu induk → klik → BARU muncul sub-pilihan** (opsi 1a);
② istilah **BESAR + terjemahan kecil** (opsi 2a); ③ tambah M/Z pakai **tombol**
+ tulis istilah statistiknya: perantara (M), penguat (Z).

---

## 2. YANG DIBANGUN

### 4 KARTU INDUK di `/kuantitatif`

| Kartu | Judul (bahasa tujuan) | Sub-pilihan |
|---|---|---|
| ① | **Regresi** — "satu atau beberapa variabel" | **3** |
| ② | **Ada perantara** — "lewat sesuatu dulu" | **4** |
| ③ | **Ada yang memperkuat / melemahkan** | **6** |
| ④ | **Campuran** | 0 (masih langsung) |
| ⑤ | *(Susun sendiri — TERKUNCI, dibahas belakangan)* | — |

### 3 SUB-PILIHAN REGRESI (Langkah A)

| Sub | Diagram | Galat terukur |
|---|---|---|
| Sederhana | X → Y | 0,0014 |
| Berganda | X1, X2, X3 → Y | 0,0144 |
| Berganda-berantai | X1→X2→X3, lalu ke Y | 0,0185 |

Slug: `sederhana` · `berganda` · `berantai`.

### 4 SUB-PILIHAN MEDIASI (Langkah B)

| Sub | Diagram | Galat terukur |
|---|---|---|
| Tunggal | X → M → Y | 0,0134 |
| Paralel (sejajar) | X → M1, M2 → Y | 0,0138 |
| Berjenjang (bertahap) | X → M1 → M2 → Y | 0,0161 |
| Campuran | sejajar + bertingkat | 0,0231 |

Slug: `mediasi` · `mediasi-paralel` · `mediasi-berjenjang` · `mediasi-campuran`.
**18 dari 18 jalur TEPAT** (kalibrasi_per_jalur, n=300, toleransi 0,03).

### 6 SUB-PILIHAN MODERASI (Langkah C)

| Sub | Diagram | Galat | Interaksi |
|---|---|---|---|
| Tunggal | Z di X→Y | 0,0071 | X×Z→Y |
| Dual | Z1, Z2 di X→Y | 0,0103 | X×Z1, X×Z2→Y |
| Jalur A | Z di X→M | 0,0184 | X×Z→M |
| Jalur B | Z di M→Y | 0,0148 | M×Z→Y |
| Keduanya | 1 Z di dua jalur | 0,0062 | X×Z→M + M×Z→Y |
| Tiga jalur | Z1 & Z2 berbeda | **0,0362** ⚠️ | X×Z1→M + M×Z2→Y |

Slug: `moderasi` · `moderasi-dual` · `moderasi-jalur-a` · `moderasi-jalur-b`
· `moderasi-keduanya` · `moderasi-3jalur`.
**8 dari 8 koefisien interaksi TEPAT** (n=300, toleransi 0,04).

---

## 3. TEROBOSAN PENTING — 3 BENTUK YANG DULU "BELUM TERUJI"

Catatan lama menyebut 3 bentuk moderasi **belum pernah diuji**. Diuji ulang
19Sep26 — **SEMUANYA JALAN**:

| Bentuk | Status lama | Hasil ukur 19Sep26 |
|---|---|---|
| **Jalur B** | ❓ belum pernah | ✅ galat 0,0148 |
| **Keduanya** | ❓ belum pernah | ✅ galat **0,0062** (terbaik!) |
| **3-jalur** | 🔴 pernah GAGAL (bug `item_per`) | ✅ galat 0,0362 |

⇒ **Bug `item_per` (18Sep26) sudah tidak menggigit** untuk 3-jalur.
⇒ **13 bentuk mesin kini terbuka di UI (dari 3).**

---

## 4. CARA KERJA TOMBOL (bukaSub / tutupSub)

```js
bukaSub(ev, nama)   // sembunyikan .grid-model-kartu, tampilkan #sub-<nama>
tutupSub()          // sebaliknya + scroll ke atas
```

- Panel sub-pilihan **`hidden` sejak awal** (keputusan Bos: user lihat 4 induk dulu).
- Fungsi **MANDIRI** — tidak mengambil apa pun dari berkas skrip lain
  (menghindari jebakan **urutan pemuatan** 18Sep26).
- Ditaruh di `{% block skrip %}` (dasar.html baris 109, **sebelum `</body>`**).

### Kelas CSS baru (gaya.css)
| Kelas | Guna |
|---|---|
| `.panel-sub` / `.panel-sub[hidden]` | wadah sub-pilihan |
| `.kepala-sub` | kepala panel (eyebrow + judul + keterangan) |
| `.grid-sub` | grid 2 kolom → 1 kolom di ≤620px |
| `.kartu-pilih.lebar-penuh` | kartu sub melintang penuh |
| `.garis-rantai` | garis rantai antar-X (2px abu, beda dari panah pengaruh) |
| `.denah .mata-rantai` | mata panah rantai |

---

## 5. JEBAKAN YANG KENA (jangan ulang)

1. 🚨 **KELAS SALAH** — Wulan hampir memakai `.pintu` untuk kartu sub.
   **`.pintu` = kartu dua-pintu halaman `/mulai`** (punya `.pintu-ikon`,
   `.pintu-tanya`). Yang benar untuk kartu model = **`.kartu-pilih`**
   (punya `.denah`, `.kartu-judul`, `.kartu-kaki`).
   📌 **ATURAN: sebelum memakai kelas, `grep` dulu kelasnya benar-benar ada.**

2. 🚨 **ESCAPE DOBEL** — hasil patch menulis `<\\/strong>` (dua garis miring)
   → **gerbang tag skrip menangkap 2 pelanggaran**. Perbaikan pakai `sed`
   terarah, bukan patch berlapis.

3. 🚨 **UJI MENYALAHKAN APLIKASI** — uji bilang "GAGAL: dapat 5 kartu",
   padahal kartu ke-5 = **"Susun sendiri" yang SENGAJA TERKUNCI**.
   **Aplikasi BENAR, uji SALAH.** Perbaikan: saring `.kartu-kunci`.
   📌 **ATURAN: uji gagal → periksa dulu APAKAH UJI-NYA yang salah.**

4. 🚨 **DIAGRAM MENYESATKAN** (ketemu dari **VISION**, bukan uji):
   diagram berganda-berantai (a) garis rantai **tanpa mata panah** padahal
   teks bilang "X1 → X2 → X3", (b) **hanya X3 punya jalur ke Y** padahal
   teks bilang "bersama-sama ke Y". **Mahasiswa bisa salah baca diagram.**
   Perbaikan: mata panah ditambah + **ketiga X** digambar menuju Y.
   📌 **ATURAN: diagram WAJIB diperiksa mata (vision), tidak cukup uji DOM.**

5. 🚨 **MENGUJI ALAT YANG SALAH** — Wulan menguji mediasi lewat `buat_data`
   (itu cuma pembangkit **data mentah**; ia tidak tahu mana M mana Y).
   **Nol hubungannya dengan mediasi.** Yang benar: `kalibrasi_per_jalur`.
   📌 **ATURAN: pilih alat ukur yang BENAR-BENAR mengukur yang mau diukur.**

6. 🚨 **SALAH BACA BENTUK HASIL** — uji pertama mediasi **GAGAL SEMUA**
   (`'str' object has no attribute 'get'`). Ternyata cara baca `hasil` salah;
   bentuknya `{"X->M": 0.5498}` (kunci string → angka), **bukan** daftar dict.
   📌 **Kalau SEMUA gagal dengan galat sama, curigai CARA BACA-nya.**

7. 🚨 **`sed` TIDAK MENGGANTI** (pola tidak cocok karena escape berlapis) —
   Wulan kira sudah ganti `data-induk` ke `moderasi`, **ternyata belum**.
   Hampir memverifikasi gambar yang salah. Ketahuan dari **ukuran berkas
   berubah** (144.729 → 135.251 byte).
   📌 **ATURAN: setelah `sed`, BUKTIKAN dengan `grep`/ukuran, jangan percaya.**

---

## 6. UJI & BUKTI

| Uji | Hasil |
|---|---|
| `gerbang_uji.sh` | **18 grup LULUS** (17 lama + 1 baru) |
| `uji_sub_regresi.py` | **46 LULUS / 0 GAGAL** |
| Geometri HP 390px | 6 kartu Moderasi **346×224px** |
| Tautan 7 slug Moderasi | semua **menerapkan jalur**, nol kode tumpah |
| Tautan 4 slug Mediasi | semua menerapkan jalur |
| Vision | diagram Regresi + Mediasi + Moderasi benar |
| Deploy | 16, 17, 18, 19, 20 **EXIT 0**, `/health` ok |
| SOT | selaras |

**Waktu pengerjaan:** Langkah A (deploy 16–18) · B (19) · C (20).

---

## 7. SISA / UTANG

1. **Kartu Campuran (`gabungan`) belum punya sub-pilihan** — masih langsung
   ke `/buat-data?model=gabungan`.
2. **TAHAP 1.4** — tombol "ganti model" selalu terlihat (belum dikerjakan).
3. **3-jalur galat 0,0362** — paling besar, dekat batas 0,04. Sudah ada
   catatan di kode; belum diputuskan apakah perlu peringatan di UI.
4. **7 sub-pilihan Moderasi = banyak** — di HP jadi 7 layar. Bos diminta
   memilih **Tunggal** dulu (sudah ada ajakan di panel). Belum diukur
   apakah user benar-benar tidak bingung.

---

## 8. CARA BALIK

Bos bilang **"lanjut tahap 1.4"** / **"lanjutkan statistik"** →
baca `TAHAP_PENYELESAIAN.md` + `FLAG_LANJUT_DISINI.md` blok teratas.
