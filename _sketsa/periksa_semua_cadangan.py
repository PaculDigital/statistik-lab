#!/usr/bin/python3
"""PERIKSA SEMUA CADANGAN dengan Node --check (alat yang SUDAH TERBUKTI benar).

Node melaporkan SyntaxError + baris PERSIS. Kita pakai itu untuk semua berkas,
supaya tidak mungkin salah hitung sendiri.

Pakai: .venv/bin/python _sketsa/periksa_semua_cadangan.py
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

DIR = Path(__file__).resolve().parent.parent
TMP = Path('/opt/data/tmp_sintaks')
TMP.mkdir(parents=True, exist_ok=True)

BERKAS = [
    'app/templates/belajar.html.cadangan_normalitas',
    'app/templates/belajar.html.cadangan_kamus',
    'app/templates/belajar.html.cadangan_pintasan',
    'app/templates/belajar.html',
]

for nama in BERKAS:
    p = DIR / nama
    if not p.exists():
        print(f'  (tidak ada) {nama}')
        continue
    teks = p.read_text(encoding='utf-8')
    # ambil SEMUA blok <script> ... </script> (tanpa atribut src)
    blok = re.findall(r'<script>(.*?)</script>', teks, re.S)
    print(f'\n══ {Path(nama).name} — {len(blok)} blok <script> inline')
    for i, isi in enumerate(blok):
        f = TMP / f'cek_{Path(nama).name}_{i}.js'
        f.write_text(isi, encoding='utf-8')
        r = subprocess.run(['node', '--check', str(f)],
                           capture_output=True, text=True)
        if r.returncode == 0:
            print(f'   blok {i} ({len(isi):>6} byte): ✅ sintaks OK')
        else:
            pesan = [l for l in r.stderr.splitlines() if 'Error' in l]
            m = re.search(r'\.js:(\d+)', r.stderr)
            print(f'   blok {i} ({len(isi):>6} byte): ❌ {pesan[0] if pesan else "?"}'
                  f'  [baris {m.group(1) if m else "?"}]')
