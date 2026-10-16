#!/usr/bin/env python3
"""ESCAPE tag penutup di dalam blok JS yang WULAN tulis (20Sep26).

AKAR:
  Di dalam string JS, tag penutup HTML (mis. `</strong>`) bisa membuat parser
  HTML menganggap <script> SUDAH SELESAI → kode tumpah jadi teks di halaman,
  walau HTTP 200 tetap hijau. Aturan proyek: tulis `<\\/strong>`.

  Terukur: 13 pelanggaran, SEMUA di blok yang Wulan tambahkan. Gerbang di
  CADANGAN ASLI = 0 pelanggaran → ini cacat WULAN, bukan cacat lama.
  (Wulan sempat salah simpul karena menghitung `</strong>` di SELURUH berkas,
  padahal hanya yang DI DALAM <script> yang berbahaya.)

⚠️ CARA POTONG BLOK (akar galat IndexError sebelumnya): regex
   `<script(?![^>]*\\bsrc=)[^>]*>(.*?)</script>` gagal karena berkas ini
   punya 1 blok skrip besar yang di DALAMNYA (di komentar) menyebut
   `</script>`. Jadi potong lewat POSISI + hitung kedalaman tag skrip,
   bukan regex malas.

Pakai: .venv/bin/python _sketsa/escape_tag_wulan.py
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

DIR = Path(__file__).resolve().parent.parent
BERKAS = DIR / 'app' / 'templates' / 'belajar.html'
CADANGAN = DIR / 'app' / 'templates' / 'belajar.html.cadangan_escape'

lama = BERKAS.read_text(encoding='utf-8')

# ── potong blok <script> INLINE lewat posisi ─────────────────────────────
blok = []          # (awal_isi, akhir_isi)
pos = 0
while True:
    a = lama.find('<script', pos)
    if a == -1:
        break
    tag_end = lama.find('>', a)
    pembuka = lama[a:tag_end + 1]
    if 'src=' in pembuka:
        pos = tag_end + 1
        continue
    b = lama.find('</script>', tag_end)
    if b == -1:
        break
    blok.append((tag_end + 1, b, a, b + len('</script>')))
    pos = b + 9

print(f'blok <script> inline: {len(blok)}')
for i, (s, e, _, _) in enumerate(blok):
    print(f'  blok {i}: {e - s} byte')

if not blok:
    print('tidak ada blok inline — batal')
    sys.exit(2)

# blok TERBESAR = blok kamus
idx = max(range(len(blok)), key=lambda i: blok[i][1] - blok[i][0])
s, e, _, _ = blok[idx]
target = lama[s:e]
print(f'\nblok terbesar (indeks {idx}): {len(target)} byte')

# ── escape HANYA tag penutup (hanya PENUTUP yang berbahaya) ──────────────
TAG = ['strong', 'em', 'b', 'i', 'br', 'div', 'span', 'p', 'li', 'ul', 'ol',
       'h1', 'h2', 'h3', 'a', 'small', 'code', 'table', 'tr', 'td', 'svg',
       'text', 'line', 'circle', 'button', 'input', 'label', 'section']

baru_skrip = target
total = 0
for t in TAG:
    pola = f'</{t}>'
    n = baru_skrip.count(pola)
    if n:
        baru_skrip = baru_skrip.replace(pola, f'<\\/{t}>')
        total += n
        print(f'  </{t}>  →  <\\/{t}>   ({n}×)')

print(f'\ntotal di-escape: {total}')
if total == 0:
    print('tidak ada yang perlu diubah.')
    sys.exit(0)

# ── tulis (dengan cadangan) ──────────────────────────────────────────────
shutil.copy2(BERKAS, CADANGAN)
print(f'cadangan: {CADANGAN.name}')

baru = lama[:s] + baru_skrip + lama[e:]
BERKAS.write_text(baru, encoding='utf-8')
print(f'BERKAS DITULIS: {len(lama)} → {len(baru)} byte')

# ── verifikasi ───────────────────────────────────────────────────────────
print('\n── verifikasi ──')
# tag penutup yang MASIH polos di dalam blok
sisa = 0
for t in TAG:
    sisa += baru_skrip.count(f'</{t}>')
print(f'  tag penutup polos di dalam <script>: {sisa}  (harus 0)')
print(f'  ukuran sama? {len(baru) - len(lama)} byte bertambah '
      f'(= {total} tag × 1 backslash)')

print('\n── gerbang_tag_skrip.py ──')
p = subprocess.run([str(DIR / '.venv' / 'bin' / 'python'),
                    str(DIR / 'gerbang_tag_skrip.py')],
                   cwd=str(DIR), capture_output=True, text=True)
print(p.stdout[-1200:])
print(f'EXIT={p.returncode}')
