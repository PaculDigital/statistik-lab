#!/usr/bin/env python3
"""Gerbang uji diagram: pastikan TIDAK ADA label yang bertumpuk.

KENAPA: cacat 18Sep26 — H4 dan H6 bertumpuk PERSIS (jarak 0,0 px) karena
keduanya ditaruh di titik tengah panah. Mata tidak bisa melihatnya,
tapi MENGUKUR bisa. Gerbang ini menghitung jarak antar label.

Keluar 0 = aman. Keluar ≠0 = ada label bertumpuk.
"""
from __future__ import annotations

import itertools
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from diagram_svg import model_contoh_bos, gambar_svg   # noqa: E402

AMBANG = 24.0   # px — di bawah ini = bertumpuk


def label_dari_svg(svg: str) -> dict[str, tuple[float, float]]:
    pos: dict[str, tuple[float, float]] = {}
    for m in re.finditer(r'<text x="([\d.-]+)" y="([\d.-]+)"[^>]*>'
                         r'(H\d+|NH\d*)</text>', svg):
        pos[m.group(3)] = (float(m.group(1)), float(m.group(2)))
    return pos


def periksa(nama: str, model, harap: int) -> int:
    svg = gambar_svg(model, nama)
    pos = label_dari_svg(svg)
    gagal = 0

    print(f'— {nama}')
    print(f'   label ditemukan: {len(pos)} (harap {harap})')
    if len(pos) != harap:
        print(f'   ❌ GAGAL: jumlah label tidak cocok')
        gagal += 1

    dekat = []
    for a, b in itertools.combinations(sorted(pos), 2):
        d = ((pos[a][0] - pos[b][0]) ** 2 + (pos[a][1] - pos[b][1]) ** 2) ** 0.5
        if d < AMBANG:
            dekat.append((a, b, d))

    if dekat:
        print(f'   ❌ GAGAL: {len(dekat)} pasang label bertumpuk')
        for a, b, d in dekat:
            print(f'      {a} vs {b}: {d:.1f}px  {pos[a]} {pos[b]}')
        gagal += 1
    else:
        print('   ✅ tidak ada label bertumpuk')

    # 🚨 GERBANG BARU (18Sep26): label TIDAK BOLEH di dalam elips apa pun.
    #    Akar cacat: H2 ditaruh di titik tengah panah X2→Y yang jatuh DI
    #    DALAM elips M → elips digambar terakhir → label TERTUTUP →
    #    "H2 HILANG". Mata bisa luput; HITUNGAN tidak.
    elips = []
    for m in re.finditer(r'<ellipse cx="([\d.-]+)" cy="([\d.-]+)" '
                         r'rx="([\d.]+)" ry="([\d.]+)"', svg):
        elips.append(tuple(float(m.group(i)) for i in range(1, 5)))
    didalam = []
    for nama_l, (x, y) in pos.items():
        for (cx, cy, rx, ry) in elips:
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0:
                didalam.append((nama_l, x, y, cx, cy))
                break
    if didalam:
        print(f'   ❌ GAGAL: {len(didalam)} label JATUH DI DALAM elips '
              f'(akan TERTUTUP → seolah hilang)')
        for l, x, y, cx, cy in didalam[:5]:
            print(f'      {l} di ({x:.0f},{y:.0f}) ada di dalam elips '
                  f'({cx:.0f},{cy:.0f})')
        gagal += 1
    else:
        print('   ✅ tidak ada label di dalam elips')

    # penjaga tambahan: label tidak boleh keluar batas gambar
    m_size = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg)
    if m_size:
        L, T = float(m_size.group(1)), float(m_size.group(2))
        keluar = [k for k, (x, y) in pos.items()
                  if x < 0 or y < 0 or x > L or y > T]
        if keluar:
            print(f'   ❌ GAGAL: label keluar batas gambar: {keluar}')
            gagal += 1
        else:
            print(f'   ✅ semua label di dalam batas ({L:.0f}×{T:.0f})')
    return gagal


def main() -> int:
    print('=' * 62)
    print('GERBANG UJI — LABEL DIAGRAM TIDAK BERTUMPUK')
    print('=' * 62)
    total = 0
    total += periksa('Model contoh (9 konstruk, 12 H + 1 NH)',
                     model_contoh_bos(), 13)
    print('=' * 62)
    print(f'HASIL: {"LULUS" if total == 0 else str(total) + " GAGAL"}')
    return 0 if total == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
