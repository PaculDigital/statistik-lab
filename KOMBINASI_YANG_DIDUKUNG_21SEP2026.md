# 🧩 KOMBINASI YANG BISA DIKERJAKAN MESIN — hasil UKUR, bukan klaim
## 21 September 2026 · terukur lewat PINTU PRODUKSI (`uji_kombinasi.py`)

Pertanyaan Bos: *"Jadi sekarang bisa kombinasi apa saja? Banyak x, banyak m,
banyak z, banyak y dan bisa kombinasi model? / Lebih ke fleksibel?"*

Jawaban singkat: **YA, fleksibel** — mesin tidak punya "jenis model". Mesin
menerima **DAFTAR JALUR** ("siapa memengaruhi siapa"). Yang perlu diperiksa
cuma **tanda peran kolom** (X/M/Z/Y).

---

## 1. Yang Terukur (9 LULUS / 0 GAGAL)

| # | Kombinasi | Hasil terukur |
|---|---|---|
| 1 | Banyak **X** (X1,X2,X3) + banyak **M** (M1,M2) | prediktor `['X1','X2','X3','M1','M2']` ✅ |
| 2 | Banyak **M paralel** | mediasi **2** hasil (M1 & M2) ✅ |
| 3 | Banyak **Y** (Y1,Y2) | diterima, dipakai **Y terakhir** ✅ |
| 4 | Banyak **Z** (Z1,Z2) | moderasi **2** hasil ✅ |
| 5 | **Z lain dikendalikan** (Opsi A) | `Z1 kov=['Z2']` · `Z2 kov=['Z1']` ✅ |
| 6 | **Mediasi + moderasi sekaligus** | med=2 · mod=2 dari **SATU** kiriman ✅ |
| 7 | Banyak X + M + Z + Y **bersamaan** | semua masuk, tidak ada yang dibuang ✅ |
| 8 | R² regresi (banyak X+M) | **0,4474** ✅ |
| 9 | Y banyak → satu per kiriman | mesin pakai **Y terakhir** ✅ |

---

## 2. Peta: apa yang BOLEH banyak

| Variabel | Boleh banyak? | Catatan |
|---|---|---|
| **X** (bebas) | ✅ ya | X2..Xk masuk **sebagai kovariat dikendalikan** |
| **M** (perantara) | ✅ ya | paralel (sejajar) **dan** berjenjang (bertingkat) |
| **Z** (penguat) | ✅ ya | Z lain otomatis **dikendalikan** (Opsi A) |
| **Y** (terikat) | ⚠️ **satu per kiriman** | ganti tanda Y → hasil Y berikutnya |

---

## 3. Model yang bisa DISUSUN

| Model | Keadaan |
|---|---|
| Regresi sederhana / berganda | ✅ |
| Mediasi (1 perantara) | ✅ |
| Mediasi **banyak perantara** | ✅ paralel + berjenjang + **rantai >2** |
| Moderasi (MRA) | ✅ |
| **Moderasi banyak X & banyak Z** | ✅ **Opsi A** (Z lain dikendalikan) |
| **Mediasi + Moderasi campuran** | ✅ sekaligus |
| Banyak **X + M + Z + Y** | ✅ |
| Rantai panjang (4 perantara) | ✅ |

---

## 4. Yang BELUM — jujur

| Hal | Sebab |
|---|---|
| **MANOVA** (uji 3 Y **serentak**) | ruang MANOVA sudah dipesan (R1 sudah disiapkan), **belum dibuka** Bos |
| **Y banyak serentak** | mesin pakai Y terakhir; buat Y lain → ganti tanda |
| **PLS mode banyak X/M/Z/Y** | uji ini mode **SPSS**; PLS punya jalur sendiri |
| **Kualitatif** | mesinnya belum ada |

⚠️ **Penting (statistik):** kalau Y banyak, **pembimbing** biasanya minta
**MANOVA** (regresi terpisah = galat tipe I membengkak). Aplikasi **wajib**
memberi peringatan ini.

---

## 5. Cara menguji ulang

```bash
cd /opt/data/services/statistik-lab
.venv/bin/python uji_kombinasi.py          # 9 uji → EXIT 0
```

Terdaftar di gerbang: grup **`KOMBINASI — banyak X+M+Z+Y & campuran
mediasi+moderasi`**.

**Bukti bisa gagal (wajib):** cacat lama dipasang kembali (Z lain tidak
dikendalikan) → uji **EXIT 1** dengan
`❌ Z lain jadi kovariat (Opsi A)   Z1 kov=[] Z2 kov=[]`.

---

## 6. Pelajaran uji (jangan ulang)

| # | Pelajaran |
|---|---|
| **K-19** | Kirim **`peran`** saja. Jangan kirim `kolom_z` berisi nama konstruk (`'Z1'`) — isinya MENIMPA hasil gabungan peran → moderasi kosong. |
| **K-20** | Unggah berkas: field **`name="berkas"` + filename** + `csv.writer`. Nama field salah → **HTTP 422**. |
| **K-21** | Modul uji WAJIB berbungkus `if __name__ == '__main__':` — kalau tidak, `import` menjalankan ujinya sendiri. |
