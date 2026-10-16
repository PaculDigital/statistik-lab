#!/usr/bin/env python3
"""Uji 3 model pakai resep — render SVG tanpa indikator."""
import sys
from pathlib import Path

sys.path.insert(0, '/opt/data/services/statistik-lab')
from resep_model import baca_resep, gambar_resep      # noqa: E402

R3 = """
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
"""

R2 = """
judul: Model Penelitian
variabel:
  X1 = Likuiditas
  X2 = Profitabilitas
  Z  = Kualitas Auditor
  Y  = OAGC
panah:
  X1 -> Z  H1
  X2 -> Z  H2
  X1 -> Y  H3
  X2 -> Y  H4
  Z  -> Y  H5
"""

R9 = """
judul: Model Goal-Directed Decision Quality
variabel:
  X1 = Self-efficacy
  M1 = Mastery Goals
  M2 = Performance-Approach Goals
  M3 = Performance-Avoidance Goals
  M4 = Positive Affect
  M5 = Decision Confidence
  M6 = Decision Satisfaction
  Y1 = Attitudinal Loyalty Intention
  Y2 = Switching Likelihood
panah:
  X1 -> M1  H1
  X1 -> M2  H2
  X1 -> M3  NH
  M1 -> M4  H3
  M2 -> M4  H4
  M3 -> M4  H5
  M1 -> M5  H6
  M2 -> M5  H7
  M3 -> M5  H8
  M4 -> M6  H9
  M5 -> M6  H10
  M6 -> Y1  H11
  M6 -> Y2  H12
"""

for nama, teks in [('r3', R3), ('r2', R2), ('r9', R9)]:
    m, info = baca_resep(teks)
    svg = gambar_resep(m, info)
    p = Path(f'/tmp/uji_{nama}.svg')
    p.write_text(svg, encoding='utf-8')
    print(f'{nama}: variabel={len(m.variabel)} panah={len(m.panah)} '
          f'-> {p}')
