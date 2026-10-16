# 🎓 DOKUMENTASI KARTU UJI t — 19 September 2026

> Kartu BELAJAR ke-7: **"Uji t: signifikan kok negatif?"**
> Status: **LIVE** di `statistik.bikinaja.id/belajar`.
> Uji: **13 LULUS / 0 GAGAL** · Gerbang utama: **17 grup LULUS**.

---

## 1. ASAL MASALAH — PERTANYAAN BOS (18Sep26)

> *"Sering pada uji t mahasiswa menemukan hasilnya signifikan tapi nilainya
> negatif. Bagaimana penjelasan kamu?"*

Jawaban inti yang jadi fondasi kartu:

| Pertanyaan | Dijawab oleh | Nilainya |
|---|---|---|
| **"Apakah pengaruhnya NYATA?"** | **Sig. (p-value)** | signifikan / tidak |
| **"Arahnya ke mana?"** | **TANDA pada B** | positif / negatif |

**Keduanya BERDIRI SENDIRI.** Jadi kombinasi = **2 × 2 = 4 kemungkinan** —
**semuanya SAH terjadi**.

---

## 2. DISKUSI 3 PUTARAN (18-19Sep26)

### Putaran 1 — "Kenapa signifikan kok negatif?"
Wulan paparkan **6 sebab**:
1. Arah hipotesis memang berlawanan (paling sering)
2. **Kode skala kuisioner terbalik** (item "mahal" diskor 5)
3. Multikolinearitas (VIF > 10) — tanda B bisa berputar
4. Pencilan / data ekstrem
5. Variabel memang kebalikan secara konsep ("Biaya", "Risiko")
6. Salah pilih Y ("Ketidakpuasan" seharusnya "Kepuasan")

### Putaran 2 — "Apa saja keluaran uji t? Bisa tidak signifikan + positif/negatif?"
Bos **memancing miskonsepsi ke-2** yang awalnya tidak terpikir Wulan:

| # | Sig. | Tanda B | Arti | Label |
|---|---|---|---|---|
| 1 | < 0,05 | + | Ada pengaruh nyata, searah dugaan | **DITERIMA** |
| 2 | < 0,05 | − | Ada pengaruh nyata, berlawanan | **ADA TEMUAN** |
| 3 | 0,05–0,10 | ± | Di batas (marginal) | **HATI-HATI** |
| 4 | > 0,05 | + | Tidak ada bukti pengaruh | **TIDAK TERBUKTI** |
| 5 | > 0,05 | − | Tidak ada bukti pengaruh | **TIDAK TERBUKTI** |

> 🚨 **MISKONSEPSI KE-2:** *"Sig. 0,142 tanda plus → berarti pengaruhnya positif!"*
> **SALAH.** Kalau TIDAK signifikan, **tandanya TIDAK boleh ditafsirkan**.
> Angka +0,204 itu bisa saja kebetulan.

### Putaran 3 — "Sebab + cara memperbaiki? Apakah itu curang?"
Bos minta **tambahan** — dan ini jadi **lapis ke-3** kartu.

**PRINSIP PEMISAH (uji lakmus):**
> *"Saya mengubah ini karena datanya MEMANG SUDAH BEGINI — atau karena saya
> TIDAK SUKA hasilnya?"* Kalau jawabannya yang **kedua** → itu curang.

**Kuncinya satu: URUTAN.** Rencanakan dulu di BAB III → baru lihat hasil.
Kalau hasil dilihat dulu, baru aturan diubah — itulah masalahnya.

---

## 3. STRUKTUR AKHIR — 3 LAPIS (ACC Bos: 1A · 2A · 3A)

```
┌─────────────────────────────────────────────────────────────┐
│ LAPIS ①  "Hasilmu yang mana?"                               │
│   5 kotak: 4 kuadran (Sig × tanda) + 1 marginal             │
│   Tiap kotak tampilkan angka SPSS + pita label              │
├─────────────────────────────────────────────────────────────┤
│ LAPIS ②  Arti & contoh penulisan                            │
│   Diagram sebaran (naik/turun) + arti bahasa sehari-hari    │
│   ✓ Tulis seperti ini:   ...                                 │
│   ✗ Jangan menulis:      ...                                 │
├─────────────────────────────────────────────────────────────┤
│ LAPIS ③  Kenapa bisa begitu & boleh diperbaiki?             │
│   Tabel: sebab | cara memperbaiki | BOLEH?                  │
│   Label: ✅SAH  ⚠️HATI-HATI  ❌CURANG                        │
│   + kotak "uji lakmus"                                       │
│   + KARTU "5 Cara Hack yang Harus Dihindari" (kepala MERAH) │
│   + tombol "Belum yakin datanya benar?" → daftar periksa    │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. ISI 5 CARA HACK (kepala MERAH `rgb(168,90,90)`)

| # | Nama | Bentuknya |
|---|---|---|
| 1 | **p-hacking** | Buang data / ganti rumus terus-menerus demi Sig. < 0,05 |
| 2 | **Menggeser batas α** | α 0,05 → 0,10 **setelah** melihat hasil tidak signifikan |
| 3 | **Fishing (Data Dredging)** | Coba banyak model, laporkan yang lolos saja |
| 4 | **HARKing** | Ubah hipotesis **setelah** tahu hasilnya |
| 5 | **Buang pencilan tanpa dasar** | Hapus responden "aneh" hanya karena mengganggu hasil |

**Penutup kartu:** *"Kuncinya cuma satu: urutan. Rencanakan dulu di BAB III,
baru lihat hasil. Kalau hasil dilihat dulu, baru aturan diubah — itulah masalahnya."*

**Kalimat pembuka (menenangkan, sesuai permintaan Bos):**
> *"Bukan karena penguji melarang — tapi karena hasilnya jadi tidak bisa dipercaya,
> termasuk oleh dirimu sendiri."*

---

## 5. KEPUTUSAN TAMPILAN — DARI SKETSA KE JADI

Wulan membuat **3 putaran sketsa** + **3 variasi warna**, Bos memilih:

| Hal | Keputusan Bos |
|---|---|
| Judul | **"5 Cara Hack yang Harus Dihindari"** (ganti dari "5 cara yang kamu hindari") |
| Warna kartu HACK | **V3 STRIP, tapi warna MERAH** (bukan coklat tinta) |
| Daftar periksa | **Pakai TOMBOL** (tertutup dulu, muncul saat diklik) |
| Susunan | **2 tingkat** (pilih hasil dulu → keluar artinya) |

**Cara memilih warna:** Wulan tawarkan V1 tinta gelap, V2 merah lembut, V3 strip
gelap. Bos pilih **V3 tapi merah** → kepala merah `rgb(168,90,90)`, badan putih.
Kontras **tanpa tabrakan** dengan tema kertas hangat.

---

## 6. 🚨 TIGA JEBAKAN BARU (TERUKUR — jangan ulang)

### Jebakan 1 — URUTAN PEMUATAN SKRIP (paling berbahaya)

```
Galat    : ReferenceError: Cannot access 'ujitAktif' before initialization
Gejala   : 0 kotak hasil tampil, TAPI halaman HTTP 200 dan tampak "hidup"
```

**Yang menipu:** urutan **BARIS** sudah benar —
`let ujitAktif` di baris 1015, pemanggilan `ujitLot()` di baris 1138. Tetap galat.

**AKAR SEBENARNYA — urutan PEMUATAN berkas:**

```
baris  488  <script>                        ← skrip halaman BELAJAR mulai
baris 1140  pilih('hetero')                 ← pakai UJI_T (BELUM ADA)
baris 1145  <script src="kartu_uji_t.js">   ← data dimuat DI SINI
```

Tag skrip ditaruh **sebelum `</body>`** → di Jinja letaknya **SETELAH**
`{% block skrip %}` → **data dimuat setelah dipakai**.

**FIX:** pindah ke **`<head>`** (skrip halaman dieksekusi di akhir `<body>`,
jadi data sudah tersedia).

> 📌 **ATURAN INDUK:** kalau kode sudah benar tapi hasil tetap salah,
> **JANGAN ubah kode lagi** — cari hal lain yang **URUTANNYA** berbeda
> (pemuatan, letak tag, blok `<script>` terpisah).
>
> Cek cepat: `grep -n "<script"` pada HTML LIVE → lihat urutan blok.

**Kesalahan Wulan:** sempat **2× mengubah kode** padahal akarnya di letak tag.
Ini kelas kesalahan "kode diubah tapi hasil identik" — petunjuk terkuat bahwa
yang salah **bukan kodenya**.

### Jebakan 2 — TAB YATIM MEMBUAT GERBANG PALSU-GAGAL

```
Gerbang : WEB — tata letak kontrol (geometri)
Gejala  : TimeoutExpired 140 detik di Chrome --dump-dom
          padahal deploy 9/10/11 gerbang ini LULUS
```

**AKAR:** **27 tab tertinggal** di sesi CDP port 9333 (**20 tab `/belajar`**
dari uji-uji hari itu). Chrome jadi lemas → `--dump-dom` tidak selesai.

**BUKTI TERUKUR:**
```
sebelum bersih : 33 proses chrome · 27 tab · /buat-data TIMEOUT
sesudah bersih : 10 proses chrome ·  0 tab · /buat-data EXIT 0 (88.982 byte)
                 gerbang geometri LULUS dalam 24,9 detik
```

**UJI TERKONTROL (untuk membuktikan bukan kode):** tag skrip baru **dimatikan
sementara** → Chrome **tetap timeout**. Jadi kode Wulan **bukan** penyebabnya.

**CEGAH:**
```bash
curl -s -m 5 http://127.0.0.1:9333/json/list | grep -c '"type": "page"'
# >5 tab → tutup: curl -s http://127.0.0.1:9333/json/close/<id>
```
**JANGAN `pkill chrome`** (aturan proyek: port 9333 jangan dimatikan paksa).

### Jebakan 3 — TANGKAPAN LAYAR CDP GAGAL DI HALAMAN TINGGI

```
Galat : RuntimeError: {'code': -32000, 'message': 'Unable to capture screenshot'}
Sebab : Page.captureScreenshot(captureBeyondViewport=True) pada halaman ~5.800px
```

**FIX:** batasi tinggi lewat `Emulation.setDeviceMetricsOverride(height=...)`
ke tinggi isi, lalu screenshot **tanpa** `captureBeyondViewport`.
**WAJIB cek** ukuran berkas >10 KB — jangan percaya "berhasil" tanpa bukti.

---

## 7. HASIL TERUKUR (halaman SUNGGUHAN, HP 390px)

| # | Uji | Hasil |
|---|---|---|
| 1 | Halaman BELAJAR termuat | ✅ |
| 2 | Skrip data kartu termuat (`UJI_T`) | ✅ 5 hasil |
| 3 | Tidak ada galat JS | ✅ 0 |
| 4 | Kartu muncul & panel kamus sembunyi | ✅ |
| 5 | Lima kotak hasil tampil | ✅ 5 |
| 6 | Tiap skenario isi sendiri | ✅ tabel 2–7 baris · cek 3–5 butir |
| 7 | Label SAH/HATI-HATI/CURANG | ✅ 3 label |
| 8 | Kepala kartu HACK merah | ✅ `rgb(168, 90, 90)` |
| 9 | Judul versi baru | ✅ "5 Cara Hack yang Harus Dihindari" |
| 10 | Tombol daftar periksa buka | ✅ tersembunyi → terbuka |
| 11 | Tombol tutup kembali | ✅ |
| 12 | Tidak meluber keluar layar HP | ✅ 0 elemen |
| 13 | Tidak ada kode tumpah | ✅ 0 kata |

**Isi per skenario (terukur — bukan satu tulisan dibagi rata):**

| Skenario | Baris tabel | Butir cek | Ada label CURANG? |
|---|---|---|---|
| sig-plus (DITERIMA) | 2 | 3 | tidak |
| **sig-minus (ADA TEMUAN)** | **7** | **5** | **ya** |
| marginal (HATI-HATI) | 5 | 5 | ya |
| tidaksig-plus | 6 | 5 | ya |
| tidaksig-minus | 4 | 4 | ya |

---

## 8. BERKAS

| Berkas | Isi | Baris |
|---|---|---|
| `app/templates/belajar.html` | kartu uji t (HTML + JS) | 1.155 |
| `app/static/kartu_uji_t.js` | **DATA** 5 hasil + 5 hack (dibangkitkan) | — |
| `_sketsa/data_uji_t.py` | **SUMBER data** ← ubah di sini, jangan edit .js manual | 264 |
| `_sketsa/css_ujit.css` | CSS kartu (digabung ke `gaya.css`) | 135 |
| `_sketsa/escape_tag_belajar.py` | auto-escape tag penutup di `<script>` | — |
| `_sketsa/render_sketsa.py` | render sketsa + potong ruang putih | 63 |
| `_sketsa/sketsa_uji_t.py` | putaran 1 (5 skenario) | 264 |
| `_sketsa/sketsa_uji_t2.py` | putaran 2 (2 tingkat) | 276 |
| `_sketsa/sketsa_uji_t3.py` | putaran 3 (3 lapis) | 480 |
| `_sketsa/sketsa_hack.py` | 3 variasi warna kartu HACK | 194 |
| `uji_kartu_ujit.py` | 13 uji halaman sungguhan | 270 |
| `app/templates/dasar.html` | pemuatan `kartu_uji_t.js` di `<head>` | 107 |

**Alur mengubah isi kartu:**
```bash
cd /opt/data/services/statistik-lab
# 1. ubah _sketsa/data_uji_t.py
.venv/bin/python _sketsa/data_uji_t.py     # bangkitkan ulang .js
.venv/bin/python gerbang_tag_skrip.py      # WAJIB: cek tag mentah
bash jalankan.sh                           # deploy (gerbang 17 grup)
.venv/bin/python uji_kartu_ujit.py         # 13 uji halaman sungguhan
```

---

## 9. PELAJARAN WULAN (jujur)

| # | Kejadian |
|---|---|
| 1 | Wulan **2× ubah kode** padahal akarnya di **letak tag** (urutan pemuatan) |
| 2 | Wulan hampir **menyalahkan alat ukur** lagi — pola yang sama seperti kasus VIF & hetero |
| 3 | Wulan **5 putaran** mengejar kode, padahal **Chrome-nya yang lemas** (27 tab) |
| 4 | Wulan **tidak sadar** miskonsepsi ke-2 sampai **Bos memancingnya** |

**Yang menyelamatkan:** Wulan **berhenti, hitung dari bukti, dan uji terkontrol**
(mematikan tag skrip untuk membuktikan bukan kode) — bukan menambal.

---

## 10. ⏭️ BELUM DIKERJAKAN

1. Format unduhan **SPSS** (nama panjang) / **PLS** (kode pendek)
2. Mode 1-model-1-jalur `/buat-data?model=…`
3. Halaman `/mulai` + `/kuantitatif` 6 kartu model bergambar
4. PERIKSA SYARAT (grafik SPSS + PLS)
5. Lapis 2 (AI) untuk judul ragu

---

## 🔒 CATATAN KREDENSIAL

Rangkaian ini **TIDAK memuat kredensial/API key apa pun**. Tidak ada token,
kata sandi, atau kunci yang dituliskan di dokumen ini.
