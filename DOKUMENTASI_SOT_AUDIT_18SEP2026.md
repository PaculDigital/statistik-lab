# DOKUMENTASI — SOT & AUDIT MESIN (18 Sep 2026)

**Konteks:** arahan Bos — *"Update dokumentasi, script, dan skill dulu agar jelas
gak salah salah lagi serta tetap prinsip SOT single source of truth dulu"*.

Berkas ini mencatat **APA yang ditemukan**, **AKAR-nya**, dan **ATURAN BARU**
supaya kesalahan yang sama tidak terulang.

---

## 1. MASALAH YANG DIPECAHKAN

| Masalah | Akibat |
|---|---|
| Dokumen & kode **berbeda** (mis. "5 grup uji" padahal ada 17) | Wulan salah menjawab pertanyaan Bos |
| Angka penting **dihafal**, bukan dihitung | Cepat basi, tiap sesi harus diaudit ulang |
| **Tidak ada alat** untuk tahu keadaan terkini | Wulan mengandalkan ingatan → menebak |
| Jebakan (file://, ukur kotak vs kata, item_per bawaan) **hanya di memory** | Mudah hilang saat konteks terpotong |

---

## 2. SOLUSI: `sot.py` — SATU PINTU INFORMASI

**Prinsip (arahan Bos):** sumber kebenaran = **KODE DI DISK**. Dokumen = salinan.

```bash
.venv/bin/python sot.py            # cetak ringkasan (dihitung dari kode)
.venv/bin/python sot.py --periksa  # + periksa dokumen selaras kode (EXIT ≠ 0 kalau tidak)
.venv/bin/python sot.py --json     # keluaran mesin
```

**Yang DIHITUNG dari kode, bukan dihafal:**

| Informasi | Cara mendapatkannya |
|---|---|
| Jumlah grup gerbang | `len(re.findall(r'^\s{4}\(', gerbang_uji.py))` |
| Bentuk model yang terbukti | daftar + galat (dari `audit_mesin.py`) |
| Kartu pilihan di web | `re.findall(r'data-cara="([a-z]+)"', buat_data.html)` |
| Sisa bug `item_per=4` | pindai `app/hitung/*.py` |
| Klaim usang di dokumen | pola regex (`30-500`, `78 asersi`, `5 grup`) |

**Sudah jadi GERBANG UJI NOMOR 1** — di `gerbang_uji.py`:
```python
("SOT — dokumen selaras dengan kode", "sot.py", "--periksa"),
```
**Kenapa paling awal:** kalau dokumen berbohong, uji lainnya tidak ada artinya.

---

## 3. 🚨 BUG BESAR YANG DITEMUKAN AUDIT INI

### `item_per` diambil dari NILAI BAWAAN, bukan dari DATA

```python
# SALAH (lama) — di 3 berkas:
rl = dict(bolong_persen=0.02, ..., skala=5, item_per=4)   # ← BAWAAN 4
item_per = int(rl["item_per"])
item[rng.choice(nama)][r, rng.integers(0, item_per)] = -1  # ← indeks bisa kena 3
```

**Akibat:** kalau pemanggil memakai `item_per=3` (seperti skenario moderasi),
indeks acak naik ke 3 → kolom ke-4 tidak ada →
`IndexError: index 3 is out of bounds for axis 1 with size 3`.

**Kenapa TERSEMBUNYI BERHARI-HARI:**
> **SEMUA uji lama memakai `item_per=4`** (nilai bawaan). Jadi bug tidak pernah
> muncul. Yang kena hanya **4 bentuk moderasi** — dan tidak ada yang tahu.

**Berkas yang diperbaiki:** `berurutan.py:217` · `generator.py:251` ·
`struktural.py:210`

**PERBAIKAN:**
```python
_lebar = [int(v.shape[1]) for v in item.values() if v.ndim == 2]
_bawaan = int(rl.get("item_per") or 0) or (modus(_lebar) if _lebar else 4)
item_per = min(_bawaan, max(_lebar)) if _lebar else _bawaan
rl["item_per"] = item_per
# + pemilih variabel hanya memilih yang PUNYA kolom selebar item_per
```

**Hasil:** moderasi **0/4 LULUS → 4/4 LULUS**. Total audit **10 LULUS / 0 GAGAL**.

> ### 📌 ATURAN BARU
> **JANGAN percaya nilai bawaan — UKUR dari data.**
> Nilai bawaan yang dipakai berhari-hari membuat bug **tak terlihat** karena
> semua uji memakai nilai yang sama.

---

## 4. JEBAKAN PENGUKURAN (3 kesalahan Wulan dalam satu malam)

| # | Kesalahan | Akibat | Pelajaran |
|---|---|---|---|
| 1 | Ukur **KOTAK** `<span>` ala grid-item | kotak selalu selebar kolom → "sudah benar" **PALSU** | Ukur **KATA** di dalamnya (`document.createRange()`) |
| 2 | Buka halaman lewat **`file://`** | `<link href="/static/gaya.css">` → CSS **tidak termuat** → `display:inline` **PALSU** | **Suntik CSS-nya**; ukur dari halaman **sungguhan** |
| 3 | Tandai **pemisah `·`** sebagai "teks menempel" | Gerbang **memblokir deploy** dengan temuan palsu | Gerbang harus **abaikan elemen yang MEMANG rapat** |

> ### 📌 ATURAN BARU
> **MENGUKUR, BUKAN MENEBAK.** Ukur dari halaman sungguhan + tanya **CSSOM**
> aturan mana yang menang. Alatnya: `periksa_halaman_sungguhan.py`.

---

## 5. AKAR CSS YANG AKHIRNYA KETEMU

**Masalah Bos:** kartu "Bagaimana X diuji ke Y?" — radio button di tengah atas,
teks terpusat, kartu boros (96px).

**Akar:** **spesifisitas menang atas urutan.**
```css
.medan label  { display: flex; align-items: center }   /* 0,1,1 */
.pilih-cara   { display: block; text-align: left }     /* 0,1,0 → KALAH */
```
`:pilih-cara` adalah `<label>` **di dalam `.medan`** → `.medan label` menang
walau `.pilih-cara` ditulis **belakangan**.

**Fix:** naikkan jadi **`label.pilih-cara`** (0,1,2) → menang.
Hasil terukur: `display=flex; flexDirection=row` · `textAlign=left` ·
radio di **kiri** · tinggi **62px** (dari 96px) ✅

**Juga ditemukan:** `overflow-wrap: anywhere` pada `h1,h2,h3,p,label,span`
membuat browser boleh **memotong kata di mana saja** → `Tampilkan` jadi
`Tampilk`+`an`, angka `1`/`8` terpotong. Fix: `break-word` + larangan potong
untuk angka.

---

## 6. HASIL AKHIR SESI INI

| Uji | Hasil |
|---|---|
| `audit_mesin.py` (10 bentuk model) | **10 LULUS / 0 GAGAL** (galat maks 0,0258) |
| `gerbang_uji.py` (17 grup) | **SEMUA LULUS**, EXIT 0 |
| `sot.py --periksa` | **SOT SELARAS**, EXIT 0 |
| `periksa_halaman_sungguhan.py` | slider ✅, kartu ✅ (terukur dari halaman LIVE) |

**Berkas baru 18Sep26:** `sot.py` · `audit_mesin.py` ·
`periksa_halaman_sungguhan.py` · `ukur_posisi_slider.py` ·
`RANCANGAN_SEMUA_MODEL_DI_WEB.md` · `DOKUMENTASI_SOT_AUDIT_18SEP2026.md`

**Berkas diperbaiki:** `berurutan.py` · `generator.py` · `struktural.py`
(bug `item_per`) · `gaya.css` (kartu + `overflow-wrap`) · `buat_data.html`
(kartu bisa diketuk, label slider) · `gerbang_slider.py` · `gerbang_teks_terpotong.py`

---

## 7. URUTAN KEKUATAN SUMBER (SOT)

| # | Sumber | Sifat |
|---|---|---|
| 1 | **Kode di disk** | **KEBENARAN** |
| 2 | `MASTER_PLAN.md` | salinan — keputusan terkunci |
| 3 | `FLAG_LANJUT_DISINI.md` | salinan — posisi kerja |
| 4 | skill `statistik-lab` + `references/` | salinan — cara kerja |
| 5 | memory / fact_store | salinan — pengingat |

**Kalau dokumen berbeda dengan kode → KODE YANG MENANG, dokumen diperbaiki.**
Alat pemeriksa: `sot.py --periksa`.
