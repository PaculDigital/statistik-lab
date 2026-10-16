#!/usr/bin/env python3
"""Gerbang uji TEMPLATE RESEP — periksa GEOMETRI, bukan cuma label.

KENAPA: cacat 18Sep26 — kotak indikator M MENABRAK elips Y. Terukur:
butuh 254 px, tersedia 210 px. Mata bisa luput, tapi HITUNGAN tidak.

Pemeriksaan:
  1. resep terbaca tanpa galat
  2. jumlah label = jumlah panah berlabel
  3. tidak ada label bertumpuk (jarak ≥ 24 px)
  4. tidak ada label keluar batas gambar
  5. KOTAK INDIKATOR tidak menabrak ELIPS mana pun
  6. KOTAK INDIKATOR tidak menabrak kotak indikator lain
  7. semua isi ada di dalam batas gambar

Keluar 0 = aman.
"""
from __future__ import annotations

import itertools
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from resep_model import (baca_resep, gambar_resep, RESEP_CONTOH_3,   # noqa
                         RESEP_TANPA_INDIKATOR)

AMBANG_LABEL = 24.0


def kotak_dari_svg(svg: str):
    """Ambil (x, y, w, h) tiap <rect> yang KOTAK INDIKATOR.

    ⚠️ JEBAKAN (terukur 18Sep26): kotak putih kecil di belakang LABEL H
    (lebar ±23 px, tinggi 14) ikut terhitung sebagai kotak indikator →
    gerbang melaporkan 'kotak menabrak elips' PADAHAL itu kotak label.
    ATURAN: kotak indikator = yang TINGGINYA TINGGI_KOTAK (30), bukan 14.
    """
    from resep_model import TINGGI_KOTAK
    hasil = []
    for m in re.finditer(r'<rect x="([\d.-]+)" y="([\d.-]+)" '
                         r'width="([\d.]+)" height="([\d.]+)"', svg):
        x, y, w, h = (float(m.group(i)) for i in range(1, 5))
        if w >= 1000:                 # latar belakang
            continue
        if abs(h - TINGGI_KOTAK) > 0.5:   # kotak label putih, bukan indikator
            continue
        hasil.append((x, y, w, h))
    return hasil


def elips_dari_svg(svg: str):
    hasil = []
    for m in re.finditer(r'<ellipse cx="([\d.-]+)" cy="([\d.-]+)" '
                         r'rx="([\d.]+)" ry="([\d.]+)"', svg):
        hasil.append(tuple(float(m.group(i)) for i in range(1, 5)))
    return hasil


def label_dari_svg(svg: str):
    pos = {}
    for m in re.finditer(r'<text x="([\d.-]+)" y="([\d.-]+)"[^>]*>'
                         r'(H\d+|NH\d*)</text>', svg):
        pos.setdefault(m.group(3), (float(m.group(1)), float(m.group(2))))
    return pos


def tumpang_tindih(a, b) -> bool:
    """Kotak A=(x,y,w,h) vs kotak B — beririsan?"""
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return (ax < bx + bw and bx < ax + aw
            and ay < by + bh and by < ay + ah)


def kotak_vs_elips(kotak, elips) -> bool:
    """Kotak menabrak elips? Uji sudut kotak + titik terdekat pusat."""
    x, y, w, h = kotak
    cx, cy, rx, ry = elips
    sudut = [(x, y), (x + w, y), (x, y + h), (x + w, y + h)]
    for (px, py) in sudut:
        if ((px - cx) / rx) ** 2 + ((py - cy) / ry) ** 2 <= 1.0:
            return True
    # pusat elips di dalam kotak?
    if x <= cx <= x + w and y <= cy <= y + h:
        return True
    return False


def periksa(nama: str, teks_resep: str, harap_label: int,
            harap_kotak: int) -> int:
    gagal = 0
    print(f'— {nama}')
    try:
        m, info = baca_resep(teks_resep)
    except Exception as e:
        print(f'   ❌ GAGAL baca resep: {e}')
        return 1

    svg = gambar_resep(m, info)
    label = label_dari_svg(svg)
    kotak = kotak_dari_svg(svg)
    elips = elips_dari_svg(svg)

    print(f'   variabel={len(m.variabel)} panah={len(m.panah)} '
          f'label={len(label)} kotak={len(kotak)} elips={len(elips)}')

    if len(label) != harap_label:
        print(f'   ❌ GAGAL label: dapat {len(label)}, harap {harap_label}')
        gagal += 1
    if len(kotak) != harap_kotak:
        print(f'   ❌ GAGAL kotak indikator: dapat {len(kotak)}, '
              f'harap {harap_kotak}')
        gagal += 1

    # label bertumpuk
    dekat = [(a, b) for a, b in itertools.combinations(sorted(label), 2)
             if ((label[a][0] - label[b][0]) ** 2
                 + (label[a][1] - label[b][1]) ** 2) ** 0.5 < AMBANG_LABEL]
    if dekat:
        print(f'   ❌ GAGAL: {len(dekat)} pasang label bertumpuk: {dekat}')
        gagal += 1
    else:
        print('   ✅ tidak ada label bertumpuk')

    # kotak menabrak elips  ← GERBANG BARU penangkap cacat 18Sep26
    tabrak = [(k, e) for k in kotak for e in elips if kotak_vs_elips(k, e)]
    if tabrak:
        print(f'   ❌ GAGAL: {len(tabrak)} kotak indikator MENABRAK elips')
        for k, e in tabrak[:4]:
            print(f'      kotak x={k[0]:.0f}..{k[0]+k[2]:.0f} '
                  f'y={k[1]:.0f}..{k[1]+k[3]:.0f}  '
                  f'vs elips cx={e[0]:.0f} rx={e[2]:.0f}')
        gagal += 1
    else:
        print('   ✅ kotak indikator tidak menabrak elips')

    # kotak vs kotak
    kk = [(a, b) for a, b in itertools.combinations(range(len(kotak)), 2)
          if tumpang_tindih(kotak[a], kotak[b])]
    if kk:
        print(f'   ❌ GAGAL: {len(kk)} pasang kotak indikator bertumpuk')
        gagal += 1
    else:
        print('   ✅ kotak indikator tidak saling bertumpuk')

    # keluar batas
    m_size = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg)
    if m_size:
        L, T = float(m_size.group(1)), float(m_size.group(2))
        luar = [k for k in kotak
                if k[0] < 0 or k[1] < 0 or k[0] + k[2] > L or k[1] + k[3] > T]
        llabel = [k for k, (x, y) in label.items()
                  if x < 0 or y < 0 or x > L or y > T]
        if luar or llabel:
            print(f'   ❌ GAGAL: {len(luar)} kotak & {len(llabel)} label '
                  f'keluar batas {L:.0f}×{T:.0f}')
            gagal += 1
        else:
            print(f'   ✅ semua isi dalam batas {L:.0f}×{T:.0f}')
    return gagal


def main() -> int:
    print('=' * 64)
    print('GERBANG UJI — TEMPLATE RESEP MODEL')
    print('=' * 64)
    total = 0
    total += periksa('Contoh 3 Bos (indikator, 4 var, 5 H)',
                     RESEP_CONTOH_3, 5, 13)
    total += periksa('Tanpa indikator (4 var, 5 H)',
                     RESEP_TANPA_INDIKATOR, 5, 0)
    print('=' * 64)
    print(f'HASIL: {"LULUS" if total == 0 else str(total) + " GAGAL"}')
    return 0 if total == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
