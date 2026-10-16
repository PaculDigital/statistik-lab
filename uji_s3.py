#!/usr/bin/env python3
"""UJI S3 — BERGANDA-BERANTAI (ACC Bos 18Sep26).

DEFINISI BOS (verbatim): "S3 berganda-berantai gambar nya seperti regresi
linear berganda dan ditambah garis turun dari X1 ... Xn terhadap Y"

Jadi:
  · bagian BERGanda : X1..Xn masing-masing panah ke Y  (seperti A2)
  · bagian RANTAI   : X1 → X2 → X3 → ... (garis antar X)
  · "garis turun dari X1...Xn terhadap Y" = panah berganda itu sendiri
    (dari atas ke bawah menuju Y yang ada di tengah/kanan)

Wulan gambar 2 contoh: 3 X dan 5 X (supaya terlihat rantai apa adanya).
"""
import sys
from pathlib import Path

DIR = Path('/opt/data/services/statistik-lab')
sys.path.insert(0, str(DIR))

from resep_model import baca_resep, gambar_resep  # noqa: E402

# ── S3 3 X ──
# ACC Bos 18Sep26:
#   · H1..H3 = tiap X -> Y (berganda, panah biasa)
#   · H4     = X3 (X TERAKHIR) juga terhubung ke Y  → jawaban Bos "1 = B"
#   · garisnya H4 SAMA dengan garis rantai → jawaban Bos "2 = A"
#     (garis tebal putus-putus, TANPA mata panah)
#   · rantai antar X: X1-X2, X2-X3 (tanpa label/tulisan)
S3_3X = """
judul: S3 Berganda-Berantai (3 variabel X)
variabel:
  X1 = Kualitas Produk
  X2 = Harga
  X3 = Promosi
  Y  = Keputusan Pembelian
panah:
  X1 -> Y  H1
  X2 -> Y  H2
  X3 -> Y  H3
  X3 - Y  H4
  X1 - X2
  X2 - X3
"""

# ── S3 5 X ──
S3_5X = """
judul: S3 Berganda-Berantai (5 variabel X)
variabel:
  X1 = Kualitas
  X2 = Harga
  X3 = Promosi
  X4 = Lokasi
  X5 = Pelayanan
  Y  = Keputusan Pembelian
panah:
  X1 -> Y  H1
  X2 -> Y  H2
  X3 -> Y  H3
  X4 -> Y  H4
  X5 -> Y  H5
  X5 - Y  H6
  X1 - X2
  X2 - X3
  X3 - X4
  X4 - X5
"""


def utama() -> int:
    keluar = DIR / '_uji_bos'
    keluar.mkdir(exist_ok=True)
    for nama, teks in (('s3_3x', S3_3X), ('s3_5x', S3_5X)):
        m, info = baca_resep(teks)
        svg = gambar_resep(m, info)
        (keluar / f'{nama}.svg').write_text(svg, encoding='utf-8')
        print(f'{nama:12} var={len(m.variabel):2} panah={len(m.panah):2} '
              f'-> {nama}.svg')
    return 0


if __name__ == '__main__':
    raise SystemExit(utama())
