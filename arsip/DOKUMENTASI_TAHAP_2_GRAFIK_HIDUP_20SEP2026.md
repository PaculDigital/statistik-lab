# 📊 DOKUMENTASI TAHAP 2.1 — GRAFIK HIDUP + TAB "BACA GRAFIK"

**Tanggal:** 20 September 2026
**Status:** ✅ **lolos gerbang — 31 grup EXIT 0** · ⛔ **BELUM DEPLOY** (menunggu ACC Bos)
**Ruang lingkup:** 7 grafik SVG statis di `/syarat` → **grafik hidup** di `/klinik` + tab ke-3 BELAJAR

---

## 1. MASALAH YANG DIPECAHKAN

| # | Masalah nyata | Akibat ke mahasiswa |
|---|---|---|
| ① | ` /syarat` punya **7 grafik SVG statis** — sama untuk semua orang | grafik tidak bicara apa-apa tentang data mahasiswa sendiri |
| ② | `/syarat` dan `/klinik` = **dua pintu yang membingungkan** | mahasiswa tidak tahu harus ke mana |
| ③ | mahasiswa harus **punya data sendiri dulu** sebelum bisa belajar membaca grafik | yang belum punya data tidak bisa latihan |

**Keputusan Bos 19Sep26 (langkah 3A) + 20Sep26:** satu jalur, dua peran jelas —
**BELAJAR = KAMUS** (tab ke-3 **"Baca Grafik"**), **KLINIK = ALAT**.
`/syarat` **dialihkan**, bukan dihapus (banyak tautan menuju ke sana).

---

## 2. YANG BERUBAH (di mata mahasiswa)

| # | Sebelum | Sesudah |
|---|---|---|
| ① | 7 grafik statis di `/syarat` | **grafik hidup** di `/klinik`, dihitung dari data yang diunggah |
| ② | 2 pintu bingung | BELAJAR tab ke-3 **"Baca Grafik"** (7 kartu bacaan) · `/syarat` → **308** → `/belajar#tab-3` |
| ③ | harus punya data dulu | **2 tombol contoh** di Langkah 2: *Contoh sehat* / *Contoh bermasalah* → kolom X1·X2→Y terisi otomatis |
| ④ | menu **8** pintu | menu **7** (KAMUS GRAFIK keluar — tidak ada dua pintu) |

---

## 3. ARSITEKTUR

```
app/diagnosis.py          → MESIN: menambah `titik` = {zpred, zresid, pp, hist, xy}
                            (memakai angka yang SUDAH dihitung — tidak ada rumus statistik baru)
app/static/grafik_hidup.js → FUNGSI GAMBAR: SVG dari data
                            petakan() · indeksSebar() · ambilPada() · bingkaiSvg()
                            svgHetero() · svgPP() · svgHistogram() · svgLinear()
                            kotakGrafik() · catatanTitik() · BATAS_TITIK = 500
app/templates/dasar.html   → memuat grafik_hidup.js di <head>  ← WAJIB di <head>
app/templates/diagnosis.html → grafik di bawah tabel angka + 2 tombol contoh
app/templates/belajar.html  → tab ke-3 "Baca Grafik" (7 kartu dari /syarat)
app/main.py                 → /syarat dialihkan 308 → /belajar#tab-3 · menu 8 → 7
```

### ⚠️ `grafik_hidup.js` WAJIB di `<head>`

`<script src>` yang ditaruh **sebelum `</body>`** jatuh **SETELAH `{% block skrip %}`** →
fungsi gambar belum dikenal saat skrip halaman jalan → **halaman MATI SENYAP**.
Pola ini sudah terekam 18Sep26; sekarang diikuti.

---

## 4. BUKTI TERUKUR (5 lapisan, semua EXIT 0)

| Lapisan | Uji | Hasil |
|---|---|---|
| **Mesin** | `uji_bahan_gambar.py` | **33 LULUS** |
| **Fungsi gambar** | `uji_grafik_hidup.js` (Node) | **24 LULUS** · corong **1,3× lebih lebar** |
| **Halaman `/klinik`** | `uji_web_grafik.py` | **18 LULUS** (unggah → periksa → SVG tergambar) |
| **Jalur mahasiswa + tab** | `uji_tab_baca_grafik.py` | **16 LULUS** |
| **Uji gambarnya sendiri** | `uji_alat_ukur_grafik.py` | **22 LULUS** + **terbukti BERGIGI** |
| **Gerbang penuh** | `bash gerbang_uji.sh` | **31 GRUP · EXIT 0** |
| **SOT** | `.venv/bin/python sot.py --periksa` | **SELARAS** |

---

## 5. CACAT NYATA YANG DITEMUKAN & DITUTUP DI AKAR

| # | Cacat | Akar jujur | Bahaya |
|---|---|---|---|
| ① | `skala()` **salah rumus** | Dua makna beda dalam satu nama (`dari` = nilai data, `ke` = koordinat tujuan) → rumus kacau, tidak ketahuan saat dibaca | 200 titik jatuh di x=9…26 padahal bingkai 34…300 → **titik TUMPAH keluar** |
| ② | pasangan titik **tertukar** | `sebar()` dipanggil **terpisah** untuk zpred & zresid → titik ke-7 berasal dari baris data BERBEDA | gambar omong kosong yang **kelihatan masuk akal** — jenis paling berbahaya (lolos dari mata) |
| ③ | **`n is not defined`** | **BUG LAMA**, ada di cadangan baris 400 **SEBELUM Tahap 2**: `const n = d.normalitas` ada di dalam blok SPSS (TDZ) → error ditelan `catch` | halaman **mati** setiap habis unggah; mahasiswa cuma lihat *"Koneksi ke server terputus"* |
| ④ | `#}` sebagai penutup **komentar JS** | Wulan menyalin gaya komentar Jinja (`{# #}`) ke dalam JavaScript | **1 komentar tak tertutup → SELURUH 26.716 byte skrip MATI** (HTTP 200, konsol cuma 404 favicon) |
| ⑤ | ⭐ **`const n = zp.length`** (3 fungsi) | Memakai panjang **satu** larik; dua larik bisa **beda panjang** kalau ada baris kosong | titik **`NaN` yang hilang TANPA galat**; pada data >500 baris jumlah titik **melampaui batas jaga** (terukur **5000 lingkaran** padahal batas 500). Ditemukan **dari uji-suntik** yang bilang "kerusakan ini lolos" — bukan dari membaca kode |
| ⑥ | tombol *"Contoh sehat"* **berbohong** | Derau `sin(i*5.7)` = pola **teratur berulang** → Shapiro p=0,0000 (**GAGAL normalitas**) | mahasiswa dikira diberi contoh data sehat, padahal uji bilang bermasalah |

### Perbaikan ⑥ (paling penting untuk kejujuran aplikasi)

Wulan ukur **4 bentuk derau**. Yang lolos semua uji: **jumlahkan 6 gelombang beda frekuensi**
(teorema limit pusat) → distribusi mendekati normal (SW **0,609**) **tetap deterministik**
(hasil sama tiap klik — mahasiswa bisa membandingkan dua rasa).

---

## 6. JEBAKAN BARU TERUKUR (jangan ulang)

1. **`(0, eval)` di Node TIDAK membocorkan `const`** — hanya `function`.
   `BATAS_TITIK` → `undefined`. Yang benar: `vm.runInThisContext` + ekspor **eksplisit**
   ke `globalThis` (pola `uji_grafik_hidup.js`).
2. **Uji yang hanya MENGHITUNG belum tentu BERGIGI.** Uji Wulan sempat melaporkan
   "petakan() dirusak → LOLOS". Yang salah **skrip pembuktinya**: memakai `sys.executable`
   (Python LUAR) → `import app.diagnosis` mengambil berkas dari jalur **asli**, bukan
   salinan tersuntik. WAJIB `<salinan>/.venv/bin/python` + `cwd=<salinan>`.
3. **Gerbang TIDAK BOLEH memotret.** `Page.captureScreenshot` pada halaman 6000+ px kena
   `WebSocketTimeoutException` → grup uji **GAGAL padahal 16 asersinya LULUS**.
   Potret = untuk mata; gerbang = untuk kode. → `_sketsa/potret_tab_baca_grafik.py`.
4. **Gerbang kini bisa menjalankan `.js`** — `gerbang_uji.py` memakai `node`
   (lewat `shutil.which`), Python venv untuk sisanya.
5. **Navigasi hanya beda HASH tidak memuat ulang halaman** → `bukaTab` tidak jalan.
   Uji `#tab-3` harus `about:blank` dulu, baru alamat bersih.
6. **Potret yang digulir membuat pita tab "kelihatan hilang".** Sebelum menuduh halaman
   rusak: pastikan potret diambil dari posisi yang benar.
7. **Server uji yang sudah jalan menyajikan kode LAMA.** Gerbang yang membaca dari server
   bisa menilai versi usang — baca dari **berkas**.

---

## 7. PELAJARAN STATISTIK (layak jadi bahan ajar)

> **Glejser menguji `|sisa|` vs X secara LINEAR.**
> Corong yang membesar **linear TIDAK tertangkap**, corong **eksponensial tertangkap**.

| Bentuk corong | p Glejser | Tertangkap? |
|---|---|---|
| `1 + 1,5·|x₁|` | 0,44 | ❌ |
| `1 + 3·|x₁|` | 0,31 | ❌ |
| `1 + 5·|x₁|` | 0,18 | ❌ |
| `exp(1,2·x₁)` | **0,0000** | ✅ |

Ini alasan mengapa **mata pada grafik tetap perlu** — bukan hanya angka uji.

---

## 8. NILAI TEKNIS

| Hal | Nilai |
|---|---|
| `BATAS_TITIK` | **500 titik** + label jujur *"digambar 500 dari 2.400 titik — polanya tetap terlihat sama"* |
| Histogram | **Sturges, 5–14 bin** |
| Bingkai contoh | `P.X0=34, P.X1=300` |
| Warna | aman `#2E7D6F` (hijau) · bermasalah `#A85A5A` (merah) |
| Slider hetero awal | **35** |
| Kalimat wajib | *"Tidak ada corong — justru ini yang bagus."* · *"Tidak ada kemiringan — justru ini yang bagus."* |

---

## 9. SISA TAHAP 2

| Langkah | Keadaan | Bahan |
|---|---|---|
| 2.2 Linearitas (scatter X vs Y) | ⬜ | `titik.xy` **sudah ada** |
| 2.3 VIF + hetero | ✅ jalan, tinggal dirapikan | `vif[].vif` |
| 2.4 Khas PLS (Outer Loading · AVE · CR) | ⬜ | `konstruk[].muat[].muat`, `.ave`, `.cr` |
| 2.5 Pemisah jelas mana SPSS mana PLS | ⬜ | — |

---

## 10. CARA MENGULANG SEMUA BUKTI

```bash
cd /opt/data/services/statistik-lab

# gerbang penuh (31 grup) — WAJIB, nilai dari EXIT CODE
bash gerbang_uji.sh; echo "EXIT=$?"

# per lapisan
.venv/bin/python uji_bahan_gambar.py          # 33 LULUS
node uji_grafik_hidup.js                       # 24 LULUS
.venv/bin/python uji_web_grafik.py             # 18 LULUS (butuh server :8122)
.venv/bin/python uji_tombol_contoh.py          # 15 LULUS
.venv/bin/python uji_tab_baca_grafik.py        # 16 LULUS
.venv/bin/python uji_alat_ukur_grafik.py       # 22 LULUS

# buktikan uji grafik BISA GAGAL (suntik 4 kerusakan nyata → harus EXIT 1)
.venv/bin/python _sketsa/bukti_uji_gagal.py

# dokumen cocok dengan kode?
.venv/bin/python sot.py --periksa

# potret untuk mata (TERPISAH dari gerbang)
.venv/bin/python _sketsa/potret_tab_baca_grafik.py bacagrafik
```
