# CATATAN BUG — Buat Data (Statistik Lab) · 22 Okt 2026

Ditemukan Wulan saat mereview update Bos di branch `agen/wulan/meja-kerja-baru`
(`890ae05`, `dbc496f`). **BELUM DIPERBAIKI** — menunggu perintah Bos.

---

## 🔴 BUG-1 · Unduhan GAGAL pada kunjungan PERTAMA (P0)

**Gejala terukur (container uji, `172.17.0.7:8000`):**

```
POST /api/buat-data   (request #1)  -> 200  ✅  (cookie sl_sesi dipasang di response)
GET  /api/unduh       (request #2)  -> 404  ❌  {"detail":"Belum ada data. Buat dulu."}
POST /api/buat-data   (request #3)  -> 200  ✅
GET  /api/unduh       (request #4)  -> 200  ✅  693 byte
```

**Bukti di disk container:**
```
/app/data/terakhir.pkl                              <- data PERTAMA (slot bersama)
/app/data/terakhir_3e67dca47e47472bab498c174a20ef1b.pkl  <- data KEDUA (slot sesi)
```

**AKAR (sudah dibaca kodenya, bukan tebakan):**

Middleware `_pasang_sesi` di `app/main.py` memasang cookie **SESUDAH** handler selesai:

```python
request.state.sesi = sesi if disajikan else None   # request #1: None (cookie belum ada)
response = await call_next(request)                # <- handler jalan, simpan_terakhir(None)
if not disajikan:
    response.set_cookie('sl_sesi', uuid4().hex, ...)  # <- cookie BARU dipasang di sini
```

Karena itu pada request pertama `request.state.sesi = None` sehingga
`simpan_terakhir(d, sesi=None)` menulis ke **slot bersama** (`terakhir.pkl`).
Request berikutnya sudah membawa cookie → `ambil_terakhir(sesi='3e67...')`
mencari `terakhir_3e67....pkl` yang **belum pernah dibuat** → 404.

**Dampak ke mahasiswa:** buka halaman → buat data → klik unduh → ditolak
"Belum ada data. Buat dulu." Harus membuat data **dua kali**. Ini LEBIH BURUK
dari perilaku lama (dulu selalu berhasil walau bisa tertukar saat ramai).

**Perbaikan yang diusulkan (2 pilihan, belum dikerjakan):**
- **A (akar, disukai Wulan):** middleware membuat kode sesi **sebelum** handler
  (`request.state.sesi = sesi or uuid4().hex`), lalu cookie ditulis di response.
  Data pertama langsung masuk slot sesi yang benar.
- **B (cadangan):** tulis ke slot sesi **dan** slot bersama. Lebih aman, tapi
  menyisakan berkas sampah & dua sumber kebenaran.

**Status:** ⛔ BELUM diperbaiki. Menunggu keputusan Bos (siapa yang menambal).

---

## 🟡 BUG-2 · Berkas sesi menumpuk tanpa batas jumlah (P2)

`_sapu_sesi_lama()` hanya menghapus `terakhir_*.pkl` berumur **> 7 hari**,
dan hanya jalan **1 jam sekali** (`_SWEEP['waktu']`). Tidak ada batas
**jumlah** berkas. Kalau 1.000 mahasiswa memakai dalam 7 hari, ada 1.000
berkas `.pkl` (~5 KB/berkas ≈ 5 MB) — belum mendesak, tapi perlu dipantau.

**Status:** ⛔ BELUM diperbaiki (dicatat saja).

---

## 🟡 BUG-3 · `_TERAKHIR_PER_SESI` di memori tumbuh tanpa batas (P2)

`simpan_terakhir()` menyimpan `_TERAKHIR_PER_SESI[k] = d` ke dict memori
global untuk **setiap** sesi, dan **tidak pernah** menghapus entri lama.
Pada `dbc496f`, `ambil_terakhir()` sudah benar membaca berkas lebih dulu
(memori hanya cadangan), jadi dampaknya **hanya memori** — tapi dict ini
tumbuh terus selama container hidup.

**Status:** ⛔ BELUM diperbaiki (dicatat saja).

---

## ✅ Yang TERBUKTI BENAR dari update Bos

| Hal | Bukti |
|---|---|
| CSV pemisah `;` dari halaman | `buat_data.html` menambah `?pemisah=;`; server **sudah** mendukung (`app/main.py:1513/1532`, `berkas_kerja.py:1319`) |
| Server menolak pemisah aneh | nilai selain `,`/`;` dikembalikan ke `,` (`main.py:1532`) |
| Unduhan tidak basi (890ae05) | `ambil_terakhir()` baca berkas dulu, cache memori hanya cadangan |
| Sesi memisah simpanan | `terakhir_<sesi>.pkl` benar-benar dibuat pada request kedua |
| Cookie aman | `HttpOnly; Max-Age=2592000; SameSite=lax; Secure` saat HTTPS |
| Klien tanpa cookie | jatuh ke slot bersama (perilaku lama, tidak lebih buruk) |
| Tulis atomik | `os.replace(tmp, berkas)` — unduhan bersamaan tidak baca berkas setengah jadi |

---

## Catatan metode uji (agar tidak mengulang kesalahan)

Skrip uji: `/opt/data/_uji_berkas/_uji_buatdata.py`.
Dua kesalahan Wulan saat menyusunnya (SUDAH dibetulkan, bukan bug aplikasi):
1. Payload `/api/buat-data` ditebak (`x`/`y` berupa daftar nama) → HTTP 400.
   Bentuk ASLI: `n`, `x` (jumlah X), `beta` (daftar), `skala`, `alpha`,
   `mode`, `nama_x`, `cara`. Dibaca dari `app/main.py:1120-1133`.
2. Mengira `/api/unduh` 404 = bug. Ternyata 404 itu **akibat** BUG-1
   (sesi belum nyambung), bukan rute hilang. Rute ada di `app/main.py:1511`.
