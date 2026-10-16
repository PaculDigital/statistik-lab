#!/usr/bin/env python3
"""Gerbang uji SEMUA model — label tidak bertumpuk & tidak di dalam elips.

Model yang diuji:
  r3 · contoh 3 Bos (Variasi Produk/Brand Image → Kepuasan → Loyalitas)
  r2 · contoh 2 Bos (Likuiditas/Profitabilitas → Kualitas Auditor → OAGC)
  r9 · contoh 1 Bos (9 konstruk, 12 H + 1 NH)
  r6 · enam bentuk C1-C6 (sederhana, mediasi, moderasi, dual, berjenjang,
       moderated mediation)

Keluar 0 = semua aman.
"""
from __future__ import annotations

import itertools
import re
import sys
from pathlib import Path

DIR = Path('/opt/data/services/statistik-lab')
sys.path.insert(0, str(DIR))
from resep_model import baca_resep, gambar_resep      # noqa: E402

AMBANG = 24.0

R3 = """
judul: Contoh 3 — Variasi Produk
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
judul: Contoh 2 — Likuiditas
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
judul: Contoh 1 — Goal-Directed Decision Quality
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

# ── 6 bentuk standar ──
C1 = """
judul: C1 — Dua hal berhubungan
variabel:
  X1 = Kepemimpinan
  Y  = Kinerja
panah:
  X1 -> Y  H1
"""
C2 = """
judul: C2 — Lewat satu perantara
variabel:
  X1 = Kepemimpinan
  M  = Motivasi
  Y  = Kinerja
panah:
  X1 -> M  H1
  M  -> Y  H2
  X1 -> Y  H3
"""
C3 = """
judul: C3 — Ada yang menguatkan
variabel:
  X1 = Kepemimpinan
  Z  = Budaya Kerja
  Y  = Kinerja
panah:
  X1 -> Y  H1
  Z  -> Y  H2
"""
C4 = """
judul: C4 — Dua perantara sejajar
variabel:
  X1 = Kepemimpinan
  M1 = Motivasi
  M2 = Kepuasan Kerja
  Y  = Kinerja
panah:
  X1 -> M1  H1
  X1 -> M2  H2
  M1 -> Y   H3
  M2 -> Y   H4
"""
C5 = """
judul: C5 — Perantara berurutan
variabel:
  X1 = Kepemimpinan
  M1 = Motivasi
  M2 = Kepuasan Kerja
  Y  = Kinerja
panah:
  X1 -> M1  H1
  M1 -> M2  H2
  M2 -> Y   H3
  X1 -> Y   H4
"""
C6 = """
judul: C6 — Perantara yang dikuatkan
variabel:
  X1 = Kepemimpinan
  M  = Motivasi
  Z  = Budaya Kerja
  Y  = Kinerja
panah:
  X1 -> M  H1
  M  -> Y  H2
  X1 -> Y  H3
  Z  -> Y  H4
  Z  -> M  NH
"""

# ── efek tidak langsung (garis putus-putus) — ACC Bos 18Sep26 ──
TL3 = """
judul: Contoh 3 + efek tidak langsung
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


def pos_label(svg: str) -> dict[str, tuple[float, float]]:
    """Ambil posisi SEMUA label panah.

    ⚠️ JEBAKAN (terukur 18Sep26): regex `>H\\d+<` TIDAK menangkap label
    panjang seperti "H6 (tidak langsung)" → gerbang BUTA terhadapnya →
    label bertumpuk lolos. Sekarang ambil SEMUA teks berawalan H/NH/TL.
    """
    pos = {}
    for m in re.finditer(r'<text x="([\d.-]+)" y="([\d.-]+)"[^>]*>'
                         r'([^<]+)</text>', svg):
        teks = m.group(3).strip()
        if re.match(r'^(H\d|NH|TL)', teks):
            pos.setdefault(teks, (float(m.group(1)), float(m.group(2))))
    return pos


def lebar_label(teks: str) -> float:
    """Lebar kotak putih label (px) — perkiraan dari panjang teks."""
    return len(teks) * 6.5 + 10


def daftar_elips(svg: str):
    return [tuple(float(m.group(i)) for i in range(1, 5))
            for m in re.finditer(r'<ellipse cx="([\d.-]+)" cy="([\d.-]+)" '
                                 r'rx="([\d.]+)" ry="([\d.]+)"', svg)]


def periksa(nama: str, teks: str, harap: int) -> int:
    m, info = baca_resep(teks)
    svg = gambar_resep(m, info)
    pos = pos_label(svg)
    elips = daftar_elips(svg)
    gagal = 0
    print(f'— {nama}: var={len(m.variabel)} panah={len(m.panah)} '
          f'label={len(pos)}/{harap}')

    if len(pos) != harap:
        print(f'   ❌ label tidak cocok (dapat {len(pos)}, harap {harap})')
        gagal += 1

    # 🚨 Cek TUMPANG TINDIH KOTAK label (bukan cuma jarak titik).
    #    Terukur 18Sep26: "H1" (345,76) vs "H6 (tidak langsung)" (303,73)
    #    jarak titik 42 px → lolos cek jarak, TAPI kotak H6 selebar 142 px
    #    MENUTUPI H1. Jadi harus diukur sebagai PERSEGI PANJANG.
    tumpuk = []
    for a, b in itertools.combinations(sorted(pos), 2):
        ax, ay = pos[a]
        bx, by = pos[b]
        # kotak label: lebar dari panjang teks, tinggi 14 (sama dengan SVG)
        aw, bw = lebar_label(a), lebar_label(b)
        if (abs(ax - bx) < (aw + bw) / 2 + 4
                and abs(ay - by) < 14 + 4):
            tumpuk.append((a, b, abs(ax - bx), abs(ay - by)))
    if tumpuk:
        print(f'   ❌ {len(tumpuk)} pasang KOTAK label bertumpuk:')
        for a, b, dx, dy in tumpuk:
            print(f'      "{a}" vs "{b}"  dx={dx:.1f} dy={dy:.1f}')
        gagal += 1
    else:
        print('   ✅ tidak ada kotak label bertumpuk')

    dekat = [(a, b) for a, b in itertools.combinations(sorted(pos), 2)
             if ((pos[a][0] - pos[b][0]) ** 2
                 + (pos[a][1] - pos[b][1]) ** 2) ** 0.5 < AMBANG]
    if dekat:
        print(f'   ❌ {len(dekat)} pasang label bertumpuk: {dekat}')
        gagal += 1

    didalam = [l for l, (x, y) in pos.items()
               for (cx, cy, rx, ry) in elips
               if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0]
    if didalam:
        print(f'   ❌ label DI DALAM elips (akan tertutup): {didalam}')
        gagal += 1

    if gagal == 0:
        print('   ✅ semua label aman & terlihat')
    return gagal


def main() -> int:
    print('=' * 64)
    print('GERBANG UJI — SEMUA MODEL (label terlihat, tidak tertutup)')
    print('=' * 64)
    total = 0
    total += periksa('Contoh 3 Bos  (Variasi Produk)', R3, 5)
    total += periksa('Contoh 2 Bos  (Likuiditas)', R2, 5)
    total += periksa('Contoh 1 Bos  (9 konstruk)', R9, 13)
    total += periksa('C1 sederhana', C1, 1)
    total += periksa('C2 mediasi', C2, 3)
    total += periksa('C3 moderasi', C3, 2)
    total += periksa('C4 dual paralel', C4, 4)
    total += periksa('C5 berjenjang', C5, 4)
    total += periksa('C6 moderated mediation', C6, 5)
    total += periksa('TL — efek tidak langsung', TL3, 7)
    print('=' * 64)
    print(f'HASIL: {"LULUS SEMUA" if total == 0 else str(total) + " GAGAL"}')
    return 0 if total == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
