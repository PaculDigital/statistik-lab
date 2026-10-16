#!/usr/bin/env python3
"""DIAGNOSA: kenapa panah menyilang tidak dilengkungkan?

Cetak keadaan `geo` SEBELUM dan SESUDAH putaran kedua.
"""
import sys
from pathlib import Path

DIR = Path('/opt/data/services/statistik-lab')
sys.path.insert(0, str(DIR))

import diagram_svg as D
from gerbang_semua_model import R9
from resep_model import baca_resep

m, info = baca_resep(R9)

# jalankan hitung kolom/baris persis seperti gambar_svg
kolom, jml = D.hitung_kolom(m)
baris = D.hitung_baris(m, kolom, jml)
print('kolom:', kolom)
print('baris:', baris)
print()

# tiru perhitungan pusat
print('cek: berapa panah yang "dekat_pusat" satu sama lain?')
# kita perlu pusat: ambil dari D
import inspect
src = inspect.getsource(D.gambar_svg)
print('--- potongan kode putaran kedua ---')
for i, baris_kode in enumerate(src.split('\n'), 1):
    if 'dekat_pusat' in baris_kode or 'min(d1, d2, d3, d4)' in baris_kode:
        print(f'{i}: {baris_kode}')
