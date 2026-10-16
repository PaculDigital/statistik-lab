# 🔴 CACAT NYATA — MEDIASI & MODERASI HANYA PAKAI **X PERTAMA**
## 21 September 2026 · hasil ukur lewat PINTU PRODUKSI

> ## ✅ STATUS: **SUDAH DIPERBAIKI — 21Sep26** (ACC Bos: *"Semua x masuk"* + *"Opsi A"*)
>
> **Perbaikan 2 tahap:**
> 1. **Banyak X** (ACC "Semua x masuk") — `mediasi_banyak_x` & `moderasi_banyak_x`:
>    X2..Xk masuk sebagai **kovariat yang DIKENDALIKAN** (bukan dibuang).
> 2. **Banyak Z** (ACC "Opsi A") — `z_lain`: Z lain juga **dikendalikan**.
>    Terukur: ΔR² Z1 **0,135607 → 0,133066** saat Z2 dikendalikan.
>    Tanpa ini, hasil Z1 SAMA PERSIS entah Z2 ada atau tidak.
>
> **CATATAN PENTING:** mahasiswa menandai `Z1` = **beberapa kolom** (Z1a, Z1b)
> → digabung jadi **satu** moderator oleh `_gabung_peran()`. Jangan kirim
> `kolom_z` berisi nama konstruk (`'Z1'`) — nilainya MENIMPA hasil gabungan
> dan moderasi jadi kosong (K-19).
>
> **Cara membetulkan:** X2..Xk **masuk sebagai kovariat yang DIKENDALIKAN**
> (bukan dibuang). Fungsi baru: `mediasi_banyak_x()`, `mediasi_rantai_banyak_x()`,
> `moderasi_banyak_x()` di `app/hitung/kaitan.py` — dipisah supaya fungsi lama
> (terbukti benar) **tidak disentuh**.
>
> **Bukti telak:** p jalur a X1 bergeser **0,057 → 0,387** setelah X2
> dikendalikan (dulu X1 kelihatan hampir signifikan — menyesatkan).
>
> **Tidak merusak yang lama:** dengan 1 X, hasil **sama persis**
> (0,579463 = 0,579463).
>
> **Terbukti bisa gagal:** `kolom_x[0]` dikembalikan → **6 kegagalan** ditangkap.
>
> **Uji baru:** `uji_banyak_x.py` (21 uji) · `uji_ukur_xmy_banyak.py`
> (pintu produksi, 19 uji). Gerbang **51 → 53 grup**.

---

> **Pertanyaan Bos:** *"Tanya apakah sudah support x1, x2, x3 dst. M1, m2 dst.
> Terhadap y1, y2, y3"*
>
> **Jawaban waktu itu: BELUM SEMUA.** Wulan uji langsung lewat pintu produksi
> (unggah `.csv` → tandai peran → Hasil), **bukan** dari ingatan.

---

## ✅ KEADAAN SEKARANG (21Sep26, setelah perbaikan)

| Bagian | Keadaan | Bukti terukur |
|---|---|---|
| Banyak **X** di **regresi biasa** | ✅ DIDUKUNG | `prediktor = ['X1','X2','X3','M1','M2']` |
| Banyak **X** di **MEDIASI** | ✅ **DIPERBAIKI** | `x_semua=['X1','X2','X3']` · ket *"dengan X2, X3 dikendalikan"* |
| Banyak **X** di **MODERASI** | ✅ **DIPERBAIKI** | moderasi `x_semua=['X1','X2','X3']`, jenis `memoderasi` |
| Banyak **M** (paralel) | ✅ DIDUKUNG | 2 hasil mediasi keluar (`M1`, `M2`) |
| Banyak **M** (berjenjang) | ✅ DIDUKUNG | 2 jalur: `X1→M1→Y1`, `X1→M1→M2→Y1` |
| Rantai **>2 perantara** | ✅ DIDUKUNG | 3 & 4 perantara (uji 21Sep26) |
| Banyak **Y** (satu-satu) | ✅ DIDUKUNG | R² Y1=0,3512 · Y2=0,334 · Y3=0,252 (beda, tidak ditimpa) |
| Banyak **kolom per peran** | ✅ DIDUKUNG | X1 = 3 kolom → digabung 1 skor |
| **Z** | ✅ DIDUKUNG | moderasi keluar + X lain dikendalikan |

⚠️ **Catatan (bukan cacat):** kalau mahasiswa menandai Y1, Y2, Y3 **sekaligus**,
mesin mengerjakan **Y TERAKHIR** sebagai Y utama (`app/main.py:470-472`,
`kolom_y = y_peran[-1]`). Y lain diuji dengan menandainya sendiri — sudah
dibuktikan benar (R² tiga-tiganya beda).

---

## 🔴 CACAT YANG DULU ADA (disimpan sebagai pelajaran)

### Mediasi & moderasi **HANYA memakai X PERTAMA**

Terukur: `kaitan.mediasi[0].x = "X1"` — **bukan** `['X1','X2','X3']`.

Artinya kalau mahasiswa tandai **X1, X2, X3** dan minta mediasi,
mesin menghitung mediasi **hanya dari X1**. **X2 dan X3 tidak dipakai.**

**Akarnya (terbaca dari kode, 4 tempat — bukan tebakan):**

| Berkas : baris | Kode | Akibat |
|---|---|---|
| `kaitan.py:553` | `mediasi(df, kolom_x[0], …)` | mediasi tunggal pakai X1 saja |
| `kaitan.py:565` | `mediasi_rantai(df, kolom_x[0], …)` | rantai pakai X1 saja |
| `kaitan.py:569` | `mediasi(df, kolom_x[0], m, …)` | paralel pakai X1 saja |
| `kaitan.py:573` | `moderasi(df, kolom_x[0], z, …)` | moderasi X1 saja |

Dan tanda tangan keempat fungsi itu menerima **satu** X:
`def mediasi(df, x: str, m, y)` · `def moderasi(df, x: str, z, y)`.

### Z di mode SPSS tidak muncul di daftar `penguat`

Moderasi **dihitung** (keluar 1 hasil), tapi `kaitan.penguat` **kosong**.
Halaman membaca daftar itu → kartu moderasi bisa tidak tampil utuh.

---

## 🎯 APA ARTINYA UNTUK MAHASISWA

| Model yang dipakai | Sekarang |
|---|---|
| Regresi sederhana/berganda 3 X | ✅ benar |
| Mediasi 1 X → M → Y | ✅ benar |
| Mediasi 3 X → M → Y | 🔴 **hanya X1** — X2, X3 diam-diam dibuang |
| Moderasi 3 X × Z → Y | 🔴 **hanya X1** |
| Y banyak (Y1,Y2,Y3) | ✅ bisa, diuji satu-satu |

⚠️ **Bahaya terbesar:** mahasiswa tidak akan tahu X2 dan X3 dibuang —
hasilnya **kelihatan sah**. Ini persis jenis cacat yang paling menyesatkan.

---

## 🙋 YANG WULAN BUTUH DARI BOS (keputusan statistik)

Wulan **belum menyentuh kode**. Ada 2 cara membetulkan, dan **beda artinya
secara statistik** — jadi harus Bos yang putuskan:

| # | Opsi | Artinya | Risiko |
|---|---|---|---|
| **A** ⭐ | **Semua X masuk** | jalur **a** = X1,X2,X3 **bersama-sama** → M; jalur **b** = M → Y dengan X1..X3 dikendalikan | perlu uji ulang semua; hasil berubah |
| **B** | **Protes jujur** | kalau X lebih dari satu, mesin bilang *"medisi butuh satu X — pilih yang mana"* | tidak menyesatkan, tapi menambah 1 pertanyaan |
| **C** | **A + tampilkan** | semua X masuk **dan** kartu menulis *"X2, X3 ikut dikendalikan"* | paling jujur, kerja paling banyak |

⚠️ **Catatan:** pilihan ini **bukan soal kode**, tapi soal **definisi
statistik** — apakah mediasi dengan beberapa X itu *"X1..X3 bersama-sama"*
atau *"tiap X punya jalur sendiri"*. Wulan tidak boleh memutuskan sendiri.

---

## 📌 CARA WULAN MENEMUKANNYA

Pertanyaan Bos → Wulan **uji langsung**, tidak menjawab dari ingatan.
Uji: `uji_ukur_xmy_banyak.py` (3 X + 2 M + 1 Y · 3 X + 1 M + 3 Y ·
3 X + 2 M + 2 Y + Z) lewat rute HTTP sungguhan.

**Pelajaran:** cacat ini **tidak akan pernah ketahuan** dari uji lama —
karena semua uji lama memakai **satu X**. Butuh pertanyaan Bos untuk
membukanya. (Kelas yang sama dengan K-09: *ukur dari pintu produksi,
dengan bentuk yang belum pernah diuji*.)
