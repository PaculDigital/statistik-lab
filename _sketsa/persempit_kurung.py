#!/usr/bin/env python3
"""PERSEMPIT: di BLOK MANA kurung hilang?

Cara: ukur kedalaman di TITIK-TITIK PENANDA yang kita tahu (awal tiap fungsi),
lalu bandingkan antara cadangan_pintasan (SEIMBANG) dan berkas SEKARANG
(KURANG 1). Titik pertama yang berbeda = tempat hilangnya.

Pakai: .venv/bin/python _sketsa/persempit_kurung.py
"""
from __future__ import annotations

import re
from pathlib import Path


def kedalaman_di_penanda(path: str) -> dict:
    teks = Path(path).read_text(encoding='utf-8')
    # ambil isi <script> KEDUA (skrip kamus)
    bagian = re.findall(r'<script>(.*?)</script>', teks, re.S)
    isi = bagian[1] if len(bagian) > 1 else ''
    baris = isi.split('\n')

    hasil = {}
    d = 0
    dalam = None
    penanda = re.compile(
        r'^(function\s+\w+|const\s+\w+\s*=|let\s+\w+\s*=|el\(|pintasanPasang|ujitLot|ujitIsi|pilih\(|\(function)')
    pos_baris = 1
    k, n = 0, len(isi)
    while k < n:
        c = isi[k]
        nx = isi[k + 1] if k + 1 < n else ''
        if c == '\n':
            hasil.setdefault(('BARIS', pos_baris), d)
            pos_baris += 1
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

    # catat kedalaman di awal tiap penanda fungsi
    out = {}
    d2 = 0
    dalam = None
    k = 0
    pos_baris = 1
    while k < n:
        c = isi[k]
        nx = isi[k + 1] if k + 1 < n else ''
        if c == '\n':
            pos_baris += 1
            if dalam == '//':
                dalam = None
            # cek baris berikutnya
            if pos_baris <= len(baris):
                b = baris[pos_baris - 1].strip()
                if penanda.match(b):
                    out[(pos_baris, b[:62])] = d2
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
            d2 += 1
        elif c == '}':
            d2 -= 1
        k += 1
    return out


k1 = kedalaman_di_penanda('app/templates/belajar.html.cadangan_pintasan')
k2 = kedalaman_di_penanda('app/templates/belajar.html')

print('══ BANDINGKAN kedalaman di tiap penanda fungsi ══')
print('  (cadangan = SEIMBANG, sekarang = kurang 1)\n')
ditemukan = None
for nama in k1:
    teks_penanda = nama[1]
    a = k1[nama]
    # cocokkan berdasarkan teks penanda (urutan tetap)
    b = None
    for nama2 in k2:
        if nama2[1] == teks_penanda:
            b = k2[nama2]
            break
    if b is None:
        print(f'  ❓ HILANG di sekarang: {teks_penanda}')
        continue
    tanda = '  ' if a == b else '⚠️'
    if a != b and ditemukan is None:
        ditemukan = teks_penanda
    print(f'  {tanda} d={a} vs {b}  {teks_penanda}')

print()
if ditemukan:
    print(f'>>> KEDALAMAN PERTAMA BERBEDA di penanda: {ditemukan}')
    print('    Kurung hilang SEBELUM baris ini.')
else:
    print('>>> tidak ada perbedaan di penanda → kurung hilang SETELAH penanda terakhir')
