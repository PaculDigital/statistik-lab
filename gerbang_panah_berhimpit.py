#!/usr/bin/env python3
"""Gerbang: cek dua panah tidak BERHIMPITAN (garis menumpuk).

Cacat terukur 18Sep26: H6 (efek tidak langsung) digambar dengan busur
PERSIS SAMA dengan H1 — `M209.6,97.5 Q350.6,50.8 470.4,138.5` untuk
keduanya → dua garis bertumpuk → mata tidak bisa membedakan mana
garis langsung dan mana garis tidak langsung (temuan vision).
"""
import math
import re
import sys
from pathlib import Path

DIR = Path('/opt/data/services/statistik-lab')
sys.path.insert(0, str(DIR))
from resep_model import baca_resep, gambar_resep      # noqa: E402
from gerbang_semua_model import R3, R2, R9, C1, C2, C3, C4, C5, C6, TL3


def ruas(svg: str):
    """Ambil daftar (jenis, titik-titik) tiap panah."""
    hasil = []
    for m in re.finditer(r'<line x1="([\d.-]+)" y1="([\d.-]+)" '
                         r'x2="([\d.-]+)" y2="([\d.-]+)"[^>]*', svg):
        x1, y1, x2, y2 = (float(m.group(i)) for i in range(1, 5))
        hasil.append(('line', [(x1 + (x2 - x1) * j / 20,
                                y1 + (y2 - y1) * j / 20)
                               for j in range(21)]))
    for m in re.finditer(r'<path d="M([\d.-]+),([\d.-]+) Q([\d.-]+),([\d.-]+) '
                         r'([\d.-]+),([\d.-]+)"[^>]*', svg):
        x1, y1, cx, cy, x2, y2 = (float(m.group(i)) for i in range(1, 7))
        titik = []
        for j in range(21):
            t = j / 20
            u = 1 - t
            titik.append((u * u * x1 + 2 * u * t * cx + t * t * x2,
                          u * u * y1 + 2 * u * t * cy + t * t * y2))
        hasil.append(('path', titik))
    return hasil


def periksa(nama: str, teks: str, ambang=8.0) -> int:
    """Periksa bagian TENGAH panah saja.

    ⚠️ JEBAKAN (terukur 18Sep26): panah yang BERANGKAT dari elips yang
    sama SELALU menempel di titik berangkatnya (jarak 0,0 px) — itu
    NORMAL, bukan cacat. Yang cacat adalah dua panah berhimpitan
    SEPANJANG jalur. Maka 20% titik ujung dibuang.
    """
    m, info = baca_resep(teks)
    svg = gambar_resep(m, info)
    semua = ruas(svg)

    def tengah(titik):
        # ⚠️ Buang 25% ujung tiap ruas. Terukur 18Sep26: panah di kolom
        #    BERBEDA (M4→M6 vs M6→Y2) bisa berdekatan 2,3 px di ujungnya —
        #    itu NORMAL (kolomnya beda, tidak berhimpit). Yang cacat hanya
        #    kalau berhimpitan SEPANJANG jalur.
        n = len(titik)
        potong = max(1, int(n * 0.25))
        return titik[potong:n - potong] or titik

    semua = [(j, tengah(t)) for j, t in semua]
    print(f'— {nama}: {len(semua)} panah')

    gagal = 0
    for i in range(len(semua)):
        for j in range(i + 1, len(semua)):
            jenis_a, ra = semua[i]
            jenis_b, rb = semua[j]
            dmin = min(math.dist(a, b) for a in ra for b in rb)
            if dmin < ambang:
                print(f'   ❌ panah#{i+1} ({jenis_a}) & panah#{j+1} '
                      f'({jenis_b}) BERHIMPITAN (jarak min {dmin:.1f}px)')
                gagal += 1
    if gagal == 0:
        print('   ✅ tidak ada panah berhimpitan')
    return gagal


def main() -> int:
    print('=' * 66)
    print('GERBANG: PANAH TIDAK BERHIMPITAN  (jarak min ≥ 8 px)')
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
    total += periksa('TL efek tidak langsung', TL3)
    print('=' * 66)
    print(f'HASIL: {"SEMUA PANAH TERPISAH" if total == 0 else str(total) + " BERHIMPITAN"}')
    return 0 if total == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
