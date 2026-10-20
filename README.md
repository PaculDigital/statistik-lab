# Penelitian STATISTIK Lab

Mesin simulasi data penelitian + antarmuka web untuk latihan dan olah data
statistik (deskriptif sampai uji lanjutan). FastAPI + Jinja2, tanpa dependensi
frontend.

**Status & angka grup gerbang:** lihat **`STATUS.md`** — satu-satunya tempat
angka resmi. Atau jalankan `.venv/bin/python sot.py` (menghitung dari kode).

---

## 📍 Mulai dari mana?

| Kalau Bos mau… | Baca |
|---|---|
| tahu **status & angka** sekarang | `STATUS.md` |
| tahu **sedang di mana** pekerjaan | `FLAG_LANJUT_DISINI.md` |
| tahu **keputusan yang sudah dikunci** | `MASTER_PLAN.md` |
| tahu **kesalahan yang jangan diulang** | `CATATAN_KESALAHAN_21SEP2026.md` |
| tahu **cara kerja & jebakan teknis** | skill `statistik-lab` |
| lihat **riwayat tahap lama** | `arsip/` (beku, jangan jadi acuan) |

## Perintah harian

```bash
cd /opt/data/services/statistik-lab
.venv/bin/python sot.py              # keadaan terkini DIHITUNG dari kode
.venv/bin/python sot.py --periksa    # dokumen selaras kode? (EXIT 0 = ya)
bash gerbang_uji.sh                  # gerbang penuh (EXIT 0 = aman)
bash jalankan.sh                     # deploy produksi
```

---

## Isi Repo

| Folder | Isi |
|---|---|
| `app/` | Aplikasi FastAPI — `main.py` (rute), `hitung/` (mesin statistik), `templates/` (Jinja2), `static/` (CSS/JS/ikon) |
| `scripts/` | Pembangkit sprite ikon & alat bantu |
| `_sketsa/` | Skrip eksperimen / potongan kerja |
| `_arsip/` | Mockup lama yang disimpan sebagai rujukan |
| `arsip/` | **Dokumen tahap lama — BEKU**, jangan jadi acuan |
| root `*.py` | Gerbang uji & alat ukur (`gerbang_*.py`, `uji_*.py`, `ukur_*.py`, `audit_*.py`) |
| root `*.md` | Dokumen aktif: status, keputusan, catatan |

## Teknologi

- Python 3.13
- FastAPI 0.115.6 + Uvicorn 0.34.0
- Jinja2 3.1.5
- numpy 2.2.1, scipy 1.15.1, pandas 2.2.3
- openpyxl 3.1.5 (baca/tulis Excel), pyreadstat 1.2.9 (baca SPSS `.sav` / Stata)

## Menjalankan

### Pakai Docker (cara produksi)

```bash
bash jalankan.sh
```

Skrip ini menjalankan gerbang uji dulu, membangun image bertag, lalu menyalakan
kontainer. Port host **8120** → kontainer 8000.

### Pakai uv / venv (pengembangan)

```bash
python3 -m venv .venv
.venv/bin/pip install fastapi==0.115.6 "uvicorn[standard]==0.34.0" \
  jinja2==3.1.5 python-multipart==0.0.20 numpy==2.2.1 scipy==1.15.1 \
  pandas==2.2.3 openpyxl==3.1.5 pyreadstat==1.2.9
.venv/bin/uvicorn app.main:app --reload --port 8000
```

Buka `http://localhost:8000`.

## Gerbang Uji

Repo ini memakai pendekatan **gerbang**: setiap perubahan wajib lulus
sekumpulan skrip uji sebelum deploy.

```bash
bash gerbang_uji.sh
```

Jenis gerbang yang ada:

- `gerbang_bahasa.py` — konsistensi bahasa antarmuka
- `gerbang_tag_skrip.py` / `gerbang_sintaks_js.py` — validitas template & JavaScript
- `gerbang_ikon.py` — nama ikon benar-benar ada di sprite
- `gerbang_semua_model.py`, `gerbang_s3.py` — model statistik & kalibrasi S3
- `gerbang_galat_js.py`, `gerbang_panah_berhimpit.py` — regresi tampilan
- `uji_*.py` — uji perilaku per fitur (variabel, SPSS, grafik, halaman, dsb.)
- `ukur_*.py` — alat ukur kecepatan, deteksi judul, kualitas gambar

**Jumlah grup & asersi:** lihat `STATUS.md` (tidak ditulis di sini — cepat basi).

## Aturan dokumentasi

Lihat `STATUS.md` bagian *"Aturan penulisan dokumen"*. Ringkasnya:

1. Angka status **hanya** di `STATUS.md`
2. Dokumen di `arsip/` **jangan diubah**
3. Dokumen baru **wajib didaftarkan** di peta dokumen `STATUS.md`
4. Ubah dokumen → **wajib** `.venv/bin/python sot.py --periksa`

## Catatan

- `.venv/`, `__pycache__/`, `data/*.pkl`, dan berkas rahasia dikecualikan lewat `.gitignore`.
- File berakhiran `.cadangan*` adalah cadangan versi sebelumnya, disengaja ikut tersimpan sebagai jejak perubahan.
- `Dockerfile` berisi pin versi dependensi — samakan bila menambah pustaka baru.

## Lisensi

Belum ditetapkan. Kontak pemilik repo untuk penggunaan.
