"""Cari tahu REST base post type `buku` (sitemap menyebut posts-buku, REST 404).

Juga: apa ISI halaman buku (blok Gutenberg? HTML kustom?) & dari mana
data buku diambil (shortcode? template?). Ambil HTML halaman buku utuh.
"""
from __future__ import annotations

import json
import re
import urllib.request

BASIS = 'https://www.vinichopublisindo.com'
UA = {'User-Agent': 'Mozilla/5.0 (analisa-struktur)'}


def ambil(url: str) -> str:
    r = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(r, timeout=30) as f:
        return f.read().decode('utf-8', 'replace')


print('=' * 72)
print('1. COBA BEBERAPA REST BASE untuk buku')
print('=' * 72)
for base in ('buku', 'buku-1', 'books', 'katalog-buku', 'wp/v2/buku',
             'wp/v2/bukus', 'wp/v2/books'):
    try:
        s = ambil(f'{BASIS}/wp-json/{base}')
        print(f'  ✅ /wp-json/{base} → {len(s)} char')
    except Exception as e:
        print(f'  ❌ /wp-json/{base} → {e}')

print()
print('=' * 72)
print('2. SITEMAP BUKU → daftar URL + tanggal (struktur URL)')
print('=' * 72)
try:
    sm = ambil(f'{BASIS}/wp-sitemap-posts-buku-1.xml')
    url_tgl = re.findall(r'<loc>(.*?)</loc>.*?<lastmod>(.*?)</lastmod>',
                         sm, re.S)[:6]
    for u, t in url_tgl:
        print(f'  {t[:10]}  {u.replace(BASIS, "")[:70]}')
    print(f'  total URL buku di sitemap: {len(re.findall(r"<loc>", sm))}')
except Exception as e:
    print('  gagal:', e)

print()
print('=' * 72)
print('3. ISI HALAMAN BUKU — blok apa yang dipakai?')
print('=' * 72)
try:
    b = ambil(f'{BASIS}/katalog/material-teknik-pengantar-dan-aplikasi-lanjut/')
    blok = re.findall(r'wp:([a-z0-9\-/]+)', b)
    from collections import Counter
    print('  blok Gutenberg:', dict(Counter(blok).most_common(12)))
    print()
    print('  shortcode dipakai:',
          sorted(set(re.findall(r'\[([a-z0-9_\-]+)[\s\]]', b)))[:12])
    print()
    print('  kelas CSS khas tema (Vinicho):')
    for k in sorted(set(re.findall(r'class="([^"]{4,60})"', b)))[:14]:
        print('    -', k[:70])
except Exception as e:
    print('  gagal:', e)
