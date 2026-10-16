# 📕 CATATAN KESALAHAN & CARA MEMPERBAIKI — 21 Sep 2026 (kedua)

> **Kenapa berkas ini ada:** Bos minta *"catat kesalahan agar tidak diulangi
> dan tahu jalan memperbaiki"*. Isinya **kesalahan Wulan sendiri** — bukan
> daftar bug aplikasi. Setiap kesalahan ditulis dengan **arah perbaikan yang
> bisa dijalankan**, bukan cuma "jangan salah lagi".
>
> **Aturan induk yang berlaku di proyek ini** (dari Bos, verbatim):
> *"tidak boleh buru buru, selalu cek dan analisa baca secara utuh.
> Jangan sekali kali coba suntik, tambal sangat haram disini harus cari akar
> masalahnya."* · *"Kita selalu Sot single source of truth"* ·
> **MAKS 2× percobaan** — gagal 2× di titik sama = STOP, lapor, minta putusan.

---

## 🔴 K-01 — MENYALAHKAN APLIKASI PADAHAL PRASARANA MATI

**Kejadian:** 7 grup gerbang dilaporkan **GAGAL**. Wulan mulai **mencari bug di
kode aplikasi**. Padahal mesin sama sekali tidak salah.

**Akar:** Chrome CDP `:9333` **mati**. Wulan hanya menyalakan server uji `:8122`,
lupa Chrome. Gerbang lama **menyamakan** "prasarana mati" dengan "mesin rusak".

**Cara tahu (gejala pengenal):** **banyak grup berbrowser gagal beruntun,
sementara grup murni-Python LOLOS.** Pola itu = curigai prasarana.

**PERBAIKAN (sudah dikerjakan, jangan diulang):**
1. **SELALU cek prasarana SEBELUM gerbang:**
   ```bash
   curl -s -o /dev/null -w "CDP 9333 -> %{http_code}\n" --max-time 4 http://127.0.0.1:9333/json/version
   curl -s -o /dev/null -w "server 8122 -> %{http_code}\n" --max-time 4 http://127.0.0.1:8122/klinik
   ```
   `200` = hidup · `000` = mati.
2. Chrome mati → nyalakan (`terminal(background=true)`):
   ```
   /opt/data/home/.cloakbrowser/chromium-151.0.7922.108.6-pro/chrome \
     --headless=new --no-sandbox --disable-gpu \
     --remote-debugging-port=9333 --remote-allow-origins=* \
     --window-size=390,900 --hide-scrollbars
   ```
3. Sekarang uji memakai **`prasarana_uji.pastikan_chrome()`** → mati = keluar
   **kode 77 (LEWAT)**, dan gerbang mencetak *"lewat karena prasarana"* —
   **bukan** GAGAL. Jadi laporan gerbang tidak lagi menyesatkan.

**Batas yang sudah terukur (JANGAN dicoba lagi):** Chrome **TIDAK BISA** dilepas
dari gateway. 4 cara gagal semua (`Popen` biasa · `start_new_session=True` ·
double-fork · double-fork+setsid → Chrome kabur dengan galat **dbus**). Chrome
hanya hidup kalau dijalankan lewat `terminal(background=true)` Hermes (PPID =
gateway). **JANGAN** bikin watchdog cron (cron ≠ anak Hermes → gagal dbus).

---

## 🔴 K-02 — SALAH MEMBACA BENTUK JAWABAN SERVER (DITEBak)

**Kejadian:** 2 uji gagal karena Wulan menebak nama kunci & bentuk data.

| Dianggap | Kenyataan (terukur) |
|---|---|
| `up['kolom']` = daftar teks | **daftar dict**: `[{'nama':'X1a','kosong':0,'jenis':'angka'}, …]` |
| jawaban `/periksa` punya kunci `hasil` | kuncinya **`koef`** · ada juga `prediktor`, `y`, `r2`, `vif`, `normalitas` |

**Akibat:** `c.startswith` meledak / peran jadi kosong → uji gagal palsu.

**PERBAIKAN — ATURAN BARU (lakukan sebelum menulis uji apa pun):**
```python
# CETAK dulu kunci-kunci jawaban, baru tulis uji
for k in sorted(jawaban.keys()):
    print(f'  {k:22} = {type(jawaban[k]).__name__:6} {str(jawaban[k])[:80]}')
```
**Jangan hafal — cetak.** Nama kunci bisa berubah kalau mesin diubah.

---

## 🔴 K-03 — MEMAKU ANGKA / AMBANG KARANGAN DI UJI

**Kejadian:** Wulan menuntut **`R² > 0,3`** lalu uji memprotes mesin
(`R² = 0,2543`). Setelah **dihitung tangan dengan data yang sama**: R²
**seharusnya memang 0,2543** → **mesin BENAR**, uji Wulan yang cacat.

**Kenapa 0,25 itu benar:** derau dari 2 item `Y1` (skala 1-5) menelan sinyal `X1`
yang kekuatannya cuma ~1,15 simpangan baku. Bukan bug — itu datanya.

**PERBAIKAN — ATURAN BARU:**
> **Hitung dulu angka yang SEHARUSNYA dari sumbernya, baru bandingkan.**
> Jangan pakai ambang karangan ("sepertinya harus di atas 0,3").
> Kalau tidak bisa dihitung tangan → uji **bentuk**-nya (ada/tipe/rentang),
> jangan nilainya.

Kelas kesalahan yang sama pernah terjadi (19Sep26): kunci uji Wulan salah tulis
("Berjenjang" = mediasi berjenjang) — mesin benar, Wulan salah kunci.

---

## 🔴 K-04 — MEMBERSIHKAN DATA DI DALAM UJI (MENGUJI DIRI SENDIRI)

**Kejadian:** uji mengirim `''` **lalu Wulan sendiri** menjalankan
`pd.to_numeric(..., errors='coerce')` **sebelum** memanggil fungsi yang diuji.
Akibatnya kolom kosong sudah hilang → hasil 2.0 → uji memprotes palsu.

**PERBAIKAN — ATURAN BARU:**
> Kirim **nilai APA ADANYA** ke fungsi yang diuji. Biarkan **MESIN** yang
> membersihkan. Kalau uji membersihkan dulu, yang diuji adalah data bersih
> buatan sendiri — bukan perilaku mesin.

---

## 🔴 K-05 — MEMBERI NAMA CEK YANG SALAH HITUNG (salah aritmetika sendiri)

**Kejadian:** uji menulis *"responden-1 jawab **1** dari 3 → 12,0"* padahal
data ujinya berisi **2** item terjawab (4 dan 5) → seharusnya **(9/2)×3 = 13,5**.
Mesin benar, hitungan Wulan salah.

**PERBAIKAN:** sebelum menuduh mesin, **tulis ulang perhitungannya** dengan data
yang benar-benar dikirim (cetak datanya), jangan mengandalkan ingatan baris demi
baris.

---

## 🔴 K-06 — MENGUBAH DOKUMEN TANPA MENJALANKAN SOT

**Kejadian:** setelah uji baru masuk gerbang, dokumen masih menyebut **38 grup**
padahal kode sudah **43**. SOT menangkap → tak selaras.

**PERBAIKAN (urutan benar setiap kali gerbang berubah):**
```bash
.venv/bin/python sot.py --periksa     # ← WAJIB, menghitung dari KODE
```
Pesan SOT *"menyebut 38 grup, kode punya 43"* → perbaiki dokumen, **jangan**
perbaiki sot.py. SOT adalah **pintu tunggal kebenaran**.

---

## 🔴 K-07 — MEMUTUSKAN SOAL STATISTIK SENDIRI

**Kejadian:** muncul pertanyaan *"jawaban kosong dihitung bagaimana?"* — Wulan
hampir memilih sendiri. Kalau salah pilih, **seluruh hasil analisis mahasiswa
bisa salah** tanpa ada yang sadar.

**PERBAIKAN:** berhenti, sodorkan **3 opsi + akibatnya masing-masing + ⭐
rekomendasi**, minta putusan Bos. Bos memilih **Opsi B**. Keputusan itu dicatat
di `KEPUTUSAN_PARSIAL_SIMULTAN_21SEP2026.md §8`.

> **Pembeda penting:** keputusan **statistik/metodologi** = hak Bos.
> Keputusan **teknis** (nama variabel, struktur kode) = boleh diputuskan Wulan,
> tetap dilaporkan.

---

## 🔴 K-08 — MENGULANG PERBAIKAN ATAS LAPORAN YANG SUDAH KEDALUWARSA

**Kejadian:** laporan *"6 GRUP GAGAL"* masuk **setelah** Chrome dinyalakan dan
gerbang sudah hijau. Perbaikan sudah dilakukan; laporan itu milik proses **lama**.

**PERBAIKAN:** sebelum memperbaiki, **pastikan laporan itu masih berlaku**:
cek **waktu proses** (`ps -o etime`) & **keadaan prasarana sekarang**. Kalau
sudah teratasi → **jelaskan**, jangan mengerjakan ulang (mengerjakan ulang
laporan basi = menambal).

---

## 🔴 K-09 — MENGUKUR MESIN DI TENGAH JALAN (lalu menuduh cacat)

**Kejadian (21Sep26):** audit menemukan `uji_mesin_s3.py` GAGAL. Wulan lalu
**mengukur sendiri dengan `bangun_dari_spek()` langsung** → dapat galat
**0,22** → **melaporkan ke Bos** bahwa mesin rantai (**S3 berganda-berantai**)
**cacat**, bahkan sempat menulis berkas `CACAT_RANTAI_BERANTAI_21SEP2026.md`.

**Kenyataannya: MESIN BENAR.** Diukur dari jalur SUNGGUHAN (`buat_data()`):
```
X1 → X2   minta 0,55   terbaca 0,5503   galat 0,0003  ✅
X2 → X3   minta 0,55   terbaca 0,5417   galat 0,0083  ✅
galat_maks 0,0207 (batas 0,06) → LOLOS
```

**Akar kesalahan Wulan:** `bangun_dari_spek()` adalah fungsi **tingkat rendah** —
ia membangun data **BELUM dikalibrasi**. Kalibrasi terjadi di
`buat_data()` lewat `kalibrasi_per_jalur()`. Wulan mengukur **bahan setengah jadi**
lalu menyalahkan hasil akhir.

**PERBAIKAN — ATURAN BARU:**
> Sesudah gagal, tanyakan dulu: **"fungsi mana yang DIPAKAI aplikasi?"**
> Ukur dari **pintu masuk yang sama** dengan produksi (`buat_data()`,
> `periksa_peran()`, rute HTTP), **bukan** dari fungsi internal.
> Buktikan dengan: `grep -n "def buat_data" -A5 app/berkas_kerja.py` dan lihat
> fungsi apa yang dipanggilnya.

**Pelajaran turunannya:** laporan `uji_mesin_s3.py` GAGAL — sebabnya uji itu
**mengukur dengan cara yang sama** seperti Wulan (dari fungsi internal). Jadi
**uji itu sendiri yang salah ukur**, bukan mesinnya. **Mesin tidak pernah rusak.**

**Catatan kejujuran:** berkas cacat palsu **dihapus** — dokumentasi tidak boleh
menyimpan tuduhan yang salah. Kalau tidak dihapus, orang berikutnya akan
"memperbaiki" mesin yang sudah benar (**menambal!**).

---

## 🔴 K-10 — SALAH MEMATIKAN SERVER (server LAMA masih hidup)

**Kejadian (21Sep26):** saat menguji "bukti bisa gagal", Wulan menyuntikkan
cacat ke `app/main.py` lalu `kill $PID`. Ternyata PID yang diambil hanya
**salah satu** dari DUA proses (`bash` pembungkus + `python` uvicorn). Server
**LAMA masih hidup** → uji dijalankan ke kode LAMA → hasilnya menipu:
`penguat=['Z1']` padahal Z sudah dibuang, dan Wulan **hampir menyimpulkan**
"uji tidak bisa menangkap cacat".

**Cara memperbaiki:**
```bash
pkill -f "uvicorn app.main:app --host 127.0.0.1 --port 8122"
ps -eo pid,cmd | grep "[u]vicorn app.main" | wc -l     # WAJIB 0
curl -s -o /dev/null -w "%{http_code}" --max-time 4 \
     http://127.0.0.1:8122/health                      # WAJIB 000
```

**ATURAN:** setelah mematikan server, buktikan **0 proses** DAN port **mati**
sebelum menyalakan yang baru. Jangan percaya satu `kill`.

---

## 🔴 K-11 — `(x or 1)` UNTUK ANGKA → GAGAL PALSU

**Kejadian (21Sep26):** di `uji_kaitan_web.py`, Wulan menulis:

```python
cek('interaksi SIGNIFIKAN', (it.get('p') or 1) < 0.05, ...)
```

Server mengirim `p = 0.0` — **SANGAT signifikan** (p dibulatkan 6 angka).
Tapi `0.0` itu **falsy** → tergantikan `1` → uji menyatakan **GAGAL**.
Wulan hampir melaporkan "mesin salah" padahal **ujinya** yang salah.

**Cara memperbaiki:**
```python
p_it = it.get('p')
cek('interaksi SIGNIFIKAN', p_it is not None and float(p_it) < 0.05, ...)
```

**ATURAN:** `or` hanya untuk `None`/kosong. Untuk **angka**, periksa
`is not None` secara eksplisit.

---

## 🔴 K-12 — MEMAKU SIMPULAN STATISTIK PADA SATU NILAI

**Kejadian (21Sep26):** `uji_kaitan_web.py` memaku `jenis == 'mediasi penuh'`
padahal data ditanam dengan c' = 0,00. Kenyataannya (data berderau + item
Likert) c' = **0,169** dan tetap signifikan tipis → mesin menjawab
**"mediasi parsial"**. Mesin **BENAR**; ujinya terlalu kaku.

**Cara memperbaiki:** uji **arah & hubungan**, bukan satu label:
```python
cek('jenis termasuk mediasi', str(h.get('jenis')).startswith('mediasi'))
cek('|c\'| < |c|', abs(h['cp']['b']) < abs(h['c']['b']))
```

**ATURAN:** kalau data disimulasikan dengan derau, hasil statistik **wajar
bergeser**. Yang wajib benar = **hubungan antar-angka**, bukan angka persis.

---

## 🔴 K-13 — MEMAKAI VARIABEL YANG TIDAK ADA DI FUNGSI (`payload`)

**Kejadian (21Sep26):** menambah `bentuk=payload.get('bentuk_mediasi')` di
`periksa_spss()` — padahal fungsi itu **tidak punya** `payload`; yang ada
`kolom_x/kolom_y/kolom_m/kolom_z`. Akibatnya: `NameError` **setiap kali**
dihitung → mediasi & moderasi **mati total** (`kaitan.ada = False`),
padahal sebelumnya sudah lulus.

**Cara memperbaiki:** tambahkan parameter eksplisit `bentuk_mediasi` ke
tanda tangan fungsi + teruskan dari rute (`app/main.py`).

**ATURAN:** fungsi yang dipanggil dari rute TIDAK melihat `payload`. Setiap
nilai baru harus **ditambahkan ke tanda tangan** dan **diteruskan rute**.

---

## 🔴 K-14 — MERUSAK JALUR YANG SUDAH HIJAU (tidak uji lama dulu)

**Kejadian (21Sep26):** saat menambah mediasi berjenjang, `kaitan` yang
sudah lulus jadi `ada=False` untuk **semua** kasus. Ketahuan **hanya karena**
membandingkan dengan uji lama `uji_kaitan_web.py` (yang tadinya EXIT 0).

**Cara memperbaiki:** jalankan uji lama **SEBELUM** dan **SESUDAH** setiap
perubahan yang menyentuh jalur yang sudah hijau.

```bash
# SEBELUM mengubah
.venv/bin/python uji_kaitan_web.py    # harus EXIT 0 (patokan)
# ... ubah kode ...
# SESUDAH mengubah
.venv/bin/python uji_kaitan_web.py    # harus tetap EXIT 0
```

**ATURAN:** kode yang sudah lulus itu **patokan**. Kalau setelah perubahan
patokan jadi gagal → itu **KERUSAKAN BARU**, bukan "uji usang".

---

## 🔴 K-15 — MENULIS TAG PENUTUP MENTAH DI DALAM STRING JS

**Kejadian (21Sep26):** menambah kartu mediasi di `diagnosis.html`, Wulan
menulis `'…</h2>'` dan `'…</p>'` **mentah** di dalam string JavaScript.
`gerbang_tag_skrip.py` menangkapnya (**1 pelanggaran**) — halaman akan tetap
HTTP 200 dan "tampak hidup", tapi **kode tumpah jadi teks**.

**Cara memperbaiki:** escape garis miring → `<\/h2>` dan `<\/p>`.

**ATURAN:** setiap kali menyentuh `<script>` di template, **WAJIB** jalankan:

```bash
.venv/bin/python gerbang_tag_skrip.py     # WAJIB EXIT 0
```

---

## 🔴 K-16 — MENUNTUT PERILAKU YANG SUDAH DIBUANG BOS (uji usang)

**Kejadian (21Sep26):** grup gerbang `WEB — sub-pilihan model` GAGAL **7**.
`uji_sub_regresi.py` masih menuntut **3 sub** di panel Regresi
(`Sederhana` · `Berganda` · **`Berganda-berantai`**) dan istilah
"Beberapa regresi sederhana".

**Kenyataannya BENAR:** keputusan Bos 21Sep26 (N1 + R1) → kartu Regresi
memang **2 sub** ("**Parsial** (Sederhana)" + "Berganda (Parsial + Simultan)")
dan **"Berganda-berantai" sengaja disembunyikan** (`class="pilih-cara sembunyi"`,
baris 150, komentar *"JANGAN HAPUS"*). Penegasan Bos: *"Berganda berantai sudah
tidak ada"*.

⇒ **CACAT UJI, BUKAN CACAT APLIKASI.** Aplikasi sudah lama benar; uji lama
tertinggal.

**CARA MEMBETULKAN (jangan tambal):** hapus tuntutan berantai; ganti jadi
menuntut **2 sub** + istilah **"Parsial"** & **"Simultan"**.

**⚠️ JEBAKAN DI DALAM JEBAKAN — 3 putaran terbuang:**
1. Uji membaca `d2['teknis']` dari `.kartu-teknis` — **tidak memuat judul**.
2. Wulan menambah baca `.cara-judul` → **KOSONG di panel sub** `.kartu-pilih`
   (`.cara-judul` itu milik kartu `data-cara` di halaman `/buat-data`, beda tempat).
3. Yang BENAR: judul sub = **`.kartu-judul`** (mis. `Parsial (Sederhana)`).

**PELAJARAN:**
- Dua kelas nama mirip di DUA HALAMAN berbeda → **buktikan dengan grep** dulu
  (`grep -n "kartu-judul" app/templates/kuantitatif.html`), jangan tebak.
- Uji lama yang menuntut perilaku **yang sudah diputuskan dibuang** = harus
  DISELARASKAN, bukan dipaksa lolos, dan bukan pula aplikasinya yang diubah.
- Halaman yang sama bisa punya 2 struktur kartu: `data-induk` (induk) vs
  `data-cara` (pemilih di /buat-data). Periksa yang mana yang diukur.

---

## 🔴 K-17 — UJI "HARUS BERGESER" DENGAN DATA YANG MUSTAHIL BERGESER

**Kejadian (21Sep26):** uji moderasi menuntut `ΔR² Z1` **berbeda** saat Z2
diikutsertakan — tapi datanya dibuat dengan `Z2 = rng.normal()` **lepas**
(tidak berkorelasi Z1). Mengendalikan variabel yang **tidak berhubungan**
memang **tidak mengubah** hasil → uji **mustahil lulus**.

⇒ **Cacat RANCANGAN UJI, bukan mesin.** Untuk membuktikan "kovariat
dikendalikan", kovariatnya WAJIB berkorelasi dengan variabel fokus
(`Z2 = 0,75·Z1 + derau`). Baru setelah itu pergeseran terukur nyata.

---

## 🔴 K-18 — UJI API LANGSUNG MENYEMBUNYIKAN CACAT JALUR HALAMAN

**Kejadian (21Sep26):** uji moderasi mengirim `kolom_z` **langsung ke
`/api/diagnosis/periksa`** → hijau. Padahal **HALAMAN tidak pernah mengirim
`kolom_z`** → pemakaian nyata **tidak pernah** menghitung moderasi.

⇒ **Uji yang tidak lewat jalur user TIDAK membuktikan fitur sampai ke user.**
Wajib ada uji **jalur halaman sungguhan** (`uji_moderasi_halaman.py`:
Chrome → unggah → tandai peran lewat dropdown → tekan periksa → baca hasil).

---

## 🔴 K-19 — MENGIRIM `kolom_z` MENIMPA HASIL GABUNGAN PERAN

**Kejadian (21Sep26, 2 putaran terbuang):** uji mengirim
`kolom_z=['Z1','Z2']` (nama KONSTRUK) ke rute, padahal di data kolomnya
bernama `Z1a, Z1b, Z2a, Z2b`.

Rute memakai **`peran`** untuk menggabung kolom seperan; kalau `kolom_z`
ikut dikirim, isinya **MENIMPA** hasil gabungan → server mencari kolom
`Z1` yang **tidak ada** → moderasi dihitung **tanpa moderator**.

**CARA BENAR:** kirim **`peran`** saja (seperti halaman). Jangan kirim
`kolom_x/kolom_m/kolom_z` sekaligus saat sudah mengirim `peran`.

**TANDA PENGENAL di hasil:** `z_kovariat` berisi nama kolom MENTAH
(`['Z1b','Z2a','Z2b']`) = jalur salah. Kalau benar: `['Z2']`.

---

## 🔴 K-22 — HALAMAN MENAMPILKAN **F** DI KOLOM "NILAI" (ketemu MATA, 22Sep26)

**Kejadian:** tabel "Statistik uji" MANOVA menampilkan
`Wilks = 28,369` dan `Pillai = 57,224` — **Pillai mustahil > 1**.

**Akar:** `kartuUjiManova(nm, q)` mengisi kolom "Nilai" dengan **`q.F`**.
Dua hal BERBEDA tercampur: (a) **nilai ukuran statistik** (Wilks/Pillai ∈ [0,1]),
(b) **hasil uji F** atas ukuran itu. Mesinnya BENAR — catatan kaki di halaman
sudah menunjukkan angka benar (0,67342 · 0,32658 · 0,48495).

**KENAPA UJI TEKS LOLOS:** uji Wulan hanya memeriksa *"ada 18 angka desimal"*,
tidak memeriksa **angka mana** yang benar. 22 asersi hijau, bug tetap lolos.

**CARA BENAR:** kolom "Nilai" = `r.statistik.wilks/pillai/...`; kolom F & p =
`r.uji.*`. **TAMBAHAN WAJIB di uji:** nilai Pillai & Wilks ∈ [0,1] dan
`Nilai ≠ F`.

---

## 🔴 K-23 — `df` TIDAK DILAPORKAN (halaman tampil "—, —", 22Sep26)

**Kejadian:** kolom df kosong untuk Pillai, Hotelling, Roy (hanya Wilks ada).
Ditemukan **MATA**, bukan uji.

**Akar:** `_f_dari_statistik()` **memakai** df `(k-1)·p, (n-k)·p` untuk
menghitung p, tapi **tidak menyimpan** `df1`/`df2` ke hasil → halaman jatuh
ke `'—'`. Mesinnya BENAR; yang hilang cuma **laporan** df-nya.

**CARA BENAR:** setiap `{'F','p'}` WAJIB disertai `{'df1','df2'}`.
Ada penjaga di `uji_manova.py` bagian [15].

---

## 🔴 K-24 — GERBANG BAHASA GAGAL PALSU: KOMENTAR JINJA `{# #}` DIHITUNG

**Kejadian:** `gerbang_bahasa.py` menolak `buat_data.html` karena kata
"pagar" — padahal kata itu ada di **komentar Jinja** `{# … #}` yang
**hilang saat template dirender**. Halaman bersih (dibuktikan: hasil render
memuat **0** kata itu, berkas mentah memuat 1).

**Akar:** `ambil_teks_tampil()` membuang `<script>`, `<style>`, `<tag>`,
`{{ }}`, `{% %}` — **TIDAK membuang `{# #}`**.

**CARA BENAR:** buang `{# … #}` **lebih dulu** (paling luar) sebelum yang lain.

**PELAJARAN cara kerja:** Wulan **hampir menuduh gerbangnya rusak**. Dicek
dulu (`curl` + grep ke hasil render) → ternyata gerbang **BENAR** untuk
6 kemunculan lain (id elemen + komentar JS yang IKUT terkirim ke browser).
**Buktikan dulu, baru menuduh** — dan perbaikan tetap di akar
(nama id `pagar-${i}` → `perkiraan-${i}`).
Bukti bergigi: `_sketsa/bukti_bahasa_bergigi.py` (6 LULUS — menolak cacat
nyata, tidak menuduh komentar).

---

## 🔴 K-25 — VERIFIKASI MENUNTUT BENTUK YANG **DITEBAK** → "GAGAL" PALSU (22Sep26)

**Kejadian:** uji verifikasi produksi melaporkan **"produksi TIDAK memuat
perbaikan"** padahal **KODE PRODUKSI BENAR** (diperiksa langsung: perbaikannya ADA).

**2 kesalahan berturut-turut di titik yang sama:**
1. Menuntut `r.statistik[` di JS — padahal bentuk sebenarnya nama **parameter**
   `kartuUjiManova(nm, q, nilaiStat)`. Nama variabelnya beda, maksudnya sama.
2. `kode.split('\\n')` di dalam string bertingkat → jadi **literal `\n`**, bukan
   newline → keluaran dianggap SATU baris → selalu "melanggar".

**CARA BENAR:** **CETAK dulu** bentuk/isi sebenarnya (`print(repr(...))`), baru
tulis syaratnya. Untuk pecah baris di skrip bertingkat → pakai **`chr(10)`**.
**Aturan induk ini persis sama** dengan aturan "grep nama kelas/ikon dulu" dan
"cetak jawaban server dulu" — **jangan tuntut bentuk yang ditebak.**

Bukti akhir: `_sketsa/verifikasi_produksi_manova.py` **9 LULUS / 0 GAGAL**.

---

## ⛔ YANG HARAM DI PROYEK INI (dari Bos)

| Larangan | Sebab |
|---|---|
| **Suntik / tambal** | menyembunyikan akar; akar akan muncul lagi di tempat lain |
| **Bikin berkas/aturan baru tanpa diminta** | Wulan pernah bikin `ATURAN_GERBANG.md` → **dihapus** |
| **Ubah yang TIDAK salah** | Bos: *"jangan ubah yang tidak salah"* |
| **Kredensial di kode/dokumen/skill** | token hanya di `.env`; tulis `<nilai-A>` |
| **Uji tanpa bukti bisa GAGAL** | penjaga buta lebih buruk daripada tidak ada penjaga |
| **Percobaan ke-3 dengan cara sama** | itu menambal — STOP di percobaan ke-2 |
| **`pkill` pola lebar** | mematikan shell sendiri (SIGTERM) |

---

## ✅ URUTAN KERJA YANG BENAR (ringkas)

```
1. BACA BERKAS UTUH — jangan menebak isi/struktur
2. CEK PRASARANA   — Chrome :9333 & server :8122 hidup?
3. CETAK JAWABAN   — kunci-kunci server, sebelum menulis uji
4. HITUNG SENDIRI  — angka yang seharusnya, dari sumbernya
5. PERBAIKI AKAR   — satu tempat, jangan ditulis dua kali
6. UJI 2 ARAH      — sehat LULUS + dirusak HARUS GAGAL
7. SOT --periksa   — dokumen selaras dengan kode
8. GERBANG PENUH   — semua grup hijau, EXIT 0
9. LAPOR JUJUR     — sebut yang BELUM, jangan bilang "sempurna"
```
