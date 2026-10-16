#!/usr/bin/env python3
"""UKUR: apakah garis/busur panah MENEMBUS elips?

Dukung <line> DAN <path Q...> (busur).

  · <line x1 y1 x2 y2>          → 201 titik di garis lurus
  · <path d="M x,y Q cx,cy x,y"> → 201 titik pada kurva kuadratik Bezier
"""
import re
import sys
from pathlib import Path

DIR = Path('/opt/data/services/statistik-lab')
sys.path.insert(0, str(DIR))
from gerbang_semua_model import R3, R2, R9, C1, C2, C3, C4, C5, C6  # noqa
from resep_model import baca_resep, gambar_resep                    # noqa


def nilai_elips(px, py, cx, cy, rx, ry):
    return ((px - cx) / rx) ** 2 + ((py - cy) / ry) ** 2


def titik_garis(x1, y1, x2, y2, n=201):
    for j in range(n):
        t = j / (n - 1)
        yield x1 + (x2 - x1) * t, y1 + (y2 - y1) * t


def titik_bezier(x1, y1, cx, cy, x2, y2, n=201):
    for j in range(n):
        t = j / (n - 1)
        u = 1 - t
        px = u * u * x1 + 2 * u * t * cx + t * t * x2
        py = u * u * y1 + 2 * u * t * cy + t * t * y2
        yield px, py


def ambil_ruas(svg: str):
    """Kembalikan daftar generator titik per ruas."""
    ruas = []
    for m in re.finditer(r'<line x1="([\d.-]+)" y1="([\d.-]+)" '
                         r'x2="([\d.-]+)" y2="([\d.-]+)"[^>]*marker-end', svg):
        v = [float(m.group(i)) for i in range(1, 5)]
        ruas.append(('line', v, titik_garis(*v)))
    for m in re.finditer(r'<path d="M([\d.-]+),([\d.-]+) Q([\d.-]+),([\d.-]+) '
                         r'([\d.-]+),([\d.-]+)"[^>]*marker-end', svg):
        v = [float(m.group(i)) for i in range(1, 7)]
        ruas.append(('path', v, titik_bezier(*v)))
    return ruas


def periksa(nama: str, teks: str, ambang=1.12) -> int:
    """Periksa HANYA di luar elips asal/tujuan.

    ⚠️ JEBAKAN (terukur 18Sep26): ujung panah MEMANG menyentuh tepi elips
    tujuan (nilai ≈ 1,000) — itu BENAR, bukan cacat. Yang cacat adalah
    bagian TENGAH ruas masuk ke dalam elips LAIN. Maka: elips asal &
    elips tujuan DIKECUALIKAN.
    """
    m, info = baca_resep(teks)
    svg = gambar_resep(m, info)
    elips = [tuple(float(x.group(i)) for i in range(1, 5))
             for x in re.finditer(r'<ellipse cx="([\d.-]+)" cy="([\d.-]+)" '
                                  r'rx="([\d.]+)" ry="([\d.]+)"', svg)]
    ruas = ambil_ruas(svg)
    lurus = sum(1 for j in ruas if j[0] == 'line')
    busur = sum(1 for j in ruas if j[0] == 'path')
    print(f'— {nama}: {len(ruas)} ruas ({lurus} lurus, {busur} busur)')

    gagal = 0
    for i, (jenis, v, titik) in enumerate(ruas, 1):
        # tentukan elips asal & tujuan dari titik ujung
        if jenis == 'line':
            ax, ay, bx, by = v
        else:
            ax, ay, _, _, bx, by = v
        asal_tujuan = []
        for (cx, cy, rx, ry) in elips:
            # titik ujung menempel elips ini? (nilai ≈ 0,9..1,15)
            na = nilai_elips(ax, ay, cx, cy, rx, ry)
            nb = nilai_elips(bx, by, cx, cy, rx, ry)
            if 0.85 < na < 1.35 or 0.85 < nb < 1.35:
                asal_tujuan.append((cx, cy, rx, ry))

        terburuk = None
        for px, py in titik:
            for e in elips:
                if e in asal_tujuan:
                    continue        # elips asal/tujuan DIKECUALIKAN
                cx, cy, rx, ry = e
                n = nilai_elips(px, py, cx, cy, rx, ry)
                if terburuk is None or n < terburuk[0]:
                    terburuk = (n, px, py, cx, cy)

        if terburuk is None:
            continue
        n, px, py, cx, cy = terburuk
        if n < 1.0:
            print(f'   ❌ ruas#{i} ({jenis}) MENEMBUS elips lain '
                  f'(nilai={n:.3f} di {px:.0f},{py:.0f})')
            gagal += 1
        elif n < ambang:
            print(f'   ⚠️ ruas#{i} ({jenis}) MENEMPEL elips lain '
                  f'(nilai={n:.3f})')
            gagal += 1
    if gagal == 0:
        print('   ✅ semua ruas tidak menembus elips lain')
    return gagal


def main() -> int:
    print('=' * 66)
    print('UKUR: PANAH vs ELIPS — menembus/menempel? (ambang nilai ≥ 1,12)')
    print('=' * 66)
    total = 0
    total += periksa('Contoh 3 Bos (Variasi Produk)', R3)
    total += periksa('Contoh 2 Bos (Likuiditas)', R2)
    total += periksa('Contoh 1 Bos (9 konstruk)', R9)
    total += periksa('C1', C1)
    total += periksa('C2', C2)
    total += periksa('C3', C3)
    total += periksa('C4', C4)
    total += periksa('C5', C5)
    total += periksa('C6', C6)
    print('=' * 66)
    print(f'HASIL: {"SEMUA PANAH BERSIH" if total == 0 else str(total) + " RUAS BERMASALAH"}')
    return 0 if total == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
