#!/usr/bin/env python3
"""GERBANG SINTAKS JS — satu kurung hilang mematikan SELURUH halaman.

⚠️ MENGAPA GERBANG INI ADA (20Sep26, akar TERUKUR — bukan dugaan):
   Terukur di /belajar: sebuah `}` yang hilang di akhir entri KAMUS membuat
   `SyntaxError: Unexpected identifier 'normalitas'`. Akibatnya BUKAN cuma
   fitur baru yang mati — SELURUH 50.177 karakter skrip MATI, termasuk kamus
   yang tadinya jalan berbulan-bulan. Halaman tetap HTTP 200, konsol hanya
   mencatat 404 favicon, dan TIDAK ADA gerbang lama yang menangkapnya:

     · gerbang_jinja.py        → hanya compile Jinja (template lolos)
     · gerbang_tag_skrip.py    → hanya tag penutup HTML
     · gerbang_galat_js.py     → hanya SyntaxError pada berkas .js BERDIRI
                                 SENDIRI; skrip INLINE di template tidak
                                 diperiksa sama sekali
     · gerbang_kode_tumpah.py  → hanya teks yang terlihat user

   Pelajaran lama yang terulang: "HTTP 200 + konsol bersih ≠ kode jalan".

⚠️ CARA YANG BENAR: skrip inline di template mengandung sintaks Jinja
   (`{{ versi_aset }}`, `{% if %}`). Menjalankan `node --check` pada teks
   MENTAH akan gagal PALSU (terbukti: buat_data.html baris 4). Jadi:
     1. RENDER template dulu lewat Jinja  → itulah yang benar-benar dikirim
        ke browser (sekaligus membuktikan templatenya bisa di-render).
     2. Baru periksa tiap <script> inline dengan `node --check`.

KELUAR 0 = semua skrip inline (SETELAH render) sintaksnya sah.
Pakai: .venv/bin/python gerbang_sintaks_js.py
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(DIR))


def main() -> int:
    node = shutil.which('node')

    print('═' * 74)
    print(' GERBANG: sintaks <script> inline (SETELAH render Jinja)')
    print('═' * 74)

    # ⚠️ Gerbang WAJIB bisa gagal. Node tidak ada → JANGAN diam-diam hijau.
    if not node:
        print('\n  ❌ node tidak ditemukan — gerbang TIDAK BISA memeriksa.')
        print('     Ini kekurangan yang harus diketahui, bukan izin lulus.')
        return 2

    try:
        from app.main import templates, _konteks       # noqa: PLC0415
    except Exception as e:                              # noqa: BLE001
        print(f'\n  ❌ tidak bisa impor app.main: {e}')
        return 2

    # daftar halaman: nama template → konteks yang dipakai main.py
    HALAMAN = [
        ('beranda.html', 'beranda', 'Beranda'),
        ('belajar.html', 'belajar', 'BELAJAR'),
        ('mulai.html', 'mulai', 'Mulai'),
        ('kuantitatif.html', 'kuantitatif', 'Kuantitatif'),
        ('syarat.html', 'syarat', 'Periksa Syarat'),
        ('buat_data.html', 'buat-data', 'Buat Data'),
        ('diagnosis.html', 'klinik', 'Diagnosis Data'),
        ('segera.html', 'segera', 'Segera'),
        ('pengaturan.html', 'pengaturan', 'Pengaturan'),
    ]

    tmp = Path(tempfile.mkdtemp(prefix='cekjs_'))
    lulus = 0
    gagal = 0
    dilewat = 0

    class PermintaanPalsu:
        """Request tiruan — _konteks hanya memakainya untuk meneruskan."""
        pass

    for nama, aktif, judul in HALAMAN:
        tpl = DIR / 'app' / 'templates' / nama
        if not tpl.exists():
            dilewat += 1
            continue
        try:
            konteks = _konteks(PermintaanPalsu(), aktif, judul)
            konteks['batas_beta_rantai'] = 1.2
            konteks['versi_aset'] = '0'
            html = templates.get_template(nama).render(**konteks)
        except Exception as e:                          # noqa: BLE001
            gagal += 1
            print(f'  ❌ {nama}: template GAGAL dirender — {str(e)[:160]}')
            continue

        blok = re.findall(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>',
                          html, re.S)
        if not blok:
            continue
        for i, isi in enumerate(blok):
            if not isi.strip():
                continue
            f = tmp / f'{Path(nama).stem}_{i}.js'
            f.write_text(isi, encoding='utf-8')
            p = subprocess.run([node, '--check', str(f)],
                               capture_output=True, text=True)
            if p.returncode == 0:
                lulus += 1
                print(f'  ✅ {nama} skrip#{i} ({len(isi)} byte)')
            else:
                gagal += 1
                m = re.search(r'\.js:(\d+)', p.stderr)
                no = int(m.group(1)) if m else 0
                pesan = [x for x in p.stderr.splitlines() if 'Error' in x]
                print(f'  ❌ {nama} skrip#{i} ({len(isi)} byte) — '
                      f'baris {no}: {pesan[0] if pesan else "?"}')
                if no:
                    b = isi.split('\n')
                    for j in range(max(0, no - 4), min(len(b), no + 2)):
                        tanda = '>>>' if j == no - 1 else '   '
                        print(f'        {tanda} {j+1:4}: {b[j][:100]}')

    print()
    print('═' * 74)
    print(f'  {lulus} LULUS / {gagal} GAGAL  ({dilewat} template dilewat)')
    print('═' * 74)
    if gagal == 0:
        print('  Semua skrip inline SAH setelah render.')
        print('  (Menjaga pola terukur 20Sep26: 1 kurung hilang = seluruh')
        print('   halaman mati, HTTP 200, tanpa galat apa pun.)')
    return 0 if gagal == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
