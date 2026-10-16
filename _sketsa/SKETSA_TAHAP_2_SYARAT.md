# 📐 SKETSA TAHAP 2 — PERIKSA SYARAT: GRAFIK HIDUP DARI DATA SUNGGUHAN

> **Status: RENCANA — belum dikoding.** Wulan susun ini dari **pembacaan utuh**
> `app/templates/syarat.html` (466 baris), `app/diagnosis.py` (505 baris), dan
> `TAHAP_PENYELESAIAN.md` Tahap 2. Bos putuskan dulu.

---

## 1. MASALAH YANG MAU DIBETULKAN

Halaman `/syarat` **sudah ada 7 grafik SVG** — tapi semuanya **DIPAKU STATIS**:

```html
<circle cx="42" cy="45" r="2.5"/><circle cx="50" cy="59" r="2.5"/>...
```

Titik-titiknya **ditulis satu per satu dengan tangan** (literal angka di HTML).
Catatan jujur di berkas itu sendiri (baris 19–21):

> *"ISI UJI: halaman ini BELUM menghitung dari data yang sedang aktif.
> Grafiknya masih contoh tetap. Sambungan ke data nyata dikerjakan setelah
> mesin di /buat-data selesai disambung."*

**Akibatnya:** mahasiswa melihat gambar "aman" terus-menerus. Tidak ada gunanya
membaca grafik, karena gambarnya **tidak pernah** berubah.

**Sebaliknya**, mesin diagnosa (`app/diagnosis.py`) **SUDAH** menghitung angka
sungguhan dari berkas yang diunggah user — lewat `/klinik`. Bahkan sudah
menyiapkan bahan gambar (baris 326–328):

```python
# Sisa mentah DIPAKAI untuk menggambar scatter ZPRED × ZRESID
# di browser — jadi grafiknya dari DATA USER, bukan contoh.
'titik': {'zpred': [...], 'zresid': [...]},
```

⇒ **Niatnya sudah ada, sambungannya belum dibuat.** Ini PERSIS semangat aturan
Bos: *"sambungkan komponen yang SUDAH ADA, jangan bangun mesin baru"*.

---

## 2. BAHAN GAMBAR YANG SUDAH TERSEDIA (TERUKUR)

Wulan jalankan mesin di atas data contoh (n=120), ini kunci yang keluar:

| Grafik | Bahan dari mesin | Keadaan |
|---|---|---|
| **Hetero** scatter ZPRED × ZRESID | `titik.zpred` (120 angka) + `titik.zresid` (120) | ✅ **SIAP** |
| **VIF** batang | `vif[].nama` + `vif[].vif` + `vif_maks` | ✅ **SIAP** |
| **PLS** outer loading | `konstruk[].muat[].butir` + `.muat` | ✅ **SIAP** |
| **PLS** AVE | `konstruk[].ave` | ✅ **SIAP** |
| **PLS** CR | `konstruk[].cr` | ✅ **SIAP** |
| **Normalitas** P-P plot | ❌ tidak ada | 🔧 **PERLU DITAMBAH** |
| **Normalitas** histogram residu | ⚠️ resid dihitung, tapi tidak dikirim | 🔧 **kirim resid** |
| **Linearitas** scatter X × Y | ❌ tidak ada | 🔧 **PERLU DITAMBAH** |

---

## 3. TAMBAHAN KECIL DI MESIN (bukan mesin baru)

Tiga tambahan, semuanya **memanfaatkan angka yang SUDAH dihitung** — cuma
belum dikirim ke halaman:

| # | Tambahan | Bahan yang sudah ada |
|---|---|---|
| 1 | `titik.zresid_urut` | `resid` sudah dihitung (baris 228) |
| 2 | `titik.pp` (P-P plot) | cukup `z_res` (sudah dihitung baris 283) → titik teoritis |
| 3 | `titik.xy` (scatter X×Y) | `d[pred]` + `d[kolom_y]` sudah jadi DataFrame di baris 214 |

**Tidak ada rumus baru** — P-P plot cuma mengurutkan z residu lalu memasangkannya
dengan nilai harapan normal ke-i `Φ⁻¹(i/(n+1))`.

---

## 4. TIGA PILIHAN CARA SAMBUNG (Bos pilih)

### ⭐ Opsi A — Grafik hidup di `/syarat`, ikut data terakhir

User mengunggah data di `/klinik`, lalu membuka `/syarat` → grafiknya **dari data
mereka sendiri**. Belum unggah → tetap contoh tetap + label jujur
*"ini contoh — unggah datamu di KLINIK untuk melihat grafikmu sendiri"*.

- ✅ Semangat "sambungkan yang sudah ada" — paling pas
- ✅ Mahasiswa melihat **grafiknya sendiri**, bukan gambar hiasan
- ⚠️ Perlu simpan data terakhir (sudah ada polanya: `data/terakhir.pkl` dipakai
  `/buat-data`)

### Opsi B — Grafik hidup di `/klinik` saja, `/syarat` tetap sebagai kamus

`/syarat` dibiarkan sebagai **kamus bacaan** (seperti sekarang), grafik hidup
hanya muncul di hasil diagnosa `/klinik`.

- ✅ Paling sedikit risiko — `/syarat` tidak disentuh
- ✅ Pembagian jelas: kamus vs alat
- ⚠️ Dua tempat harus dibuka (kurang nyaman di HP)

### Opsi C — Grafik hidup di KEDUA tempat

`/klinik` untuk data sungguhan, `/syarat` sebagai contoh tetap.

- ✅ Paling aman
- ⚠️ Pekerjaan dobel, dan Bos bilang "jangan bangun mesin baru"

---

## 5. URUTAN PENGERJAAN (kalau Opsi A)

| Langkah | Kerjaan | Bukti selesai |
|---|---|---|
| 2.1a | Tambah bahan gambar di mesin (`pp`, `xy`, `zresid_urut`) | uji mesin: 3 kunci baru ada, isinya benar |
| 2.1b | Buat fungsi gambar SVG di JS (satu fungsi per jenis grafik) | uji: SVG terbentuk, jumlah titik = n |
| 2.1c | Sambung ke `/syarat` + simpan data terakhir | buka `/syarat` → grafik dari data sendiri |
| 2.1d | Tombol **Contoh sehat / Contoh sakit** di tiap grafik | klik → gambar berubah wujud jelas |
| 2.2 | **Linearitas** scatter X × Y hidup | idem |
| 2.3 | **VIF + hetero** dirapikan (sudah jalan, tinggal disatukan) | idem |
| 2.4 | **PLS**: tabel + batang outer loading, AVE, CR | idem + ambang batas terlihat |
| 2.5 | **Pemisah jelas** mana SPSS mana PLS | mahasiswa tahu bedanya |

Tiap langkah: **gerbang uji + deploy `jalankan.sh`** (aturan proyek).

---

## 6. YANG **TIDAK** DIKERJAKAN (biar jelas)

- ❌ **Tidak** bikin mesin hitung baru — `app/diagnosis.py` sudah lengkap
- ❌ **Tidak** menghapus 7 grafik statis — dipakai sebagai **tampilan awal**
- ❌ **Tidak** menyentuh `/klinik` lebih dari yang perlu
- ❌ **Tidak** mengubah alur unggah berkas
- ❌ **Tidak** pasang Chart.js/D3 — pakai **SVG tulisan sendiri** (sesuai pilihan
  Bos, dan proyek ini sudah terbukti bisa: kamus `/belajar` & diagram model)

---

## 7. RISIKO YANG WULAN SEBUT JUJUR

| Risiko | Penanganan |
|---|---|
| Data besar (n = 5.000) → 5.000 titik SVG berat | Batasi tampil ~300 titik acak + beri tahu; angka tetap dari semua data |
| Grafik "aman" terus karena data kita memang dirancang sehat | Tombol **Contoh sakit** menyuntik data melanggar asumsi |
| `/syarat` jadi lambat kalau hitung ulang tiap buka | Simpan hasil hitung terakhir (pola `data/terakhir.pkl` sudah ada) |
| Grafik salah gambar → mahasiswa salah paham | Tiap grafik **wajib ada uji**: jumlah titik, arah corong, titik di garis |

---

## 8. YANG WULAN BUTUH DARI BOS

1. **Opsi A / B / C** — Wulan sarankan **A**.
2. Simpan data terakhir untuk `/syarat`: **pakai berkas** (pola `data/terakhir.pkl`)
   atau **hitung ulang saat halaman dibuka**?
3. Batas titik digambar: **300 titik** cukup, atau mau semua?
