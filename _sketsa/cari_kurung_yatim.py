#!/usr/bin/env python3
"""Temukan kurung yang NAIK tapi tidak pernah turun — di baris mana?

Terukur: kedalaman akhir const KAMUS = 1 (harusnya 0). Kita lacak TIAP
perubahan kedalaman dan cari kurung '{' yang 'yatim' (tidak berpasangan).

Pakai: .venv/bin/python _sketsa/cari_kurung_yatim.py
"""
from __future__ import annotations

from pathlib import Path

BERKAS = Path('/opt/data/tmp_sintaks/skrip_1.js')
baris = BERKAS.read_text(encoding='utf-8').split('\n')

# mulai dari 'const KAMUS = {' sampai '};'
mulai = next(i for i, b in enumerate(baris) if b.startswith('const KAMUS = {'))
# ⚠️ JANGAN cari dengan teks '};' — itu ketemu penutup FUNGSI lain lebih dulu
# (terukur: baris 106, padahal penutup KAMUS di 521). Cari lewat KEDALAMAN.
teks = '\n'.join(baris[mulai:])
pos_baris = 1
depth = 0
tutup = None
dalam = None
k, n = 0, len(teks)
while k < n:
    c = teks[k]
    nxt = teks[k + 1] if k + 1 < n else ''
    if c == '\n':
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
        if c == '*' and nxt == '/':
            dalam = None
            k += 2
            continue
        k += 1
        continue
    if dalam == '//':
        k += 1
        continue
    if c == '/' and nxt == '/':
        dalam = '//'
        k += 2
        continue
    if c == '/' and nxt == '*':
        dalam = '/*'
        k += 2
        continue
    if c in ("'", '"', '`'):
        dalam = c
        k += 1
        continue
    if c == '{':
        depth += 1
    elif c == '}':
        depth -= 1
        if depth == 0:
            tutup = mulai + pos_baris - 1
            break
    k += 1
print(f'KAMUS: baris {mulai+1} … {tutup+1 if tutup else "TIDAK KETEMU"}')

teks = '\n'.join(baris[mulai:tutup + 1])
pos_baris = 1
depth = 0
tumpukan = []          # simpan (baris, kolom, teks)
dalam = None
k, n = 0, len(teks)

while k < n:
    c = teks[k]
    nxt = teks[k + 1] if k + 1 < n else ''

    if c == '\n':
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
        if c == '*' and nxt == '/':
            dalam = None
            k += 2
            continue
        k += 1
        continue
    if dalam == '//':
        k += 1
        continue

    if c == '/' and nxt == '/':
        dalam = '//'
        k += 2
        continue
    if c == '/' and nxt == '*':
        dalam = '/*'
        k += 2
        continue
    if c in ("'", '"', '`'):
        dalam = c
        k += 1
        continue
    if c == '{':
        depth += 1
        tumpukan.append((pos_baris, baris[pos_baris - 1].strip()[:100]))
        k += 1
        continue
    if c == '}':
        depth -= 1
        if tumpukan:
            tumpukan.pop()
        k += 1
        continue
    k += 1

print(f'\nkedalaman akhir: {depth}')
print(f'kurung yang TIDAK PERNAH DITUTUP: {len(tumpukan)}')
for b, t in tumpukan:
    print(f'  >>> baris {b}: {t}')

print('\n── 25 baris sesudah tiap tersangka ──')
for b, t in tumpukan:
    for j in range(max(0, b - 4), min(len(baris), b + 22)):
        tanda = '>>>' if j == b - 1 else '   '
        print(f'  {tanda} {j+1:5}: {baris[j][:120]}')
    print()
