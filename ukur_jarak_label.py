#!/usr/bin/env python3
"""UKUR jarak sebenarnya label H ke garis elips — jangan tebak."""
import re
import sys
from pathlib import Path

DIR = Path('/opt/data/services/statistik-lab')
sys.path.insert(0, str(DIR))
from gerbang_semua_model import R3, R9, C6      # noqa: E402
from resep_model import baca_resep, gambar_resep  # noqa: E402


def jarak_ke_elips(px, py, cx, cy, rx, ry):
    """Jarak titik ke KURVA elips (pendekatan: skala ke lingkaran).

    Metode: proyeksikan titik ke elips sepanjang arah dari pusat
    (bukan jarak tegak lurus sejati, tapi cukup untuk mengukur
    'menempel atau tidak' — galat < 2 px untuk rasio kita).
    """
    dx, dy = px - cx, py - cy
    if dx == 0 and dy == 0:
        return -min(rx, ry)
    # titik di elips searah (dx, dy)
    t = 1.0 / (((dx / rx) ** 2 + (dy / ry) ** 2) ** 0.5)
    ex, ey = cx + dx * t, cy + dy * t
    return ((px - ex) ** 2 + (py - ey) ** 2) ** 0.5


def periksa(nama, teks, ketat=10.0):
    m, info = baca_resep(teks)
    svg = gambar_resep(m, info)
    label = {}
    for x in re.finditer(r'<text x="([\d.-]+)" y="([\d.-]+)"[^>]*>'
                         r'(H\d+|NH\d*)</text>', svg):
        label.setdefault(x.group(3), (float(x.group(1)), float(x.group(2))))
    elips = [tuple(float(x.group(i)) for i in range(1, 5))
             for x in re.finditer(r'<ellipse cx="([\d.-]+)" cy="([\d.-]+)" '
                                  r'rx="([\d.]+)" ry="([\d.]+)"', svg)]

    print(f'— {nama}')
    gagal = 0
    for l, (px, py) in sorted(label.items()):
        # jarak min ke elips mana pun (positif = di luar, negatif = di dalam)
        jarak = []
        for (cx, cy, rx, ry) in elips:
            nilai = ((px - cx) / rx) ** 2 + ((py - cy) / ry) ** 2
            d = jarak_ke_elips(px, py, cx, cy, rx, ry)
            jarak.append(-d if nilai <= 1.0 else d)
        dmin = min(jarak, key=abs)
        tanda = 'DALAM ⛔' if dmin < 0 else 'luar'
        status = 'OK' if dmin >= ketat else ('ME PET ⚠️' if dmin >= 0
                                            else 'TERTUTUP ❌')
        print(f'   {l:4} ({px:6.1f},{py:6.1f})  jarak={dmin:7.1f}px  '
              f'{tanda}  {status}')
        if dmin < ketat:
            gagal += 1
    return gagal


def main() -> int:
    print('=' * 68)
    print('UKUR JARAK LABEL → GARIS ELIPS  (ketat: ≥ 10 px)')
    print('=' * 68)
    total = 0
    total += periksa('Contoh 3 Bos (Variasi Produk)', R3)
    total += periksa('Contoh 1 Bos (9 konstruk)', R9)
    total += periksa('C6 moderated mediation', C6)
    print('=' * 68)
    print(f'HASIL: {"SEMUA BERJARAK CUKUP" if total == 0 else str(total) + " TERLALU DEKAT"}')
    return 0 if total == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
