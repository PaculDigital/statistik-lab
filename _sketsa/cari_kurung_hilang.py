#!/usr/bin/env python3
"""CARI PERSIS baris tempat kurung { } hilang di entri hetero.

Terukur: const KAMUS punya 136 '{' tapi 135 '}' → kurang SATU.
Entri hetero GAGAL parse; entri lain OK. Jadi penutupnya ada di hetero.

Skrip ini menyusuri teks KARAKTER PER KARAKTER (mengabaikan isi string,
template literal, komentar) lalu melaporkan di kedalaman berapa KAMUS
berakhir — dan baris mana yang dicurigai.

Pakai: .venv/bin/python _sketsa/cari_kurung_hilang.py
"""
from __future__ import annotations

import re
from pathlib import Path

BERKAS = Path('/opt/data/tmp_sintaks/skrip_1.js')
isi = BERKAS.read_text(encoding='utf-8')
baris = isi.split('\n')

# ── mulai dari 'const KAMUS = {' ──────────────────────────────────────────
mulai = None
for i, b in enumerate(baris):
    if b.startswith('const KAMUS = {'):
        mulai = i
        break
print(f'const KAMUS mulai baris {mulai+1}')

# ── susuri dengan MESIN KEADAAN (abaikan string/komentar) ─────────────────
dalam = None          # None | "'" | '"' | '`' | '//' | '/*'
depth = 0
lapor = []
i = mulai
pos = 0
teks = '\n'.join(baris[mulai:])
line_no = mulai + 1
depth_saat_baris = {}

k = 0
n = len(teks)
while k < n:
    c = teks[k]
    nxt = teks[k + 1] if k + 1 < n else ''

    if c == '\n':
        line_no += 1
        if dalam == '//':
            dalam = None
        depth_saat_baris[line_no] = depth
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
        k += 1
        continue
    if c == '}':
        depth -= 1
        if depth == 0:
            lapor.append(('KEDALAMAN 0 di baris', line_no))
        k += 1
        continue
    k += 1

print(f'\nkedalaman akhir: {depth}')
print(f'penanda kedalaman 0: {lapor}')

# cari di baris mana kedalaman kembali 0 untuk PERTAMA kali setelah entri dimulai
# (yaitu setelah 'hetero: {')
het = None
for i, b in enumerate(baris):
    if re.match(r'\s{2}hetero: \{', b):
        het = i
        break
print(f'\nentri hetero mulai baris {het+1}')

# susuri mulai dari hetero
k = 0
teks2 = '\n'.join(baris[het:])
d = 0
ln = het + 1
m = len(teks2)
kedalaman = {}
while k < m:
    c = teks2[k]
    nxt = teks2[k + 1] if k + 1 < m else ''
    if c == '\n':
        ln += 1
        kedalaman[ln] = d
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
        d += 1
    elif c == '}':
        d -= 1
        if d == 0:
            print(f'  >>> KEDALAMAN 0 di baris {ln}  '
                  f'(= {baris[ln-1].strip()[:110]})')
            break
    k += 1

print('\n── 15 baris sebelum titik kedalaman-0 ──')
print(f'  (kalau kedalaman-0 muncul TERLALU AWAL, di situ kurung hilang)')

# tampilkan kedalaman tiap baris di zona akhir entri hetero
zona = [ln2 for ln2 in range(max(het + 1, ln - 14), ln + 2)]
for z in zona:
    d2 = kedalaman.get(z, '?')
    print(f'  {z:5} [d={d2}] {baris[z-1][:120]}')
