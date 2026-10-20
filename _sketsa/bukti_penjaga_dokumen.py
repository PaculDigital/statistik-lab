"""Bukti penjaga SOT baru (20Okt26) BISA GAGAL — bukan gerbang buta.

Menyalin proyek ke folder sementara, menyuntik 4 kerusakan nyata, lalu
menjalankan sot.py --periksa di SALINAN. Tiap suntikan WAJIB membuat EXIT != 0.

Pelajaran yang dipakai (skill statistik-lab, K-02 & jebakan uji):
  • jalankan dengan .venv dari SALINAN + cwd=SALINAN, jangan jalur absolut
    ke berkas asli — kalau tidak, suntikan tak pernah terpakai.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ASLI = Path(__file__).resolve().parent.parent   # akar proyek (berkas ini di _sketsa/)

# Berkas minimal yang dibutuhkan sot.py untuk memeriksa dokumen
BERKAS = [
    'sot.py', 'gerbang_uji.py', 'STATUS.md', 'MASTER_PLAN.md',
    'FLAG_LANJUT_DISINI.md', 'README.md',
    'CATATAN_KESALAHAN_21SEP2026.md', 'RUANG_MANOVA.md',
    'KEPUTUSAN_PARSIAL_SIMULTAN_21SEP2026.md',
    'TEMUAN_MEDIASI_MODERASI_21SEP2026.md',
    'CATATAN_DISKUSI_VALIDITAS_12_UJI.md',
    'CATATAN_DISKUSI_GERBANG_MODEL_Y_GANDA.md',
    'CACAT_MEDIASI_X_BANYAK_21SEP2026.md',
    'AUDIT_UJI_LUAR_GERBANG_21SEP2026.md',
    'KOMBINASI_YANG_DIDUKUNG_21SEP2026.md',
    'RANCANGAN_SEMUA_MODEL_DI_WEB.md', 'KANVAS_MODEL_RANCANGAN.md',
]
FOLDER = ['app', 'arsip']


def siapkan(tmp: Path) -> None:
    for f in BERKAS:
        s = ASLI / f
        if s.exists():
            shutil.copy2(s, tmp / f)
    for d in FOLDER:
        s = ASLI / d
        if s.exists():
            shutil.copytree(s, tmp / d, dirs_exist_ok=True)


def jalankan(tmp: Path) -> tuple[int, str]:
    r = subprocess.run(
        [str(ASLI / '.venv' / 'bin' / 'python'), 'sot.py', '--periksa'],
        cwd=str(tmp), capture_output=True, text=True, timeout=300)
    return r.returncode, r.stdout + r.stderr


def main() -> int:
    lulus = gagal = 0

    def cek(nama: str, tertangkap: bool, keluaran: str) -> None:
        nonlocal lulus, gagal
        if tertangkap:
            lulus += 1
            print(f'LULUS  : {nama} — tertangkap')
        else:
            gagal += 1
            print(f'GAGAL  : {nama} — LOLOS, padahal harus ditangkap')
            print(f'         keluaran: {keluaran.strip()[-300:]}')

    # ── 0. DASAR: salinan bersih harus SELARAS (EXIT 0) ────────────────
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        siapkan(tmp)
        rc, out = jalankan(tmp)
        if rc == 0:
            lulus += 1
            print('LULUS  : salinan bersih → SOT SELARAS (EXIT 0)')
        else:
            gagal += 1
            print(f'GAGAL  : salinan bersih malah TIDAK selaras (rc={rc})')
            print(out[-500:])

    # ── 1. STATUS.md hilang ────────────────────────────────────────────
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        siapkan(tmp)
        (tmp / 'STATUS.md').unlink()
        rc, out = jalankan(tmp)
        cek('STATUS.md dihapus', rc != 0 and 'STATUS.md HILANG' in out, out)

    # ── 2. angka grup salah di STATUS.md ───────────────────────────────
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        siapkan(tmp)
        p = tmp / 'STATUS.md'
        p.write_text(p.read_text().replace('**60**', '**99 grup**', 1))
        rc, out = jalankan(tmp)
        cek('STATUS.md menyebut 99 grup', rc != 0 and '99' in out, out)

    # ── 3. dokumen aktif tidak terdaftar di peta ───────────────────────
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        siapkan(tmp)
        (tmp / 'DOKUMEN_NYASAR.md').write_text('# dokumen tanpa izin\n')
        rc, out = jalankan(tmp)
        cek('dokumen aktif tak terdaftar', rc != 0 and 'belum didaftarkan' in out, out)

    # ── 4. penanda beku arsip dihapus ──────────────────────────────────
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        siapkan(tmp)
        p = tmp / 'arsip' / 'README.md'
        p.write_text('# arsip\n\ntanpa penanda apa pun\n')
        rc, out = jalankan(tmp)
        cek('penanda BEKU arsip hilang', rc != 0 and 'BEKU' in out.upper(), out)

    print(f'\nHASIL: {lulus} LULUS / {gagal} GAGAL')
    return 0 if gagal == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
