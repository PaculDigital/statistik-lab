#!/usr/bin/env python3
"""UJI 6 KASUS yang ditanyakan Bos — gambar nyata, bukan klaim.

1. Regresi berganda 8 X → Y          (X1..X8)
2. Regresi berganda 3 X → Y          (pembanding)
3. Mediasi PARALEL  (X → M1 → Y, X → M2 → Y)
4. Mediasi BERJENJANG (X → M1 → M2 → Y)
5. Dual mediasi paralel + 2 X
6. Moderasi (Z memotong jalur)
"""
import sys
from pathlib import Path

DIR = Path('/opt/data/services/statistik-lab')
sys.path.insert(0, str(DIR))
from resep_model import baca_resep, gambar_resep      # noqa: E402

# ── 1. REGRESI BERGANDA 8 X → Y ──
R_8X = """
judul: Regresi Linear Berganda (8 Variabel X)
variabel:
  X1 = Kualitas Produk
  X2 = Harga
  X3 = Promosi
  X4 = Lokasi
  X5 = Kualitas Layanan
  X6 = Citra Merek
  X7 = Kepuasan
  X8 = Kepercayaan
  Y  = Loyalitas Pelanggan
panah:
  X1 -> Y  H1
  X2 -> Y  H2
  X3 -> Y  H3
  X4 -> Y  H4
  X5 -> Y  H5
  X6 -> Y  H6
  X7 -> Y  H7
  X8 -> Y  H8
"""

# ── 2. REGRESI BERGANDA 3 X → Y ──
R_3X = """
judul: Regresi Linear Berganda (3 Variabel X)
variabel:
  X1 = Likuiditas
  X2 = Profitabilitas
  X3 = Leverage
  Y  = Nilai Perusahaan
panah:
  X1 -> Y  H1
  X2 -> Y  H2
  X3 -> Y  H3
"""

# ── 3. MEDIASI PARALEL (2 perantara sejajar) ──
R_PAR = """
judul: Mediasi Paralel (Dua Perantara Sejajar)
variabel:
  X1 = Kepemimpinan
  M1 = Motivasi
  M2 = Kepuasan Kerja
  Y  = Kinerja Pegawai
panah:
  X1 -> M1  H1
  X1 -> M2  H2
  M1 -> Y   H3
  M2 -> Y   H4
"""

# ── 4. MEDIASI BERJENJANG (perantara berurutan) ──
R_BER = """
judul: Mediasi Berjenjang (Perantara Berurutan)
variabel:
  X1 = Kepemimpinan
  M1 = Motivasi
  M2 = Kepuasan Kerja
  Y  = Kinerja Pegawai
panah:
  X1 -> M1  H1
  M1 -> M2  H2
  M2 -> Y   H3
  X1 -> Y   H4
"""

# ── 5. DUAL MEDIASI PARALEL DENGAN 2 X ──
R_DUAL = """
judul: Dual Mediasi Paralel (Dua X, Dua Perantara)
variabel:
  X1 = Gaya Kepemimpinan
  X2 = Budaya Organisasi
  M1 = Motivasi
  M2 = Komitmen
  Y  = Kinerja Pegawai
panah:
  X1 -> M1  H1
  X1 -> M2  H2
  X2 -> M1  H3
  X2 -> M2  H4
  M1 -> Y   H5
  M2 -> Y   H6
"""

# ── 6. MODERASI ──
R_MOD = """
judul: Moderasi (Variabel Penguat)
variabel:
  X1 = Kepemimpinan
  Z  = Budaya Kerja
  Y  = Kinerja Pegawai
panah:
  X1 -> Y  H1
  Z  -> Y  H2
"""

KASUS = [
    ('regresi_8x', R_8X),
    ('regresi_3x', R_3X),
    ('mediasi_parallel', R_PAR),
    ('mediasi_berjenjang', R_BER),
    ('dual_mediasi', R_DUAL),
    ('moderasi', R_MOD),
]

out = Path('/opt/data/services/statistik-lab/_uji_bos')
out.mkdir(exist_ok=True)

for nama, teks in KASUS:
    m, info = baca_resep(teks)
    svg = gambar_resep(m, info)
    p = out / f'{nama}.svg'
    p.write_text(svg, encoding='utf-8')
    print(f'{nama:22} var={len(m.variabel):2} panah={len(m.panah):2} -> {p.name}')
