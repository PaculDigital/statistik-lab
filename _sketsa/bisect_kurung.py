#!/usr/bin/env python3
"""CARI BARIS TEMPAT kurung hilang — dengan BISECT.

Cadangan (cadangan_pintasan) SEIMBANG. Berkas sekarang KURANG 1.
Kita hitung kedalaman kumulatif di TIAP BARIS untuk kedua berkas, lalu
temukan baris PERTAMA tempat keduanya berbeda.

Pakai: .venv/bin/python _sketsa/bisect_kurung.py
"""
from __future__ import annotations

import re
from pathlib import Path


def kedalaman_per_baris(path: str) -> list[int]:
    teks = Path(path).read_text(encoding='utf-8')
    return kedalaman_teks(teks)


def kedalaman_teks(teks: str) -> list[int]:
    out = []
    d = 0
    dalam = None
    k, n = 0, len(teks)
    while k < n:
        c = teks[k]
        nx = teks[k + 1] if k + 1 < n else ''
        if c == '\n':
            out.append(d)
            if dalam == '//':
                dalam = None
            k += 1
            continue
        if dalam in ("'", '"', '`'):
            if c == '\\':
                k += 2
                continue
            if c == dalam:
                dalam = None
            k += 1
            continue
        if dalam == '/*':
            if c == '*' and nx == '/':
                dalam = None
                k += 2
                continue
            k += 1
            continue
        if dalam == '//':
            k += 1
            continue
        if c == '/' and nx == '/':
            dalam = '//'
            k += 2
            continue
        if c == '/' and nx == '*':
            dalam = '/*'
            k += 2
            continue
        if c in ("'", '"', '`'):
            dalam = c
            k += 1
            continue
        if c == '{':
            d += 1
        elif c == '}':
            d -= 1
        k += 1
    return out


CDG = 'app/templates/belajar.html.cadangan_pintasan'
SKR = 'app/templates/belajar.html'

k1 = kedalaman_per_baris(CDG)
k2 = kedalaman_per_baris(SKR)
print(f'baris cadangan={len(k1)}  sekarang={len(k2)}')

# bandingkan sampai baris min
beda = None
for i in range(min(len(k1), len(k2))):
    if k1[i] != k2[i]:
        beda = i
        break

print(f'\nbaris pertama BERBEDA (indeks 0): {beda}')
if beda is not None:
    b1 = Path(CDG).read_text(encoding='utf-8').split('\n')
    b2 = Path(SKR).read_text(encoding='utf-8').split('\n')
    lo = max(0, beda - 12)
    hi = min(min(len(b1), len(b2)), beda + 8)
    print(f'\n── CADANGAN baris {lo+1}…{hi} ──')
    for j in range(lo, hi):
        tanda = '>>>' if j == beda else '   '
        print(f'  {tanda} {j+1:5} [d={k1[j]:>3}] {b1[j][:112]}')
    print(f'\n── SEKARANG baris {lo+1}…{hi} ──')
    for j in range(lo, hi):
        tanda = '>>>' if j == beda else '   '
        print(f'  {tanda} {j+1:5} [d={k2[j]:>3}] {b2[j][:112]}')
else:
    print('kedalaman sama sampai baris terakhir yang bisa dibandingkan')

print(f'\nkedalaman akhir cadangan : {k1[-1] if k1 else "?"}')
print(f'kedalaman akhir sekarang : {k2[-1] if k2 else "?"}')
