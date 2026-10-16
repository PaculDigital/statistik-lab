#!/usr/bin/env python3
"""Uji EFEK TIDAK LANGSUNG (TL) — contoh 3 Bos + H6/H7.

ACC Bos 18Sep26: "H6 dan H7 adalah effek tidak langsung di gambar garis
panah titik titik".
"""
import re
import sys
from pathlib import Path

DIR = Path('/opt/data/services/statistik-lab')
sys.path.insert(0, str(DIR))
from resep_model import baca_resep, gambar_resep      # noqa: E402

R = """
judul: Gambar 2.1 Model Penelitian
variabel:
  X1 = Variasi Produk
  X2 = Brand Image
  M  = Kepuasan
  Y  = Loyalitas Pelanggan
panah:
  X1 -> Y  H1
  X2 -> Y  H2
  X1 -> M  H3
  X2 -> M  H4
  M  -> Y  H5
  X1 -> Y  H6 (tidak langsung)
  X2 -> Y  H7 (tidak langsung)
"""

m, info = baca_resep(R)
print(f'variabel={len(m.variabel)} panah={len(m.panah)}')
for p in m.panah:
    print(f"   {p['dari']:3} -> {p['ke']:3}  {p['label']:22} jenis={p['jenis']}")

svg = gambar_resep(m, info)
Path('/tmp/uji_tl.svg').write_text(svg, encoding='utf-8')

# ukur: apakah ada garis putus-putus TL?
tl = len(re.findall(r'stroke-dasharray="2 3"', svg))
nh = len(re.findall(r'stroke-dasharray="2 4"', svg))
print(f'\ngaris TL (putus-putus 2 3): {tl}')
print(f'garis NH (putus-putus 2 4): {nh}')

# cek kolom tidak terpengaruh TL
import diagram_svg as D
kolom, jml = D.hitung_kolom(m)
print(f'\nkolom: {kolom}')
print(f'jumlah kolom: {jml}')
print(f'-> Y harus di kolom terakhir ({jml-1}), sekarang: {kolom["Y"]}')
