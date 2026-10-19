# Penelitian STATISTIK Lab

Mesin simulasi data penelitian + antarmuka web untuk latihan dan olah data statistik (deskriptif sampai uji lanjutan). FastAPI + Jinja2, tanpa dependensi frontend.

**Status:** commit `07c1a38` — 437 berkas, 60 grup gerbang uji LULUS.

---

## Isi Repo

| Folder | Isi |
|---|---|
| `app/` | Aplikasi FastAPI — `main.py` (rute), `hitung/` (mesin statistik), `templates/` (Jinja2), `static/` (CSS/JS/ikon) |
| `scripts/` | Pembangkit sprite ikon & alat bantu |
| `_sketsa/` | Skrip eksperimen / potongan kerja |
| `_arsip/` | Mockup lama yang disimpan sebagai rujukan |
| root `*.py` | ±40 gerbang uji & alat ukur (`gerbang_*.py`, `uji_*.py`, `ukur_*.py`, `audit_*.py`) |
| root `*.md` | Dokumentasi keputusan, audit, dan catatan diagnosis |

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

Skrip ini menjalankan gerbang uji dulu, membangun image bertag, lalu menyalakan kontainer. Port host **8120** → kontainer 8000.

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

Repo ini memakai pendekatan **gerbang**: setiap perubahan wajib lulus sekumpulan skrip uji sebelum deploy. Jalankan semuanya:

```bash
bash gerbang_uji.sh
```

Jenis gerbang yang ada:

- `gerbang_bahasa.py` — konsistensi bahasa antarmuka
- `gerbang_tag_skrip.py` / `gerbang_sintaks_js.py` — validitas template & JavaScript
- `gerbang_semua_model.py`, `gerbang_s3.py` — model statistik & kalibrasi S3
- `gerbang_galat_js.py`, `gerbang_panah_berhimpit.py` — regresi tampilan
- `uji_*.py` — uji perilaku per fitur (variabel, SPSS, grafik, halaman, dsb.)
- `ukur_*.py` — alat ukur kecepatan, deteksi judul, kualitas gambar

## Catatan

- `.venv/`, `__pycache__/`, `data/*.pkl`, dan berkas rahasia sudah dikecualikan lewat `.gitignore`.
- File berakhiran `.cadangan*` adalah cadangan versi sebelumnya, disengaja ikut tersimpan sebagai jejak perubahan.
- `Dockerfile` berisi pin versi dependensi — samakan bila menambah pustaka baru.

## Lisensi

Belum ditetapkan. Kontak pemilik repo untuk penggunaan.
