# 🔒 RUANG MANOVA — DIPESAN, BELUM DIKERJAKAN

> **Status: RUANG DIPESAN (19Sep26). BUKAN tugas. JANGAN dikoding tanpa Bos buka lagi.**
>
> Perintah Bos (verbatim):
> *"1. A nanti kalo sudah beres, kamu catat dulu, tapi kamu perlu siapkan ruang
> untuk manova ini, agar tidak bertumpuk dan menimpa. 2. A"*

---

## 1. KEPUTUSAN BOS

| # | Pertanyaan | Keputusan |
|---|---|---|
| 1 | Kapan MANOVA dikerjakan? | **(1a)** Dicatat dulu → dikerjakan **SETELAH gerbang model beres** |
| 2 | MANOVA dapat tempat di mana? | **(2a)** **KARTU KE-5** di `/kuantitatif` — **pintu SENDIRI**, bukan saklar di dalam Regresi |

⚠️ **MANOVA DILARANG menghentikan pekerjaan gerbang model sekarang.**

---

## 2. 🔒 4 RUANG YANG SUDAH DIPESAN

Perintah Bos: *"agar tidak bertumpuk dan menimpa."* → ruang harus **dipesan lebih dulu**.

| # | Ruang | Status | Wujud pesanan |
|---|---|---|---|
| **R1** | Slot kartu ke-5 di `/kuantitatif` | ✅ **SUDAH DISIAPKAN** | Kelas CSS `.pintu.lebar-penuh` di `app/static/gaya.css` |
| **R2** | Kode model di URL | 🟡 **DIPESAN (nama dikunci)** | `?model=banding-kelompok` |
| **R3** | Berkas mesin | 🟡 **DIPESAN (nama dikunci)** | `app/hitung/manova.py` |
| **R4** | Kolom "kelompok" di data | 🔴 **SENGAJA DITAHAN** | JANGAN ditambah ke format data sekarang |

### R1 — SUDAH DISIAPKAN (19Sep26)

**TERUKUR kenapa perlu:**
```css
.grid-jenis { grid-template-columns: repeat(2, minmax(0, 1fr)); }   /* gaya.css:803 */
```
Grid **terkunci 2 kolom**. Kalau kartu ke-5 ditambahkan begitu saja →
dia **MENGGANTUNG SENDIRIAN di kiri** (tampak pincang/rusak).

**Wujud pesanan** (baris 806–817 `app/static/gaya.css`):
```css
/* ⚠️ RUANG DIPESAN 19Sep26 — untuk KARTU KE-5: BANDING KELOMPOK (MANOVA).
   Perintah Bos: "kamu perlu siapkan ruang untuk manova ini..."
   ⚠️ JANGAN hapus kelas ini walau belum dipakai. */
.pintu.lebar-penuh {
  grid-column: 1 / -1;
}
```
✅ Belum dipakai halaman mana pun — **sengaja disiapkan**.
✅ Kurung CSS terverifikasi seimbang (383 buka / 383 tutup).

**Cara pakai nanti:** `<a class="pintu lebar-penuh" href="/buat-data?model=banding-kelompok">`

### R4 — INI YANG PALING PENTING (jangan dilanggar)

Format data mesin sekarang:
```python
{'item': {nama: ndarray2D}, 'skor_konstruk': {nama: ndarray}}
```

**MANOVA butuh kolom "kelompok"** (mis. 1=Pria, 2=Wanita). Regresi **tidak butuh**.

🔴 **JANGAN menambah kolom kelompok ke format ini sekarang.**
Alasannya: format data dipakai **17 grup gerbang**. Menambah kolom = **menyentuh semua uji lama**.
Perintah Bos: *"agar tidak bertumpuk dan menimpa."*

**Jalan yang benar nanti:** kolom kelompok dibuat **terpisah**, hanya saat MANOVA dipilih
(mis. `buat_data(..., kelompok=True)`), **tanpa mengubah** bentuk data yang sudah ada.

---

## 3. HASIL CEK MESIN (19Sep26) — TERUKUR, BUKAN DUGAAN

| Hal | Keadaan |
|---|---|
| Kata `manova`/`wilks`/`pillai`/`hotelling` di `app/` | ❌ **KOSONG** — tidak ada satu pun |
| Yang ADA | hanya regresi (`regresi_terstandar`, `sk_regresi`) |
| Bahan mentah MANOVA | ✅ **LENGKAP** — numpy sanggup |
| Wilks Lambda (uji coba) | ✅ **terhitung 0,4312** pada 3 kelompok × 2 Y |
| Mesin Y ganda | ✅ **BISA** — 2X→2Y galat 0,0041 · 2X→3Y 0,0038 · 2X→4Y 0,0067 |

**Kesimpulan jujur:** MANOVA **BELUM BISA**, tapi **bisa dibangun** — tinggal ditulis
(perkiraan Wulan: 1 berkas + 1 berkas uji — belum diukur, jadi belum janji).

---

## 4. YANG PERLU DIBANGUN (daftar kerja nanti)

| # | Bagian | Bahan | Kesulitan (perkiraan) |
|---|---|---|---|
| 1 | Hitung SSCP (jumlah kuadrat & silang) | ✅ ada | ⭐ |
| 2 | Wilks' Lambda | ✅ terbukti | ⭐ |
| 3 | Pillai's Trace | ✅ bahan sama | ⭐ |
| 4 | Hotelling-Lawley | ✅ bahan sama | ⭐⭐ |
| 5 | Roy's Largest Root | ✅ bahan sama | ⭐⭐ |
| 6 | Konversi ke F & p-value | ✅ rumus baku | ⭐⭐ |
| 7 | Uji lanjutan per-Y (ANOVA) | ✅ bahan sama | ⭐ |
| 8 | Uji asumsi (Levene, **Box's M**) | ✅ bahan sama | ⭐⭐ |
| 9 | Kalimat kesimpulan otomatis | — | ⭐⭐ |
| 10 | **Kolom "kelompok" di pembuat data** | 🔴 ditahan | ⭐⭐ |

⚠️ **Bagian 8 & 9 WAJIB** — MANOVA yang tidak memeriksa syarat = **MANOVA yang menyesatkan**.
Syarat: normal multivariat · varians-kovarians sama antar kelompok (Box's M) · tidak ada pencilan.

---

## 5. MANOVA ≠ SOFTWARE (catatan penting untuk bahan ajar nanti)

| | Contoh | Apa itu |
|---|---|---|
| **SPSS** | Warung makan | **TEMPAT** kamu pesan |
| **Regresi, MANOVA, uji t** | Nasi goreng, soto | **MENU** yang ada di warung itu |

**MANOVA = ANALISIS (menu). SPSS = SOFTWARE (warung).**
Di SPSS: `Analyze → General Linear Model → Multivariate`.

👉 Tujuan akhir proyek ini (arahan Bos): **mahasiswa tahu pilih SPSS atau SmartPLS.**
Kita **bukan menyaingi SPSS** — kita **guru + pembuat bahan latihan.**

---

## 6. MASUK vs KELUAR — dua-duanya (penegasan Bos 19Sep26)

```
MASUK   → mesin MEMBANGUN data (termasuk kolom kelompok kalau MANOVA)
KELUAR  → mesin MENGUJI & memberi kunci jawaban ("Wilks=0,43 · p=0,002")
```

Ini **pola yang SUDAH JALAN** sejak awal (regresi: bangun data + "β terbaca").
MANOVA hanya menambah **2 hal**: kolom kelompok (masuk) + Wilks (keluar). **Sisanya sudah ada.**

---

## 7. MANOVA = CARA BERPIKIR BERBEDA

```
REGRESI  :  "X memengaruhi Y"          → arah pengaruh
MANOVA   :  "Kelompok A ≠ Kelompok B"  → beda rata-rata
```
Analogi:
- **Regresi** = *"seberapa kuat cinta memengaruhi kebahagiaan?"*
- **MANOVA** = *"menikah vs lajang, beda kebahagiaannya?"*

**Kalau dibangun, MANOVA membuka pasar baru:** penelitian **eksperimen** &
**komparatif** (banding 2 kelas, Pria vs Wanita) — bukan cuma survei.
Karena itu MANOVA **tidak bisa** jadi saklar di dalam Regresi → benar keputusan Bos: kartu ke-5.

---

## 8. ANAK TANGGA SETELAH MANOVA (catat, JANGAN dikerjakan)

| Bentuk | Isi | Status |
|---|---|---|
| MANOVA satu arah | 1 faktor, ≥2 kelompok, ≥2 Y | ❌ belum |
| MANOVA faktorial | 2 faktor atau lebih | ❌ belum |
| MANCOVA | MANOVA + kontrol variabel (kovariat) | ❌ belum |
| MANOVA pengukuran berulang | Y diukur beberapa waktu | ❌ belum |

---

## 8b. KEPUTUSAN BOS — MODEL BESAR: OTOMATIS (19Sep26)

Bos (verbatim): *"1. A ya semuanya hitung otomatis, user hanya isi seperlunya saja, dan range beta sudah di tentukan mesin. Tinggal user pilih output data math atau natural atau campuran seperti diawal"*

| # | Keputusan | Isi |
|---|---|---|
| 8 | **Cara mengisi β di model besar** | **(1a)** **SEMUA DIHITUNG OTOMATIS** — mesin yang mengisi |
| 9 | **User isi apa saja** | **HANYA SEPERLUNYA** — bukan semua kotak β |
| 10 | **Range β** | **DITENTUKAN MESIN** (bukan user) |
| 11 | **Yang user pilih** | **Mode output**: 🎯 **MATEMATIS (presisi)** · 🌿 **NATURAL** · 🔀 **CAMPURAN** — sama seperti di awal |

**Kata kunci Bos: *"user hanya isi seperlunya saja"*** — inilah prinsip UI model besar.

### Apa yang "seperlunya"?

```
USER lakukan:                          MESIN lakukan:
  ① pilih model (kartu bergambar)        ④ isi β semua jalur (dalam range wajar)
  ② beri NAMA variabelnya                ⑤ periksa kelayakan (R², VIF, batas β)
  ③ tunjuk panah "siapa → siapa"         ⑥ hitung & kalibrasi
     (tambah X / M / Z / Y seperlunya)   ⑦ tampilkan hasil + tafsir
  ⑧ pilih mode output (matematis/
     natural/campuran)
```

**User TIDAK PERNAH melihat 14 kotak β.** Itu pekerjaan mesin.

### Hubungan dengan komponen yang SUDAH ADA (jangan bangun baru)

| Komponen | Sudah ada? | Perannya di model besar |
|---|---|---|
| Tombol **"Setel angka wajar"** | ✅ **SUDAH ADA** di `/buat-data` | Ini yang mengisi β otomatis |
| **Pagar kelayakan** (`kelayakan.py`) | ✅ sudah dipanggil | Batas R² & VIF |
| **Batas β total** (`BATAS_BETA_RANTAI=1.20`) | ✅ satu sumber | Batas range β |
| **2 mode** (presisi/natural) | ✅ sudah ada | + **CAMPURAN** (gabungan keduanya) |

⚠️ **"CAMPURAN" (math + natural) = MODE BARU** — belum ada di mesin. Perlu dirancang:
apa yang matematis, apa yang natural, dan bagaimana user tahu bedanya.

### ⚠️ 2 HAL YANG BELUM TERPECAHKAN

1. **"Output data math" = 🌿 NATURAL?/🎯 PRESISI** — ✅ **SUDAH DIJAWAB BOS 19Sep26**:
   *"Output data math itu maksud nya presisi di istilah mesin, maaf saya salah sebut."*
   ⇒ **"MATH" = istilah mesin `presisi`** — satu hal, bukan dua. **TIDAK ada mode baru.**
   Yang ada di mesin (terukur, `app/berkas_kerja.py` baris 78/187/189/314):
   `natural` · `presisi` · **`presisi_variasi`** (koefisien tetap, p digeser derau =
   yang Bos sebut **"campuran"**).
   ⇒ **KETIGA MODE YANG BOS MAU SUDAH ADA DI MESIN.** Tidak perlu bangun mode baru.
2. **Range β otomatis** — ✅ **SUDAH DIJAWAB BOS 19Sep26**: **PROPORSIONAL**.
   Mengikuti pola model (X→M dan M→Y beda besarannya), **bukan rata**.
   Dipilih karena **lebih mirip data lapangan nyata**.

---

## 8d. 🔒 RINGKASAN FINAL — BAHASAN MANOVA & MODEL SELESAI (19Sep26)

Bos: *"Sudah diskusi tentang MANOVA selesai, kamu update catatan dan memori"*

| Pertanyaan | Jawaban Bos | Catatan |
|---|---|---|
| 4 kartu induk → sub-pilihan? | **1a** ✅ | user lihat 4 dulu |
| Istilah + terjemahan? | **2a** ✅ | istilah BESAR, terjemahan kecil |
| Tambah M/Z pakai tombol? | **3a** ✅ | tombol + tulis istilah (M)/(Z) |
| Berganda-berantai masuk mana? | **REGRESI** ✅ | — |
| Kapan MANOVA dikerjakan? | **1a** ✅ | setelah gerbang model beres |
| MANOVA di mana? | **2a** ✅ | KARTU KE-5 di `/kuantitatif` |
| Siapkan ruang MANOVA? | **WAJIB** ✅ | R1 sudah dipasang · R4 ditahan |
| Cara isi β model besar? | **1a** ✅ | otomatis, user isi seperlunya |
| Range β? | **PROPORSIONAL** ✅ | ikut pola model |
| Mode output? | **presisi · natural · campuran** ✅ | ketiganya SUDAH ADA di mesin |
| "Math" = apa? | **presisi** ✅ | Bos salah sebut, sudah diklarifikasi |

### KESIMPULAN BESAR

> **Mesin BISA menambah X, menambah Y, DAN mediasi + moderasi sekaligus.**
> Terbukti: 3 X · 2 M · 2 Y · 1 Z = **14 jalur, galat 0,0222, 14/14 TEPAT.**
>
> **Yang belum ada = PINTU (UI), bukan mesin.** Itu masuk Tahap 1.3.

### STATUS: 🟢 BAHASAN DITUTUP — BUKAN TUGAS

**MANOVA & gerbang model = DISKUSI SELESAI.** Disimpan sebagai catatan.
**DILARANG dikoding** sampai Bos membuka lagi.

**Yang TETAP JALAN (tidak diganggu bahasan ini):** Tahap 1.3 — buka 10 bentuk model ke UI.

---

## 8c. HASIL UKUR — GABUNGAN BESAR TERBUKTI BISA (19Sep26)

Diuji langsung lewat `kalibrasi_per_jalur` — **model paling rumit yang pernah dicoba**:

```
3 X  →  2 M  →  2 Y   +  Z (penguat) di 2 jalur  =  14 jalur
```

| Yang diukur | Hasil |
|---|---|
| Tercapai | ✅ **True** |
| Galat maks | **0,0222** |
| Jalur tepat | **14 dari 14** ✅ |

Rincian (minta → dapat): X1→M1 0,40→0,400 · X3→M2 0,30→0,300 · M1→Y1 0,35→0,328 ·
M2→Y2 0,30→0,286 · **M1×Z→Y1 0,15→0,148** · **M2×Z→Y2 0,12→0,116** · Z→Y1 0,10→0,098.

**KESIMPULAN: mesin BISA menambah X, menambah Y, DAN mediasi + moderasi sekaligus.**
Mesin tidak punya batas "jenis" — ia menerima **daftar jalur**.
Mesin berkata: *"Sebutkan siapa memengaruhi siapa"* — bukan *"pilih satu dari 10 model"*.

### 4 BATAS JUJUR (jangan disembunyikan)

1. **Batas β (total ≤1,20)** sudah terukur di S3 — **tapi BELUM diuji untuk bentuk gabungan besar ini**.
   Bisa jadi batasnya lebih ketat. Uji di atas memakai β 0,10–0,40 (kecil).
2. **MANOVA + mediasi + moderasi + Y ganda = BELUM diuji** (kolom kelompok belum ada).
   ✅ mediasi + moderasi + 2 Y → terbukti · ❓ + KELOMPOK → belum.
3. **UI = masalah sebenarnya, bukan mesin.** 14 kotak β di layar HP = mimpi buruk.
   **Belum dirancang sama sekali** → inilah yang dijawab keputusan Bos #8–11 di atas.
4. Dua M paralel butuh derau otomatis (sudah ada di mesin, terbukti: selisih 0,022).

---

## 9. CELAH BELUM TERPECAHKAN (jujur)

1. **Letak kartu ke-5 di layout** — sudah disiapkan kelas CSS-nya (R1), tapi **tata letak akhir belum dirancang**.
2. **Bagaimana user memilih kelompok** — dari kolom apa? Perlu rancangan form.
3. **Data kelompok dibuat dari mana** — disimulasikan (mesin bangun) atau diunggah user?
4. **Batas β (total ≤1,20)** berlaku juga untuk MANOVA? Belum diuji.
5. **MANOVA + kedalaman visual (grafik rata-rata kelompok)** belum dirancang.

---

## 10. CARA BALIK KE BAHASAN INI

Bos cukup bilang: **"lanjut bahasan MANOVA"** / **"buka ruang MANOVA"**.
Wulan akan baca berkas ini + `FLAG_LANJUT_DISINI.md`, lalu lanjut dari sini.

**Berkas terkait:**
- `CATATAN_DISKUSI_GERBANG_MODEL_Y_GANDA.md` — keputusan gerbang model (4 kartu, Y ganda)
- `RANCANGAN_SEMUA_MODEL_DI_WEB.md` — peta 10 bentuk mesin vs pintu web
- `CATATAN_DISKUSI_VALIDITAS_12_UJI.md` — 27 uji kuantitatif
- `TAHAP_PENYELESAIAN.md` — peta jalan 7 tahap
