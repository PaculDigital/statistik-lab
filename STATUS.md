# STATUS — Penelitian STATISTIK Lab.

**Berkas ini SATU-SATUNYA tempat angka dan status proyek boleh ditulis.**
Dokumen lain **DILARANG** memuat angka grup gerbang, jumlah asersi, atau status
deploy — mereka cukup menautkan ke sini.

> ⚠️ **Di atas berkas ini masih ada satu sumber lebih tinggi: KODE DI DISK.**
> Kalau berkas ini berbeda dengan kode → **KODE YANG MENANG**, berkas ini yang
> diperbaiki. Selalu jalankan `.venv/bin/python sot.py` untuk keadaan terkini.

---

## Keadaan terkini

**Angka di bawah dihitung dari kode pada 20 Oktober 2026. Jangan dihafal.**

| Hal | Nilai |
|---|---|
| Grup gerbang uji | **dihitung otomatis** oleh `sot.py` dari `gerbang_uji.py` — jangan ditulis manual di sini |
| Kontainer | `simulasi-olah-data` · port **8120 → 8000** |
| Domain | **`statistik.bikinaja.id`** — LIVE ✅ |
| Deploy | **WAJIB** `bash jalankan.sh` (gerbang → build → ganti kontainer → `/health` → **uji SEO pasca-deploy**) |
| SOT | `sot.py` = gerbang uji **nomor 1** (`--periksa` → EXIT ≠ 0 kalau dokumen melenceng) |

### ⚠️ Uji SEO sengaja PASCA-deploy (putusan Bos 20Okt26, opsi A)

`uji_seo.py` mengukur **KONTAINER**. Kalau dijalankan di gerbang pra-deploy, ia
menilai kontainer **LAMA** → GAGAL PALSU (terukur: 53 GAGAL padahal kode sudah
benar 65/65 di server uji :8122) → deploy selalu dibatalkan.

⇒ Urutan benar: gerbang (tanpa SEO) → build → ganti kontainer → `/health`
→ **`uji_seo.py` pada kontainer hidup** (`jalankan.sh` langkah **5b**).
Uji **bergigi**-nya (`_sketsa/bukti_uji_seo_gagal.py`) tetap di gerbang sebab
ia memakai server sendiri (:8199) — jadi penjaminnya tidak hilang.

**Selalu periksa sendiri, jangan percaya tabel di atas:**

```bash
cd /opt/data/services/statistik-lab
.venv/bin/python sot.py              # keadaan terkini DIHITUNG dari kode
.venv/bin/python sot.py --periksa    # dokumen selaras kode?
bash gerbang_uji.sh                  # gerbang penuh, EXIT 0 = aman
```

---

## Urutan kekuatan sumber (dari paling benar)

| # | Sumber | Sifat | Boleh memuat angka? |
|---|---|---|---|
| 1 | **Kode di disk** (`app/`, `gerbang_uji.py`, `sot.py`) | **KEBENARAN** | ya — ini sumbernya |
| 2 | `STATUS.md` (berkas ini) | salinan resmi | **ya, hanya di sini** |
| 3 | `MASTER_PLAN.md` | keputusan terkunci | tidak — tautkan ke sini |
| 4 | `FLAG_LANJUT_DISINI.md` | posisi kerja terakhir | tidak — tautkan ke sini |
| 5 | `arsip/*.md` | riwayat, **BEKU** | tidak — dibekukan apa adanya |
| 6 | skill `statistik-lab` + `references/` | cara kerja | tidak — tautkan ke sini |

---

## Peta dokumen

### Aktif — wajib dibaca sebelum kerja

| Berkas | Isi |
|---|---|
| `STATUS.md` | **berkas ini** — status & angka resmi |
| `MASTER_PLAN.md` | keputusan terkunci, peta jalan tahap |
| `FLAG_LANJUT_DISINI.md` | posisi kerja terakhir (blok teratas) |
| `README.md` | pintu masuk repo: teknologi, cara jalan, daftar gerbang |
| `CATATAN_KESALAHAN_21SEP2026.md` | **K-01…K-25** — kesalahan + cara betulnya (WAJIB) |

### Aktif — berkas uji penjaga (baru 20Okt26)

| Berkas | Isi |
|---|---|
| `uji_seo.py` | **uji favicon · sitemap · robots · meta description** (65 asersi) |
| `uji_atribusi_footer.py` | **uji brand "Powered by" di footer** (23 asersi, 8 halaman) |
| `_sketsa/bukti_uji_seo_gagal.py` | bukti uji SEO BISA GAGAL (3 suntikan tertangkap) |
| `_sketsa/bukti_varian_ui_berfungsi.py` | bukti 9 varian jalur jalan (klik nyata) |
| `_sketsa/bukti_penjaga_dokumen.py` | bukti penjaga SOT BISA GAGAL (5 suntikan) |

### Aktif — rujukan keputusan (masih berlaku)

| Berkas | Isi |
|---|---|
| `RUANG_MANOVA.md` | catatan MANOVA — **bahasan DITUTUP**, jangan koding tanpa izin Bos |
| `KEPUTUSAN_PARSIAL_SIMULTAN_21SEP2026.md` | keputusan kartu Parsial vs Berganda |
| `TEMUAN_MEDIASI_MODERASI_21SEP2026.md` | temuan terukur mesin |
| `CATATAN_DISKUSI_VALIDITAS_12_UJI.md` | diskusi validitas 12 uji |
| `CATATAN_DISKUSI_GERBANG_MODEL_Y_GANDA.md` | diskusi gerbang model Y ganda |
| `CATATAN_JEMBATAN_BAB4_FASE1_21OKT2026.md` | jembatan BAB IV Fase 1 — pintu hitung antar-layanan + vonis review |
| `CATATAN_BUG_BUAT_DATA_22OKT2026.md` | 5 temuan review Buat Data (BUG-1…BUG-5) + bukti & akar |
| `CACAT_MEDIASI_X_BANYAK_21SEP2026.md` | catatan cacat mediasi X banyak |
| `AUDIT_UJI_LUAR_GERBANG_21SEP2026.md` | audit uji di luar gerbang |
| `KOMBINASI_YANG_DIDUKUNG_21SEP2026.md` | kombinasi model yang didukung |
| `RANCANGAN_SEMUA_MODEL_DI_WEB.md` | rancangan peta model di web |
| `KANVAS_MODEL_RANCANGAN.md` | kanvas rancangan |

### Arsip — riwayat, **BEKU** (jangan jadi acuan)

Dipindah ke `arsip/`. Isinya **riwayat tahap yang sudah selesai**, angka di
dalamnya **usang dengan sengaja** dan **tidak boleh diperbaiki** — kalau
diperbaiki, riwayatnya hilang.

| Berkas | Tahap |
|---|---|
| `arsip/DOKUMENTASI_MESIN_DATA_17SEP2026.md` | mesin data — 18 putaran |
| `arsip/DOKUMENTASI_SOT_AUDIT_18SEP2026.md` | audit SOT pertama |
| `arsip/DOKUMENTASI_TAHAP_1_3_19SEP2026.md` | tahap 1.3 — sub-pilihan model |
| `arsip/DOKUMENTASI_TAHAP_1_4_19SEP2026.md` | tahap 1.4 — bar model |
| `arsip/DOKUMENTASI_TAHAP_1_5_DIAGNOSIS_19SEP2026.md` | tahap 1.5 — diagnosis SPSS/PLS |
| `arsip/DOKUMENTASI_KEPUTUSAN_DIAGNOSIS_19SEP2026.md` | keputusan diagnosis |
| `arsip/DOKUMENTASI_KARTU_UJI_T_19SEP2026.md` | kartu uji t |
| `arsip/DOKUMENTASI_TAHAP_1_6_NORMALITAS_20SEP2026.md` | tahap 1.6 — normalitas |
| `arsip/DOKUMENTASI_TAHAP_2_GRAFIK_HIDUP_20SEP2026.md` | tahap 2 — grafik hidup |
| `arsip/TAHAP_PENYELESAIAN.md` | peta jalan 7 tahap (snapshot lama) |

---

## Aturan penulisan dokumen

1. **Angka status HANYA di `STATUS.md`.** Dokumen lain menulis
   *"lihat `STATUS.md`"*.
2. **Dokumen arsip JANGAN diubah.** Kalau perlu dikoreksi, tulis berkas baru
   di root dan tautkan.
3. **Setiap dokumen baru wajib didaftarkan** di peta dokumen di atas.
4. **Ubah dokumen → WAJIB jalankan `sot.py --periksa`.** EXIT ≠ 0 = dokumen
   berbohong, perbaiki dokumennya (bukan `sot.py`).
5. **Riwayat angka tetap boleh ada** asalkan ditandai jelas dengan konteks
   waktu (*"saat itu"*, *"keadaan 20 Sep"*) — `sot.py` sengaja melewatinya.
