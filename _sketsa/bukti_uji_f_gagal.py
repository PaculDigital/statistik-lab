"""BUKTI uji F TERBUKTI BISA GAGAL (aturan induk proyek).

Suntik kerusakan NYATA ke SALINAN berkas -> uji HARUS menangkap.
Kalau semua suntikan LOLOS, berarti ujinya buta.
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

DIR = Path('/opt/data/services/statistik-lab')
TERKUNCI = DIR / 'app' / 'berkas_kerja.py'
UJI = DIR / '_sketsa' / 'uji_uji_f.py'

# (nama kerusakan, cari, ganti)
RUSAK = [
    ('MS residu dibagi df SALAH (df_total, bukan df_residu)',
     "ms_res = sse / df_res if df_res else float('nan')",
     "ms_res = sse / df_tot if df_tot else float('nan')"),
    ('F dibalik (MS_residu / MS_regresi)',
     "F = ms_reg / ms_res if ms_res and ms_res > 0 else float('nan')",
     "F = ms_res / ms_reg if ms_reg and ms_reg > 0 else float('nan')"),
    ('SS regresi dihitung salah (SST + SSE)',
     "ssr = sst - sse",
     "ssr = sst + sse"),
    ('R2 pakai SSE/SST (kebalik)',
     "r2 = ssr / sst if sst > 0 else 0.0",
     "r2 = sse / sst if sst > 0 else 0.0"),
]


def main() -> int:
    asli = TERKUNCI.read_text()
    hasil = []
    for nama, cari, ganti in RUSAK:
        if cari not in asli:
            print(f'  ❌ TIDAK KETEMU pola: {nama}')
            hasil.append(False)
            continue
        with tempfile.TemporaryDirectory() as tmp:
            sal = Path(tmp) / 'statistik-lab'
            shutil.copytree(DIR, sal, symlinks=True,
                            ignore=shutil.ignore_patterns('.venv', 'data',
                                                          '__pycache__',
                                                          '*.pkl'))
            # salin venv (symlink supaya cepat)
            (sal / '.venv').symlink_to(DIR / '.venv')
            f = sal / 'app' / 'berkas_kerja.py'
            f.write_text(asli.replace(cari, ganti, 1))
            r = subprocess.run([str(DIR / '.venv' / 'bin' / 'python'),
                                str(sal / '_sketsa' / 'uji_uji_f.py')],
                               capture_output=True, text=True, timeout=300,
                               cwd=str(sal))
            tertangkap = r.returncode != 0
            tanda = '✅ TERTANGKAP' if tertangkap else '❌ LOLOS (uji BUTA!)'
            print(f'  {tanda}  {nama}  (exit={r.returncode})')
            hasil.append(tertangkap)

    print()
    if all(hasil):
        print(f'  ✅ SEMUA {len(RUSAK)} KERUSAKAN TERTANGKAP — uji F BERGIGI')
        return 0
    print(f'  ❌ {hasil.count(False)} kerusakan LOLOS — uji F BUTA')
    return 1


if __name__ == '__main__':
    sys.exit(main())
