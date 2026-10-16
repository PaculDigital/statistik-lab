#!/usr/bin/env python3
"""Lacak KEDALAMAN tiap baris di dalam const KAMUS → temukan kurung yatim.

Terukur: tidak ada kedalaman-0 setelah 'const KAMUS = {' → ada '{' yatim.
Skrip ini mencetak kedalaman SETIAP baris di sekitar transisi entri, supaya
kelihatan persis baris mana yang naik tapi tidak pernah balik.

Pakai: .venv/bin/python _sketsa/lacak_kedalaman.py
"""
from __future__ import annotations

from pathlib import Path

baris = Path('/opt/data/tmp_sintaks/skrip_1.js').read_text(
    encoding='utf-8').split('\n')
mulai = next(i for i, b in enumerate(baris) if b.startswith('const KAMUS = {'))

# batasi sampai 560 (cukup untuk melihat semua entri)
akhir = min(len(baris), 570)
teks = '\n'.join(baris[mulai:akhir])

depth = 0
dalam = None
kd = {}                 # baris → kedalaman setelah baris itu
pos = mulai + 1
naik = []               # catat tiap '{'
k, n = 0, len(teks)
while k < n:
    c = teks[k]
    nxt = teks[k + 1] if k + 1 < n else ''
    if c == '\n':
        kd[pos] = depth
        pos += 1
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
        naik.append((pos, baris[pos - 1].strip()[:90]))
    elif c == '}':
        depth -= 1
        if naik:
            naik.pop()
    k += 1

print(f'kedalaman akhir (mulai baris {mulai+1}): {depth}')
print(f'kurung YATIM: {len(naik)}')
for b, t in naik:
    print(f'  >>> baris {b}: {t}')

print('\n── kedalaman tiap baris: dari baris 28 s/d 55 ──')
for b in range(mulai + 1, min(mulai + 30, 60)):
    print(f'  {b:5} [d={kd.get(b,"?"):>3}] {baris[b-1][:105]}')

print('\n── di mana entri KAMUS mulai (pola 2-spasi + nama:) ──')
import re
for b in range(mulai, min(len(baris), 570)):
    if re.match(r'\s{2}[a-zA-Z_][a-zA-Z0-9_]*: \{', baris[b]):
        print(f'  {b+1:5} [d={kd.get(b,"?"):>3}] {baris[b].strip()[:70]}')

print('\n── 20 baris terakhir sekitar baris 515-535 ──')
for b in range(512, min(len(baris), 536)):
    print(f'  {b+1:5} [d={kd.get(b,"?"):>3}] {baris[b][:110]}')
