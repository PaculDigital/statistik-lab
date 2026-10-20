# FLAG — posisi kerja terakhir

> 📌 **Angka status (grup gerbang, deploy, domain) TIDAK ditulis di sini.**
> Itu milik **`STATUS.md`** dan `sot.py`. Berkas ini hanya menjawab:
> *"sedang di mana kita, dan apa yang menunggu?"*

---

## 🛑 TITIK HENTI — 22 Sep 2026

Kata Bos waktu itu: *"saya cukup dulu sampai disini, kita lanjut kapan kapan"*.
Semua pekerjaan sesi 22Sep26 **SELESAI & LIVE**. Tidak ada yang menggantung separuh.

**Ditandai ulang 20 Okt 2026** — Bos minta dokumentasi dirapikan agar SOT.
Tidak ada perubahan kode pada 20 Okt.

---

## 🔖 CARA BALIK (kalau Bos bilang *"lanjut statistik"* / *"buka flag"*)

```bash
cd /opt/data/services/statistik-lab
read STATUS.md                        # 1. status resmi + peta dokumen
.venv/bin/python sot.py               # 2. keadaan terkini DIHITUNG dari kode
.venv/bin/python sot.py --periksa     # 3. dokumen selaras kode?
bash gerbang_uji.sh                   # 4. gerbang penuh, EXIT 0 = aman
```

**Prasarana dulu (jangan lupa) — Chrome CDP wajib hidup:**
```bash
curl -s -o /dev/null -w "9333 -> %{http_code}\n" --max-time 4 http://127.0.0.1:9333/json/version
```
Kalau mati: nyalakan lewat `terminal(background=true)` Hermes — **JANGAN**
`pkill`, **JANGAN** coba menyalakan sendiri (semua cara gagal, lihat skill).

---

## ✅ YANG SUDAH SELESAI (jangan dikerjakan ulang)

- Mesin simulasi data — semua bentuk model yang tercantum di `sot.py`
- Web: beranda · `/kuantitatif` · `/belajar` (3 tab) · `/buat-data` · `/diagnosis` ·
  `/pengaturan` · `/segera/<slug>`
- Diagnosis SPSS (6 uji) + PLS (5 uji) + 11 nasihat
- MANOVA — kartu ke-5 "Banding kelompok" (bahasan **DITUTUP**)
- Pemilihan kartu Parsial vs Berganda + uji F + tabel ANOVA
- Grafik hidup + tab "Baca Grafik"
- Identifikasi data: peran kolom → skor konstruk (Opsi B, jawaban kosong)

Riwayat lengkap tiap tahap ada di **`arsip/`** (beku, jangan jadi acuan).

---

## ⏭️ MENUNGGU PUTUSAN BOS — JANGAN mulai sendiri

| # | Hal | Perlu apa |
|---|---|---|
| 1 | **Mardia p=0,0000** ("tidak normal") | Wajar untuk data berkelompok, tapi mahasiswa perlu penjelasan supaya tidak dikira data rusak |
| 2 | **12 uji mati "PENINGGALAN"** | Putusan Bos: **hapus** atau pelihara? |
| 3 | **Potret mata terbaru** | Sudah diperiksa mata 1× (df terisi); potret final menyusul |
| 4 | `RUANG_MANOVA.md` §8b–8d | Masih berlaku sebagai catatan; bahasan MANOVA **DITUTUP** — jangan koding tanpa Bos buka |

---

## 📚 WAJIB DIBACA SEBELUM LANJUT

1. `STATUS.md` — status resmi + peta dokumen
2. `CATATAN_KESALAHAN_21SEP2026.md` — **K-01…K-25**, kesalahan + cara betulnya
3. `MASTER_PLAN.md` — keputusan terkunci
4. Skill `statistik-lab` — cara kerja + jebakan (angka ikut `STATUS.md`, bukan skill)
