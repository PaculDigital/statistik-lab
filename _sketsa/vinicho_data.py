"""Bedah STRUKTUR DATA WordPress vinicho (wp-json) + struktur halaman.

Tujuan: pahami bagaimana buku & harga disimpan, dan halaman apa saja yang ada.
"""
from __future__ import annotations

import json
import re
import urllib.request
from pathlib import Path

BASIS = 'https://www.vinichopublisindo.com'
UA = {'User-Agent': 'Mozilla/5.0 (analisa-struktur)'}


def ambil(url: str):
    r = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(r, timeout=30) as f:
        return f.read().decode('utf-8', 'replace')


print('=' * 72)
print('1. JENIS KONTEN (custom post type) — /wp-json/wp/v2/types')
print('=' * 72)
try:
    tipe = json.loads(ambil(f'{BASIS}/wp-json/wp/v2/types'))
    for nama, d in tipe.items():
        print(f"  {nama:22} rest={d.get('rest_base')!s:22} "
              f"{(d.get('name') or '')[:40]}")
except Exception as e:
    print('  gagal:', e)

print()
print('=' * 72)
print('2. ISI HALAMAN (/wp-json/wp/v2/pages)')
print('=' * 72)
try:
    hal = json.loads(ambil(f'{BASIS}/wp-json/wp/v2/pages?per_page=30&_fields=id,slug,title,link'))
    for h in hal:
        print(f"  [{h['id']:5}] {h['slug'][:34]:36} {(h['title'].get('rendered') or '')[:40]}")
except Exception as e:
    print('  gagal:', e)

print()
print('=' * 72)
print('3. KATALOG BUKU — post type buku')
print('=' * 72)
for ct in ('buku', 'katalog', 'produk', 'book', 'product'):
    try:
        d = json.loads(ambil(f'{BASIS}/wp-json/wp/v2/{ct}?per_page=3'))
        if isinstance(d, list) and d:
            print(f'  post type "{ct}" → {len(d)} item (contoh):')
            for x in d:
                print(f"     #{x['id']} {x['slug'][:50]}")
            break
    except Exception:
        continue
else:
    print('  (tidak ada post type buku/produk terdeteksi)')
