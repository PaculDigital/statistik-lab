#!/usr/bin/env python3
"""GERBANG: SVG WAJIB bisa diparse XML.

🚨 CACAT NYATA terukur 18Sep26: Wulan menulis
  f'{f" marker-end=url(#{ujung})" if ujung else ""}'
→ menghasilkan `marker-end=url(#ah)` TANPA tanda kutip →
  Chrome menolak: 'AttValue: " or \' expected' → SELURUH gambar kosong.

Gerbang ini memastikan: setiap SVG yang dihasilkan BISA diparse XML,
TIDAK ada atribut tanpa tanda kutip, dan tidak ada 'None'/'{' tersisa.
"""
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

DIR = Path('/opt/data/services/statistik-lab')
sys.path.insert(0, str(DIR))


def periksa(nama: str, svg: str) -> int:
    gagal = 0
    # 1. wajib bisa diparse XML
    try:
        ET.fromstring(svg)
    except ET.ParseError as e:
        print(f'— {nama}\n   ❌ XML RUSAK: {e}')
        gagal += 1
    # 2. tidak ada atribut tanpa tanda kutip (pola: =url( atau =# )
    for pola, ket in ((r'=\s*url\(', 'marker tanpa kutip'),
                      (r'="None"', 'nilai None bocor'),
                      (r'\{|\}', 'kurung kurawal bocor')):
        tem = re.findall(pola, svg)
        if tem:
            print(f'— {nama}\n   ❌ {ket}: {len(tem)}x')
            gagal += 1
    if not gagal:
        print(f'— {nama}\n   ✅ SVG VALID (bisa diparse, atribut berkutip)')
    return gagal


def utama() -> int:
    from resep_model import baca_resep, gambar_resep
    total = 0
    daftar = []
    try:
        from gerbang_semua_model import (C1, C2, C3, C4, C5, C6, R9, TL3)
        daftar += [('C1', C1), ('C2', C2), ('C3', C3), ('C4', C4),
                   ('C5', C5), ('C6', C6), ('R9', R9), ('TL3', TL3)]
    except Exception as e:                     # noqa: BLE001
        print(f'(lewati gerbang_semua_model: {e})')
    try:
        from uji_s3 import S3_3X, S3_5X
        daftar += [('S3-3X', S3_3X), ('S3-5X', S3_5X)]
    except Exception as e:                     # noqa: BLE001
        print(f'(lewati uji_s3: {e})')
    try:
        from uji_pertanyaan_bos import (R_8X, R_3X, R_PAR, R_BER, R_DUAL,
                                        R_MOD)
        daftar += [('8X', R_8X), ('3X', R_3X), ('PAR', R_PAR), ('BER', R_BER),
                   ('DUAL', R_DUAL), ('MOD', R_MOD)]
    except Exception as e:                     # noqa: BLE001
        print(f'(lewati uji_pertanyaan_bos: {e})')

    for nama, teks in daftar:
        m, info = baca_resep(teks)
        total += periksa(nama, gambar_resep(m, info))
    print(f'\nHASIL: {len(daftar)} SVG diperiksa, {total} cacat')
    return 1 if total else 0


if __name__ == '__main__':
    raise SystemExit(utama())
