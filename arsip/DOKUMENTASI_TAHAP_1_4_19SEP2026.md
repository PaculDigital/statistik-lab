# DOKUMENTASI TAHAP 1.4 — BAR "MODEL KAMU SEKARANG" (19Sep26)

> **Status: SELESAI & LIVE.** Deploy 21–22 · Gerbang utama **19 grup LULUS** ·
> `uji_bar_model.py` **32 LULUS / 0 GAGAL** · terverifikasi **mata** + **ukur**.

---

## 1. MASALAH YANG DIPECAHKAN

Halaman `/buat-data` **hanya tahu model dari alamat URL** (`?model=...`).

| Kejadian nyata | Sebelum 1.4 |
|---|---|
| User bookmark `/buat-data` | ❌ Halaman kosong — dia lupa mau model apa |
| User tutup lalu buka lagi | ❌ Harus mulai dari `/kuantitatif` lagi |
| User salah pilih model | ❌ Tidak ada jalan balik yang jelas di tengah halaman |
| User scroll jauh ke bawah | ❌ Tidak tahu lagi sedang mengerjakan model apa |

---

## 2. KEPUTUSAN BOS (19Sep26, setelah Wulan jelaskan alur)

Wulan **menjelaskan alur dulu** (sesuai permintaan Bos), menyebut **4 hal jujur**
(pekerjaan kecil · risiko menebak · belum ada login · belum diukur), lalu Bos
memberi **2 keputusan**:

| # | Pertanyaan | Pilihan Bos | Artinya |
|---|---|---|---|
| ① | Buka `/buat-data` **tanpa** pilih model → apa? | **(B)** | **Arahkan balik** ke `/kuantitatif` — JANGAN terka |
| ② | Tombol "Ganti model" ditaruh di mana? | **(A)** | **Menempel di atas** (mengikuti scroll) |

⚠️ **MENGAPA ①B, bukan "isi otomatis model terakhir"** (opsi A yang TIDAK dipilih):
tanpa login, ingatan **hanya per-browser**. Kalau mesin menebak model yang
**SALAH** lalu user tidak sadar, datanya jadi **tidak sesuai penelitiannya**.
Bahaya itu lebih besar daripada repot memilih 1 kali. (Login direncanakan Tahap 7.)

---

## 3. YANG DIBANGUN

### 3a. Bar di HTML (BUKAN dibuat dari JavaScript)
`app/templates/buat_data.html` — `<div class="bar-model" id="bar-model" hidden>`

Berisi: ikon kompas · label "**Model kamu sekarang**" · nama model (`#bar-model-nama`)
· tombol "**Ganti model**" → `/kuantitatif`.

⚠️ **SENGAJA `hidden` SEJAK AWAL.** Kalau user tidak memilih model, bar **tidak
muncul** — justru diarahkan balik (keputusan ①B).

### 3b. Keputusan ①B di JavaScript
```js
if (!slug) {
  location.replace('/kuantitatif');
  return false;
}
```
⚠️ **SENGAJA `location.replace`** (bukan `href`): **tidak menambah riwayat**
browser, jadi tombol "mundur" user tidak terjebak bolak-balik
`/buat-data` ↔ `/kuantitatif` (lingkaran tak berujung).

### 3c. Bar diisi JavaScript, bukan dibangun
Bagian 6 `terapkanJalurModel()` — **hanya** mengisi nama lalu membuang `hidden`:
```js
barNama.textContent = J.judul || slug;   // SUMBER TUNGGAL: JALUR_MODEL
bar.hidden = false;
```

### 3d. CSS di `gaya.css` (BUKAN di JavaScript)
```css
.bar-model { position: fixed; top: 0; left: 0; right: 0; z-index: 60; ... }
body:has(.bar-model:not([hidden])) .bungkus:first-of-type { padding-top: 96px; }
```

---

## 4. ⚠️ AKAR TERPENTING — KENAPA `position: sticky` GAGAL

**Ini cacat yang LOLOS semua uji DOM dan hanya ketemu dari MATA.**

### Gejala terukur
```json
ATAS  : {"top": 258,  "pos":"sticky"}
SCROLL: {"top": -1142,"pos":"sticky"}   ← bar ikut TERGULUNG
```

### Akar sejati (dibaca dari DOM, bukan dari berkas)
```
DIV.bar-model ... pos=sticky
MAIN.bungkus  ... overflow=visible
BODY          ... overflow=hidden auto   ← INI AKARNYA
```

`gaya.css` **baris 554** punya aturan **LAMA**:
```css
@media (...) { html, body { max-width: 100%; overflow-x: hidden; } }
```

**Aturan CSS:** elemen `sticky` menempel pada **scroll container terdekat**.
Begitu `<body>` jadi scroll container (`overflow-x: hidden`), sticky
**tidak lagi menempel ke viewport** — ia menempel ke body yang ikut tergulung.

### ⚖️ MENGAPA WULAN TIDAK MENGHAPUS `overflow-x: hidden`
Itu aturan **sengaja dipasang** supaya halaman **tidak bisa digeser ke samping
di HP**. Menghapusnya = **menambal satu, merusak lain** (dilarang).

**CARA AMAN YANG DIPILIH:** `position: fixed` — **tidak terpengaruh** scroll
container. Harganya: elemen `fixed` **keluar dari alur dokumen** → konten
tertutup → butuh **penyeimbang** (`padding-top` pada `.bungkus`, hanya saat bar
ada, lewat selektor `:has()`).

### UJI PENJAGA (dipasang supaya tidak menambah cacat baru)
```
✅ halaman TIDAK bisa digeser ke samping (390 ≤ 390)
```
Uji ini memastikan bar `fixed` **tidak membatalkan** aturan lama.

---

## 5. 9 CACAT DITEMUKAN & DIPERBAIKI

| # | Cacat | Cara ketemu |
|---|---|---|
| 1 | **8 ikon KOSONG** tersembunyi lama: `skull`, `clock`×3, `play-circle`, `calendar`, `history`, `message-square` | **gerbang ikon** baru → langsung ketahuan |
| 2 | `arrow-left-right` dipakai 2 tempat, **tidak ada di sprite** | cek nama **sebelum** pakai |
| 3 | `--tinta-1` **tidak ada** di CSS (adanya `--tinta`) | grep variabel dulu |
| 4 | **`position: sticky` tidak bekerja** | 👁️ vision: *"tidak ada bar"* padahal DOM bilang LULUS |
| 5 | Gerbang ikon **PALSU** — regex `ikonKecil?` salah tulis | Wulan **uji gerbangnya sendiri** → gagal menangkap |
| 6 | Uji Wulan menuntut `sticky` (usang) | 3 uji gagal padahal aplikasi benar |
| 7 | Spanduk lama ditempel di kartu `#catatan-kelayakan` | kartu itu berubah isi (VIF/R²) → bisa tertimpa |
| 8 | Gaya spanduk lama **inline di JS** → kalah spesifisitas | **inilah akar** "spanduk krem bukan hijau" |
| 9 | Spanduk lama tidak ada di DOM awal | tidak bisa diuji gerbang |

### 🚨 CACAT #5 PALING PENTING — gerbang palsu
```python
# SALAH (Wulan pertama):
r"ikonKecil?\(\s*'([a-z0-9-]+)'"
# Artinya: "ikonKecil" dengan huruf akhir `l` OPSIONAL
# → cocok `ikonKecil` / `ikonKecila`, TAPI TIDAK cocok `ikon` ❌

# BENAR:
r"(ikonKecil|ikon)\(\s*'([a-z0-9-]+)'"
```
Terukur: `ikon('ikon-palsu-xyz', 14)` **tidak tertangkap** (`re.findall` → `[]`)
padahal jelas ada. Gerbang **selalu berbunyi "semua ikon ADA"**.

**PELAJARAN:** gerbang **wajib diuji bisa GAGAL** — suntik kerusakan buatan,
harus keluar EXIT 1. Gerbang yang tidak bisa gagal = **tidak menjaga apa pun**.

---

## 6. 🔬 BUKTI — DIUKUR, BUKAN DIKLAIM

| Uji | Hasil |
|---|---|
| **Gerbang utama** (`gerbang_uji.sh`) | ✅ **19 grup SEMUA LULUS** |
| **`uji_bar_model.py`** (BARU) | ✅ **32 LULUS / 0 GAGAL** |
| └ *"2A: terbukti menempel (top=0 saat scroll)"* | ✅ terukur setelah scroll 1400px |
| └ *"1B: diarahkan ke /kuantitatif"* | ✅ |
| └ *"KLIK Ganti model → /kuantitatif"* | ✅ |
| └ *"tidak bisa digeser ke samping (390 ≤ 390)"* | ✅ tidak menambah cacat |
| **`gerbang_ikon.py`** (BARU) | ✅ 87 ikon sprite vs 86 pemakaian |
| **Vision (setelah fix)** | ✅ *"Ya, bar hijau di paling atas, rapi, ikon utuh"* |
| **Deploy 21, 22** | ✅ EXIT 0, `/health` ok |
| **SOT** | ✅ SELARAS (menangkap 18→19 grup, diperbaiki) |

### ⚠️ Pelajaran terpenting
**Membaca ATRIBUT ≠ mengukur PERILAKU.**
Versi pertama Wulan **membaca `position: sticky` dari CSS** lalu bilang
**LULUS** — padahal di halaman nyata bar **tergulung**. **MATA (vision) yang
menangkapnya.** Sekarang uji mengukur `getBoundingClientRect().top` **setelah
scroll**, bukan membaca nama properti.

---

## 7. ⚠️ BATAS JUJUR

1. **`:has()` di CSS** — kalau browser lama tidak mendukung, efeknya konten
   **sedikit tertutup** (tidak merusak). Chrome/Safari/Firefox modern aman.
2. **Belum ada login** → tidak ada ingatan lintas perangkat (memang dasar
   keputusan ①B). Login = Tahap 7.
3. **Kartu Campuran belum punya sub-pilihan** — masih langsung ke `?model=gabungan`.
4. **Tinggi bar di layar lebar (96px) belum diuji terpisah** — baru diuji di HP 390px.

---

## 8. BERKAS YANG DISENTUH

| Berkas | Perubahan |
|---|---|
| `app/templates/buat_data.html` | bar HTML (baru) · bagian 6 diganti · 1B di `terapkanJalurModel` · ikon `skull`→`gauge`, `arrow-left-right`→`refresh-cw` |
| `app/static/gaya.css` | blok `.bar-model` (baru) + penyeimbang `:has()` |
| `app/templates/kuantitatif.html` | ikon `arrow-left-right`→`refresh-cw`, `clock`→`timer` |
| `app/templates/mulai.html` | 5 ikon: `play-circle`→`play`, `calendar`→`timer`, `history`→`rotate-ccw`, `clock`→`timer`, `message-square`→`info` |
| `app/templates/syarat.html` | `clock`→`timer` |
| **`uji_bar_model.py`** | **BARU** — 32 uji bar di halaman sungguhan |
| **`gerbang_ikon.py`** | **BARU** — cek nama ikon ada di sprite |
| `gerbang_uji.py` | +2 grup (sub-pilihan & ikon) → **19 grup** |

---

## 9. PERINTAH UJI

```bash
cd /opt/data/services/statistik-lab
.venv/bin/python uji_bar_model.py     # 32 LULUS — bar di halaman sungguhan
.venv/bin/python gerbang_ikon.py      # semua nama ikon ada di sprite
bash gerbang_uji.sh                   # 19 grup, EXIT 0 = aman
```
