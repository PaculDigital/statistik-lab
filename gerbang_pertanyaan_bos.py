#!/usr/bin/env python3
"""Gerbang uji 6 KASUS BOS — label & panah tidak cacat."""
import itertools
import math
import re
import sys
from pathlib import Path

DIR = Path('/opt/data/services/statistik-lab')
sys.path.insert(0, str(DIR))
from resep_model import baca_resep, gambar_resep      # noqa: E402
import uji_pertanyaan_bos as U                        # noqa: E402


def label_svg(svg):
    pos = {}
    for m in re.finditer(r'<text x="([\d.-]+)" y="([\d.-]+)"[^>]*>'
                         r'([^<]+)</text>', svg):
        t = m.group(3).strip()
        if re.match(r'^(H\d|NH|TL)', t):
            pos.setdefault(t, (float(m.group(1)), float(m.group(2))))
    return pos


def lebar(t):
    return len(t) * 6.5 + 10


def elips_svg(svg):
    return [tuple(float(m.group(i)) for i in range(1, 5))
            for m in re.finditer(r'<ellipse cx="([\d.-]+)" cy="([\d.-]+)" '
                                 r'rx="([\d.]+)" ry="([\d.]+)"', svg)]


def ruas_svg(svg):
    hasil = []
    for m in re.finditer(r'<line x1="([\d.-]+)" y1="([\d.-]+)" '
                         r'x2="([\d.-]+)" y2="([\d.-]+)"[^>]*marker-end', svg):
        v = [float(m.group(i)) for i in range(1, 5)]
        hasil.append(('line', [(v[0] + (v[2] - v[0]) * j / 40,
                                v[1] + (v[3] - v[1]) * j / 40)
                               for j in range(41)], v))
    for m in re.finditer(r'<path d="M([\d.-]+),([\d.-]+) Q([\d.-]+),([\d.-]+) '
                         r'([\d.-]+),([\d.-]+)"[^>]*marker-end', svg):
        v = [float(m.group(i)) for i in range(1, 7)]
        titik = []
        for j in range(41):
            t = j / 40
            u = 1 - t
            titik.append((u * u * v[0] + 2 * u * t * v[2] + t * t * v[4],
                          u * u * v[1] + 2 * u * t * v[3] + t * t * v[5]))
        hasil.append(('path', titik, v))
    return hasil


total = 0
print('=' * 70)
print('GERBANG: 6 KASUS PERTANYAAN BOS')
print('=' * 70)
for nama, teks in U.KASUS:
    m, info = baca_resep(teks)
    svg = gambar_resep(m, info)
    pos = label_svg(svg)
    elips = elips_svg(svg)
    ruas = ruas_svg(svg)
    harap = len(m.panah)
    gagal = 0
    print(f'— {nama}  label={len(pos)}/{harap}  ruas={len(ruas)}')

    if len(pos) != harap:
        print(f'   ❌ label tidak cocok')
        gagal += 1

    # kotak label bertumpuk
    for a, b in itertools.combinations(sorted(pos), 2):
        ax, ay = pos[a]
        bx, by = pos[b]
        if (abs(ax - bx) < (lebar(a) + lebar(b)) / 2 + 4
                and abs(ay - by) < 18):
            print(f'   ❌ kotak label bertumpuk: "{a}" vs "{b}"')
            gagal += 1

    # label di dalam elips
    for l, (x, y) in pos.items():
        for (cx, cy, rx, ry) in elips:
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0:
                print(f'   ❌ label {l} DI DALAM elips')
                gagal += 1
                break

    # panah berhimpit (buang 25% ujung)
    def tengah(t):
        n = len(t)
        p = max(1, int(n * 0.25))
        return t[p:n - p] or t
    for i in range(len(ruas)):
        for j in range(i + 1, len(ruas)):
            ta, tb = tengah(ruas[i][1]), tengah(ruas[j][1])
            d = min(math.dist(p_, q_) for p_ in ta for q_ in tb)
            if d < 8.0:
                print(f'   ❌ panah#{i+1} & panah#{j+1} berhimpit ({d:.1f}px)')
                gagal += 1

    if gagal == 0:
        print('   ✅ BERSIH')
    total += gagal

print('=' * 70)
print(f'HASIL: {"SEMUA BERSIH" if total == 0 else str(total) + " CACAT"}')
