#!/usr/bin/env python3
"""UJI BAHWA gerbang_sintaks_js.py BENAR-BENAR BISA GAGAL.

Aturan Bos (19Sep26): "GERBANG WAJIB DIUJI BISA GAGAL → suntik kerusakan
buatan ke SALINAN berkas, jalankan, HARUS EXIT 1. Gerbang yang tak bisa
gagal = tidak menjaga apa pun."

Cara: sisipkan kerusakan ASLI yang pernah terjadi (buang satu `},` penutup
entri KAMUS di belajar.html), jalankan gerbang, HARUS GAGAL. Lalu pulihkan
dan pastikan gerbang kembali LULUS.

Pakai: .venv/bin/python _sketsa/uji_gerbang_sintaks.py
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

DIR = Path(__file__).resolve().parent.parent
TPL = DIR / 'app' / 'templates' / 'belajar.html'
SIMpan = DIR / '_sketsa' / 'belajar_rusak.html'

lulus = 0
gagal = 0


def cek(nama: str, ok: bool, ket: str = '') -> None:
    global lulus, gagal
    if ok:
        lulus += 1
        print(f'  ✅ {nama}' + (f'  ({ket})' if ket else ''))
    else:
        gagal += 1
        print(f'  ❌ {nama}' + (f'  ({ket})' if ket else ''))


def jalankan() -> int:
    p = subprocess.run([str(DIR / '.venv' / 'bin' / 'python'),
                        str(DIR / 'gerbang_sintaks_js.py')],
                       cwd=str(DIR), capture_output=True, text=True)
    return p.returncode


def main() -> int:
    print('═' * 70)
    print(' UJI: gerbang sintaks JS BISA GAGAL?')
    print('═' * 70)

    asli = TPL.read_text(encoding='utf-8')
    shutil.copy2(TPL, SIMpan)

    try:
        # 1. keadaan bersih → HARUS LULUS
        rc = jalankan()
        cek('keadaan bersih → EXIT 0 (lulus)', rc == 0, f'exit={rc}')

        # 2. SUNTIK kerusakan ASLI: buang penutup entri hetero ('  },' sebelum
        #    '  normalitas: {') — ini kerusakan yang BENAR-BENAR terjadi 20Sep26.
        pola = '    }\n  },\n  normalitas: {'
        if pola not in asli:
            print('  ⚠️ pola suntikan tidak ketemu — periksa berkas')
            return 2
        rusak = asli.replace(pola, '    }\n  normalitas: {', 1)
        TPL.write_text(rusak, encoding='utf-8')

        rc = jalankan()
        cek('setelah 1 kurung dibuang → EXIT 1 (GAGAL)', rc == 1, f'exit={rc}')

        # 3. pulihkan → HARUS LULUS lagi
        TPL.write_text(asli, encoding='utf-8')
        rc = jalankan()
        cek('dipulihkan → EXIT 0 lagi (lulus)', rc == 0, f'exit={rc}')

        # 4. pastikan berkas asli benar-benar utuh
        cek('berkas asli utuh (isi identik)', TPL.read_text(
            encoding='utf-8') == asli)
    finally:
        TPL.write_text(asli, encoding='utf-8')
        if SIMpan.exists():
            SIMpan.unlink()

    print()
    print('═' * 70)
    print(f'  {lulus} LULUS / {gagal} GAGAL')
    print('═' * 70)
    if gagal == 0:
        print('  Gerbang TERBUKTI bisa gagal — ia benar-benar menjaga.')
    return 0 if gagal == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
