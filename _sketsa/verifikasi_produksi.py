#!/usr/bin/env python3
"""VERIFIKASI PRODUKSI — apakah perubahan BENAR-BENAR hidup di kontainer live?

Bukan percaya log deploy. Periksa ISI halaman /belajar dari DALAM kontainer
produksi `simulasi-olah-data` (loopback container Hermes tidak bisa ke 8120).

Yang dibuktikan:
  1. Tombol `Normalitas` ADA di HTML produksi
  2. Judul uji t sudah "masalah uji t" (bukan "signifikan kok negatif")
  3. Biji pita "Materi & Kamus" = 8
  4. Tombol pintasan sehat/sakit ADA
  5. Kalimat "tidak ada corong" ADA
  6. Skrip produksi TIDAK punya SyntaxError (node --check pada HTML live)
  7. Halaman lain tidak rusak (HTTP 200 semua)

Pakai: .venv/bin/python _sketsa/verifikasi_produksi.py
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

KONT = 'simulasi-olah-data'
DIR = Path(__file__).resolve().parent.parent

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


def dalam_kontainer(py: str) -> str:
    """Jalankan python DI DALAM kontainer produksi, kembalikan stdout."""
    p = subprocess.run(
        ['docker', 'exec', KONT, 'python', '-c', py],
        capture_output=True, text=True, timeout=90)
    if p.returncode != 0:
        return f'❌GALAT: {p.stderr.strip()[:300]}'
    return p.stdout.strip()


def main() -> int:
    print('═' * 74)
    print(f' VERIFIKASI PRODUKSI — kontainer `{KONT}`')
    print('═' * 74)

    # ── 0. kontainer hidup? ──────────────────────────────────────────────
    p = subprocess.run(['docker', 'ps', '--filter', f'name=^{KONT}$',
                        '--format', '{{.Status}}'],
                       capture_output=True, text=True)
    status = p.stdout.strip()
    cek('kontainer produksi JALAN', 'Up' in status, status or 'tidak ada')

    # ── 1-5. periksa ISI halaman /belajar dari dalam kontainer ──────────
    html = dalam_kontainer(
        "import urllib.request;"
        "print(urllib.request.urlopen("
        "'http://127.0.0.1:8000/belajar',timeout=15).read().decode())")
    if html.startswith('❌GALAT'):
        cek('ambil halaman /belajar', False, html[:150])
        print('\n' + '═' * 74)
        print(f'  {lulus} LULUS / {gagal} GAGAL')
        return 1
    cek('halaman /belajar terambil dari produksi', len(html) > 10000,
        f'{len(html)} byte')

    cek('tombol `Normalitas` ADA di produksi', 'data-k="normalitas"' in html)
    cek('judul uji t = "masalah uji t"',
        'masalah uji t' in html.lower())
    cek('judul LAMA tidak ada lagi',
        'signifikan kok negatif' not in html.lower())
    cek('biji pita "Materi & Kamus" = 8',
        bool(re.search(r'Materi &amp; Kamus\s*<[^>]*>\s*8', html))
        or 'Materi &amp; Kamus (8)' in html
        or bool(re.search(r'kamus[^>]*>\s*8\s*<', html)),
        'pola biji')
    cek('tombol pintasan sehat/sakit ADA',
        'pintasan-sehat' in html and 'pintasan-sakit' in html)
    cek('kalimat "Tidak ada corong" ADA',
        'Tidak ada corong' in html)
    cek('kalimat "tidak ada kemiringan" (normalitas) ADA',
        'Tidak ada kemiringan' in html)

    # ── 6. SINTAKS skrip produksi (node) ─────────────────────────────────
    print('\n── 6. sintaks skrip produksi (dari HTML live) ──')
    blok = re.findall(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>', html,
                      re.S)
    tmp = Path('/opt/data/tmp_prod')
    tmp.mkdir(parents=True, exist_ok=True)
    for i, isi in enumerate(blok):
        if not isi.strip():
            continue
        f = tmp / f'prod_{i}.js'
        f.write_text(isi, encoding='utf-8')
        r = subprocess.run(['node', '--check', str(f)],
                           capture_output=True, text=True)
        cek(f'skrip#{i} ({len(isi)} byte) sintaks SAH', r.returncode == 0,
            'OK' if r.returncode == 0 else
            [x for x in r.stderr.splitlines() if 'Error' in x][:1])

    # ── 7. halaman lain tetap 200 ────────────────────────────────────────
    print('\n── 7. halaman lain tetap hidup ──')
    for jalur in ['/', '/belajar', '/buat-data', '/klinik', '/pengaturan',
                  '/kuantitatif', '/segera/ujian']:
        kode = dalam_kontainer(
            "import urllib.request\n"
            "try:\n"
            f"    r=urllib.request.urlopen('http://127.0.0.1:8000{jalur}',"
            "timeout=15)\n"
            "    print(r.status)\n"
            "except Exception as e:\n"
            "    print('ERR', e)")
        cek(f'{jalur} → HTTP 200', kode.strip() == '200', kode.strip()[:60])

    print()
    print('═' * 74)
    print(f'  {lulus} LULUS / {gagal} GAGAL')
    print('═' * 74)
    if gagal == 0:
        print('  Produksi TERBUKTI memuat perubahan — bukan cuma kata log.')
    return 0 if gagal == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
