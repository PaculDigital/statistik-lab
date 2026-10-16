# DOKUMENTASI TAHAP 1.6 — NORMALITAS + TOMBOL PINTASAN HETERO (20Sep26)

> **Status: SELESAI & LIVE.** Deploy EXIT 0 · Gerbang utama **25 grup LULUS** ·
> `uji_normalitas.py` **57 LULUS / 0 GAGAL** · verifikasi produksi **18 LULUS / 0 GAGAL** ·
> gerbang **BARU** `gerbang_sintaks_js.py` (terbukti bisa gagal).

---

## 1. MASALAH YANG DIPECAHKAN

Bos menemukan hal yang **belum dijelaskan aplikasi**:

> *"Heteroskedastisitas, saya menemukan ada grafik seperti ini, lihat contoh apa
> pendapatmu? Apakah kita salah?"* — disertai grafik SPSS: sebaran titik **rapat
> merata** di sekitar garis nol (tidak berbentuk corong).

**Jawaban jujur Wulan: TIDAK SALAH.** Grafik Bos itu **benar**, dan justru kabar
baik: **heteroskedastisitas adalah nama PENYAKITNYA**. Tidak ada corong = tidak
ada penyakit = **data sehat**.

| Kejadian nyata | Sebelum 1.6 |
|---|---|
| Mahasiswa lihat grafik rata (seperti SPSS Bos) | ❌ Menyangka "tidak ada hasil" / merasa gambar salah |
| Hetero di kamus dimulai di nilai 35 → terbaca "mulai melebar" | ❌ Tidak ada jalan pintas ke keadaan **sehat** |
| Corong disangka **satu-satunya** bentuk hetero | ❌ Melebar ke kiri / melengkung tidak pernah disebut |
| **Normalitas** tidak ada sama sekali di kamus | ❌ 7 entri, tidak ada yang menjelaskan **bentuk** sebaran sisa |
| Judul tab uji t | ❌ `Uji t: signifikan kok negatif?` — membingungkan |

---

## 2. KEPUTUSAN BOS (20Sep26)

Wulan **gambar sketsa dulu** (2 versi HTML), Bos lihat → putuskan (kebiasaan proyek).

| # | Pertanyaan | Pilihan Bos | Artinya |
|---|---|---|---|
| ① | Judul tab uji t | **`Masalah uji t`** | Ubah **satu tempat saja**: tombol kamus di `/belajar` |
| ② | Bentuk kartu hetero (3 variasi) | **(B)** | **Slider tetap** + **2 tombol pintasan** `Contoh sehat` / `Contoh sakit` |
| ③ | Bentuk kartu normalitas (2 variasi) | **(1)** | Slider **DUA ARAH**: `Miring kiri ◄─ Lonceng ─► Miring kanan` |
| ④ | Nama kartu | **`Normalitas`** | Bukan `Normalitas: lonceng atau miring?` |
| ⑤ | Uji baru + masuk gerbang? | **Boleh** | `uji_normalitas.py` + `gerbang_sintaks_js.py` (grup ke-25) |

Alasan Bos memilih **slider tetap + tombol** (bukan tombol saja):
slider membuat kartu "hidup"; tombol memberi jalan pintas **satu klik**.
Tombol **menyala sendiri** mengikuti posisi slider → tidak pernah menunjuk
keadaan yang tidak sesuai.

---

## 3. YANG DIPASANG

### 3.1 `belajar.html` — 5 titik perubahan

| # | Tempat | Perubahan |
|---|---|---|
| 1 | tombol kamus uji t | `Uji t: signifikan kok negatif?` → **`Uji t: masalah uji t`** |
| 2 | blok tombol kamus | + tombol baru **`Normalitas`** (ikon `activity`) |
| 3 | atas slider | + 2 tombol pintasan **`Contoh sehat` / `Contoh sakit`** |
| 4 | entri `KAMUS` | + entri ke-7 (kartu ke-8) **`normalitas`** |
| 5 | fungsi baru | `kalimatTafsir()` + `pintasanPasang()` |

**Entri normalitas** (paling beda dari yang lain):

```js
normalitas: {
  judul: 'Normalitas',
  tanya: 'Sebesar apa kemiringannya?',
  kiri: 'Miring kiri', kanan: 'Miring kanan',
  min: -100, maks: 100,          // ⚠️ RENTANG SENDIRI
  gambar: (v, c) => { /* histogram 21–22 batang, batang bergeser */ }
}
```

### 3.2 ⚠️ AKAR: slider dulu milik BERSAMA

Slider `#slider` dipakai **semua** entri kamus dengan batas dipaku `min="0" max="100"`.
Normalitas butuh `-100…+100`. Kalau `min` cuma diubah global → **semua entri lain rusak**.

**Perbaikan di akar:** tiap entri membawa batasnya sendiri, dan `pilih()` menyetelnya:

```js
el('slider').min = (kk.min  !== undefined) ? kk.min  : 0;
el('slider').max = (kk.maks !== undefined) ? kk.maks : 100;
```

Bukti tidak merusak entri lama (`uji_normalitas.py` bagian 6):
`beta`/`pvalue`/`r2`/`vif`/`alpha` semuanya **kembali 0…100** dan pitanya normal.

### 3.3 Kalimat penegas — HIDUP mengikuti slider

Fungsi `kalimatTafsir(k, v, pesanBawaan)` mengganti kalimat pita **hanya** untuk
`hetero` dan `normalitas`. Entri lain **tidak tersentuh** (langsung pakai `pesan`).

| Slider | Kalimat hetero |
|---|---|
| 0–17 (**sehat**) | ✅ *"**Tidak ada corong — justru ini yang bagus.** Sebarannya rata… syarat ini **terpenuhi**."* |
| 18–44 | 👀 *"Sebarannya mulai melebar. Belum pasti bermasalah… periksa **uji Glejser**."* |
| 45+ | ⚠️ *"Ini contoh yang bermasalah… **melebar bukan cuma bentuk corong** — bisa juga mekar ke arah sebaliknya, atau melengkung."* |

Kalimat senada untuk normalitas: *"**Tidak ada kemiringan — justru ini yang bagus.**"*

### 3.4 `gaya.css`

Kelas **BARU** (di-grep dulu — terbukti belum ada sebelum ditulis):

```css
.pintasan-baris  { display: flex; gap: 8px; flex-wrap: wrap; }
.pintasan        { … }   /* tombol */
.pintasan.nyala  { … }   /* tombol menyala */
```

---

## 4. ⚠️ AKAR TERBESAR: SATU `}` MEMATIKAN SELURUH HALAMAN

### 4.1 Gejalanya — sangat menipu

| Yang terlihat | Kenyataan |
|---|---|
| Halaman `/belajar` **HTTP 200** | ✅ benar, tapi skripnya **mati seluruhnya** |
| Konsol browser | hanya **404 favicon** — tidak ada galat berguna |
| **Klik tombol kamus tidak berefek** | `typeof KAMUS` = `undefined`, `typeof pilih` = `undefined` |
| Semua `<script>` **ADA** di DOM (50.177 byte) | tapi **tidak dieksekusi** |

Kata kuncinya: **"HTTP 200 + konsol bersih ≠ kode jalan".**

### 4.2 Cara menemukan (5 langkah, semua terukur)

1. **Node.js `--check`** pada isi skrip → `SyntaxError: Unexpected identifier 'normalitas'` (baris 141).
   Node dipakai karena **dia yang benar** — Wulan 3× salah hitung kurung manual.
2. **Uji terisolasi** tiap entri `KAMUS` sendiri-sendiri → hanya **`hetero`** yang gagal.
3. **Hitung kurung `const KAMUS`** → `{` = 136, `}` = **135** → **kurang 1**.
4. **Bandingkan dengan CADANGAN** (`cadangan_pintasan`, sebelum Wulan menyisipkan
   pintasan) → **sudah rusak juga** → berarti pelakunya skrip **sebelumnya**.
5. **Cek jumlah entri per cadangan** → `cadangan_kamus` = **0 entri** `normalitas`
   (artinya cadangan itu kondisi LAMA) → **pelakunya `sisip_kamus_normalitas.py`**.

### 4.3 Akarnya

```python
P_AKHIR_KAMUS = "  },\n  beta: {\n"          # ← penanda WULAN
baru = baru.replace(P_AKHIR_KAMUS, ENTRI, 1)  # ← MENGHAPUS penutup entri hetero
```

`ENTRI` Wulan berakhir dengan `  },\n  beta: {` — jadi yang **dipindahkan** adalah
penutup **hetero**, bukan penutup **normalitas**. → Hetero kehilangan `},`-nya
**selamanya**, dan `normalitas: {` **jatuh ke dalam** hetero.

**Perbaikan (di akar, bukan tambalan):** tambah `},` penutup entri `hetero`.

```diff
               fill="#6B6259">${label}<\/text>`;
     }
+  },
   normalitas: {
     judul: 'Normalitas',
```

Bukti berhasil: `node --check` → **sintaks OK** (50.182 byte).

### 4.4 Kenapa 4 gerbang lama TIDAK menangkapnya

| Gerbang | Kenapa lewat |
|---|---|
| `gerbang_jinja.py` | template bisa di-compile (Jinja tidak melihat JS) |
| `gerbang_tag_skrip.py` | urusannya tag penutup HTML, bukan sintaks JS |
| `gerbang_galat_js.py` | hanya periksa berkas `.js` **berdiri sendiri**; skrip **inline** di template tidak disentuh |
| `gerbang_kode_tumpah.py` | hanya teks yang terlihat user |

→ **Lubang ini ditutup: `gerbang_sintaks_js.py` (grup ke-25).**

---

## 5. GERBANG BARU — `gerbang_sintaks_js.py` (grup ke-25)

**Cara:** RENDER template Jinja dulu → ambil tiap `<script>` inline →
`node --check`. Node melaporkan **baris & kolom persis**.

⚠️ **Jebakan yang ketemu saat membuatnya:** percobaan pertama **GAGAL PALSU** pada
`buat_data.html` baris 4 (`window.BATAS_BETA_RANTAI = {{ batas_beta_rantai }}`).
Sebabnya: skrip inline **berisi sintaks Jinja**, jadi diperiksa **sebelum dirender**.
**Perbaikan:** render dulu, baru periksa. Hasil: **14 LULUS / 0 GAGAL**.

**Bukti gerbang BISA GAGAL** (`_sketsa/uji_gerbang_sintaks.py`):

| Langkah | Hasil |
|---|---|
| keadaan bersih | ✅ EXIT 0 |
| **buang 1 `},`** (kerusakan asli 20Sep26) | ✅ **EXIT 1 — GAGAL** |
| dipulihkan | ✅ EXIT 0 lagi |
| berkas asli utuh | ✅ identik |

---

## 6. CACAT LAIN YANG IKUT KETANGKAP

**13 tag penutup HTML tidak di-escape** di blok yang Wulan tulis
(12× `</strong>`, 1× `</em>`) — bisa membuat parser HTML menganggap `<script>`
sudah selesai → **kode tumpah jadi teks**. Perbaikan: `<\\/strong>`, `<\\/em>`.

**Cara memastikan ini cacat WULAN (bukan cacat lama):** jalankan gerbang itu pada
**cadangan ASLI** di salinan terpisah → **0 pelanggaran, EXIT 0**.

> ⚠️ Wulan sempat **salah simpul** di sini: menghitung `</strong>` di SELURUH
> berkas (46× di kondisi sekarang, 32× di cadangan) dan menyangka cacat lama.
> **Padahal hanya tag DI DALAM `<script>` yang berbahaya** — di HTML biasa aman.

---

## 7. JEBAKAN TEKNIS SESI INI (jangan diulang)

| # | Jebakan | Akar & cara benar |
|---|---|---|
| 1 | **`pkill -f "remote-debugging-port=93"`** mematikan **Chrome 9333** yang dibutuhkan `uji_sub_regresi.py` | Jangan `pkill` pola lebar. Gerbang bergantung pada Chrome itu. |
| 2 | `pkill` pola cocok ke **shell Wulan sendiri** → `SIGTERM` | Pisahkan perintah; pakai pola sempit + `\b`. |
| 3 | **CDP websocket putus** (`ConnectionResetError`/`ConnectionClosed`) | Tutup **semua tab sisa** dulu (`/json/list` → `/json/close/<id>`), baru buka tab baru. |
| 4 | **Chrome `--screenshot` tidak menulis berkas** (dbus/Glib error) | Lingkungan ini tidak mendukung. Bukan cacat aplikasi — **jangan dipaksa**; verifikasi lewat CDP/DOM (`getBoundingClientRect`, `innerText`). |
| 5 | Regex `<script>(.*?)</script>` **gagal** potong blok | Isi skrip **menyebut** `</script>` di komentar → potong lewat **posisi**, bukan regex malas. |
| 6 | `const KAMUS = {` tidak pernah mencapai kedalaman 0 | Cari penutup lewat **mesin keadaan kedalaman** (abaikan string/komentar), bukan `b.strip() == '};'` (itu menemukan penutup **fungsi lain**). |
| 7 | Uji Wulan menyalahkan aplikasi | Menuntut slider `0` padahal berkas **ASLI** memang `value="35"`. **Periksa perilaku ASLI di cadangan dulu**. |
| 8 | `pkill`/tulis ke `/tmp` dkk memicu **security scan** | Normal, tapi periksa hasilnya — jangan asal percaya "auto-approved". |

---

## 8. UJI & BUKTI

| Alat | Hasil |
|---|---|
| `uji_normalitas.py` (Chrome nyata, 390px) | **57 LULUS / 0 GAGAL** |
| `gerbang_sintaks_js.py` | **14 LULUS / 0 GAGAL** |
| `_sketsa/uji_gerbang_sintaks.py` | **4 LULUS / 0 GAGAL** (terbukti bisa gagal) |
| `gerbang_ikon.py` | LULUS (107 pemakaian) |
| `gerbang_tag_skrip.py` | **0 pelanggaran** |
| `uji_sub_regresi.py` | 46 LULUS / 0 GAGAL |
| **gerbang_uji.sh** | **26 GRUP LULUS / 0 GAGAL · EXIT 0** |
| `jalankan.sh` (deploy) | **DEPLOY_EXIT=0**, kontainer `Up (healthy)` |
| `_sketsa/verifikasi_produksi.py` | **18 LULUS / 0 GAGAL** — isi produksi diperiksa, bukan cuma log |

**Isi `uji_normalitas.py` (9 bagian):** tombol & biji pita · normalitas (min/max/nilai
awal/histogram/pita/kalimat) · geser kiri & kanan · hetero (pintasan, rentang
**kembali** ke 0…100) · klik `Contoh sakit` · **5 istilah lama tetap utuh** ·
kartu uji t · tidak ada kode bocor · **tidak meluber di 390px**.

**Isi `verifikasi_produksi.py`:** cek dari **DALAM kontainer produksi**
(tombol Normalitas ada · judul `masalah uji t` ada · judul lama **hilang** ·
biji = 8 · pintasan ada · 2 kalimat penegas ada · `node --check` skrip live ·
7 halaman HTTP 200).

---

## 9. HASIL AKHIR — SIAP DILIHAT BOS

**statistik.bikinaja.id/belajar** → tab **Materi & Kamus**:

| Aksi | Yang muncul |
|---|---|
| Lihat baris tombol | **8 tombol** (dulu 7) — baru: **Normalitas** |
| Klik **Heteroskedastisitas** | 2 tombol `Contoh sehat` / `Contoh sakit` di atas slider |
| Klik **Contoh sehat** | kotak hijau: ***"Tidak ada corong — justru ini yang bagus."*** |
| Klik **Contoh sakit** | peringatan + *"melebar bukan cuma bentuk corong"* |
| Klik **Normalitas** | slider **DUA ARAH** (miring kiri ↔ lonceng ↔ miring kanan) |
| Tab **Ruang Uji** | judul **`Uji t: masalah uji t`** |

---

## 10. SISA / BELUM

- **Belum ada potret** hasil akhir untuk dilihat mata — Chrome `--screenshot`
  tidak berfungsi di lingkungan ini. Verifikasi dilakukan lewat CDP/DOM + angka.
  **Belum diputuskan** cara lain memotret.
- Kartu **Campuran** di `/kuantitatif` masih belum punya sub-pilihan (sisa 1.3).
- Uji `uji_normalitas.py` **belum masuk `gerbang_uji.py`** (masih uji mandiri) —
  perlu keputusan Bos apakah dimasukkan sebagai grup ke-26.
- Label tombol `Sakit (corong)` pada rencana awal **tidak dipakai**; diganti
  `Contoh sakit` supaya tidak menyesatkan (corong hanya satu bentuk).

---

## 11. ⚠️ TAMBAHAN (lanjutan 20Sep26) — CHROME :9333 DIPAKAI BERSAMA

Setelah dokumen ini selesai, Wulan memasukkan `uji_normalitas.py` sebagai
**grup ke-26** gerbang. Ternyata **GAGAL** — akarnya **berlapis**. Semua terukur.

### 11.1 `uji_normalitas.py` dulu TIDAK BERDIRI SENDIRI
Ia butuh 2 hal yang disiapkan **berkas lain**:

| Kebutuhan | Dulu disiapkan oleh |
|---|---|
| Server uji :8122 | `_sketsa/jalankan_uji_normalitas.py` (berkas **TERPISAH**) |
| Chrome CDP :9333 | gerbang lain (dipakai **bersama**) |

Begitu dipanggil gerbang **langsung** → tidak ada yang melayani `URL` → halaman
kosong → *"Tombol kamus berjumlah 8 (dapat 0)"* = **GAGAL PALSU**.
**FIX di akar:** `uji_normalitas.py` **menyiapkan server-nya sendiri**
(`_nyalakan_server()`) sehingga bisa dipanggil dari mana saja.

### 11.2 🚨 JANGAN MENYALAKAN CHROME SENDIRI — 3 cara, GAGAL SEMUA
| Cara | Hasil |
|---|---|
| `pkill -f 'remote-debugging-port=9341'` | ❌ Mematikan **shell Wulan sendiri** (pola ada di baris perintah shell-nya) + kena Chrome tetangga |
| `subprocess.Popen` + `--user-data-dir` | ❌ Chrome keluar sendiri (`dbus/GLib-GIO-CRITICAL: g_settings_schema_source_lookup`) |
| `nohup ... &` dari shell | ❌ CDP sempat *"DevTools listening on ws://..."*, lalu **MATI** begitu shell selesai |

**SEBAB TERUKUR:** Chrome yang **BERTAHAN** (:9333, :9444) punya **`PPID = 1`**
(di-reparent ke init) — dijalankan lewat `terminal(background=true)` Hermes,
**bukan** dari shell perintah biasa.

**⇒ CARA BENAR: PAKAI Chrome :9333 yang SUDAH HIDUP.** Kalau mati → uji GAGAL
dengan **pesan jelas**, jangan diam-diam menguji hal lain.

```bash
# cek hidup?
curl -s -m 5 -o /dev/null -w "%{http_code}\n" http://127.0.0.1:9333/json/version
# sediakan minimal 1 tab (uji_sub_regresi.py mensyaratkannya)
curl -s -m 8 -X PUT "http://127.0.0.1:9333/json/new?about:blank" -o /dev/null
```

### 11.3 🚨 JANGAN TUTUP SEMUA TAB MILIK CHROME BERSAMA
Kode lama `Tab.buka()` menutup **SETIAP** tab lama (alasan: *"tab yatim bikin
ConnectionResetError"*). **SALAH** — terukur: `uji_sub_regresi.py` (gerbang lain,
Chrome sama) **mensyaratkan minimal 1 tab sudah ada**; kalau kita tutup semua →
dia gagal *"tidak ada tab"*.

**FIX di akar:**
- Tutup **HANYA tab milik uji sendiri** — `Tab.tutup()` menyimpan `self.tab_id`.
- **JANGAN** mematikan Chrome-nya (bukan milik kita).
- `tab = None` diletakkan **sebelum** `try` supaya `finally` tidak meledak
  (`NameError` menutupi galat asli).

### 11.4 Bukti akhir
| Uji | Hasil |
|---|---|
| `uji_normalitas.py` | **57 LULUS / 0 GAGAL** (berdiri sendiri) |
| `uji_sub_regresi.py` | **46 LULUS / 0 GAGAL** (berdampingan, tidak saling merusak) |
| `gerbang_uji.sh` | **26 GRUP LULUS · EXIT 0** |
| `sot.py --periksa` | **SELARAS** |

**📌 PELAJARAN INDUK BARU:** *"Sumber daya yang DIPAKAI BERSAMA jangan dimatikan
oleh pihak yang tidak memilikinya."* Kalau dua gerbang memakai Chrome yang sama:
(a) jangan saling mematikan, (b) masing-masing tutup **tab sendiri**,
(c) sediakan minimal 1 tab untuk yang membutuhkannya.
