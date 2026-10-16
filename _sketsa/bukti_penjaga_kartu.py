"""BUKTI penjaga kartu regresi BERGIGI 4 arah (setelah diperbaiki 21Sep26).

Suntik kerusakan ke SALINAN berkas -> sot.py --periksa HARUS protes.
Kalau semua suntikan LOLOS, penjaganya buta.
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

DIR = Path('/opt/data/services/statistik-lab')
PY = DIR / '.venv' / 'bin' / 'python'
PINTU = DIR / 'app' / 'templates' / 'buat_data.html'
MESIN = DIR / 'app' / 'berkas_kerja.py'

# (nama, berkas, [(cari, ganti), ...]) — beberapa potongan per suntikan
RUSAK = [
    ('kartu berantai DIHIDUPKAN lagi (class sembunyi dibuang)', PINTU,
     [('<label class="pilih-cara sembunyi" data-cara="berantai"',
       '<label class="pilih-cara" data-cara="berantai"')]),
    ('kartu berantai DIHAPUS (melanggar R1 = arsip, bukan hapus)', PINTU,
     [('<label class="pilih-cara sembunyi" data-cara="berantai" id="cara-berantai-kartu">',
       '<label class="pilih-cara" data-cara="lain" id="cara-berantai-kartu">')]),
    # suntikan ini membongkar KETIGA tanda wajib sekaligus — meniru orang yang
    # benar-benar mencabut fitur berantai dari mesin (bukan sekadar ganti 1 baris)
    ('mesin berantai DIBONGKAR (3 tanda wajib hilang sekaligus)', MESIN,
     [("cara == 'berantai'", "cara == 'tidak-ada'"),
      ("ranta = [0.55]", "ranta = []"),
      ("'rantai': rantai,", "'rantai_mati': rantai,")]),
    ('istilah PARSIAL dibuang dari JUDUL kartu ①', PINTU,
     [('<span class="cara-judul">Parsial (Sederhana)</span>',
       '<span class="cara-judul">Regresi Biasa</span>')]),
    ('istilah SIMULTAN dibuang dari JUDUL kartu ②', PINTU,
     [('<span class="cara-judul">Berganda (Parsial + Simultan)</span>',
       '<span class="cara-judul">Berganda</span>')]),
]


def main() -> int:
    hasil = []
    for nama, berkas_target, suntikan in RUSAK:
        asli = berkas_target.read_text()
        # pastikan SEMUA pola ada sebelum disuntik; kalau tidak, uji ini cacat
        kurang = [c for c, _ in suntikan if c not in asli]
        if kurang:
            print(f'  ⚠️  pola TIDAK KETEMU: {nama} -> {kurang}')
            hasil.append(False)
            continue
        with tempfile.TemporaryDirectory() as tmp:
            sal = Path(tmp) / 'statistik-lab'
            shutil.copytree(DIR, sal, symlinks=True,
                            ignore=shutil.ignore_patterns('.venv', 'data',
                                                          '__pycache__',
                                                          '*.pkl'))
            (sal / '.venv').symlink_to(DIR / '.venv')
            rel = berkas_target.relative_to(DIR)
            isi_baru = asli
            for cari, ganti in suntikan:
                isi_baru = isi_baru.replace(cari, ganti)
            (sal / rel).write_text(isi_baru)
            r = subprocess.run([str(PY), 'sot.py', '--periksa'],
                               capture_output=True, text=True, timeout=300,
                               cwd=str(sal))
            tertangkap = r.returncode != 0
            tanda = '✅ TERTANGKAP' if tertangkap else '❌ LOLOS (penjaga BUTA!)'
            print(f'  {tanda}  {nama}  (exit={r.returncode})')
            hasil.append(tertangkap)

    print()
    if all(hasil):
        print(f'  ✅ SEMUA {len(RUSAK)} KERUSAKAN TERTANGKAP — penjaga BERGIGI')
        return 0
    print(f'  ❌ {hasil.count(False)} kerusakan LOLOS — penjaga BUTA')
    return 1


if __name__ == '__main__':
    sys.exit(main())
