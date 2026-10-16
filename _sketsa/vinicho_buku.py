"""Bedah post type `buku` + taksonomi `kategori_buku` vinicho.

Jawab: bagaimana BUKU dan HARGA disusun? (field apa saja yang ada?)
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
print('1. TAKSONOMI KATEGORI_BUKU')
print('=' * 72)
try:
    d = json.loads(ambil(f'{BASIS}/wp-json/wp/v2/kategori_buku?per_page=40'))
    print(f'  {len(d)} kategori')
    for x in d:
        print(f"   #{x['id']:3} {x['name'][:26]:28} slug={x['slug'][:22]:24} "
              f"jumlah={x.get('count')}")
except Exception as e:
    print('  gagal:', e)

print()
print('=' * 72)
print('2. POST TYPE BUKU — daftar & field')
print('=' * 72)
try:
    d = json.loads(ambil(f'{BASIS}/wp-json/wp/v2/buku?per_page=100'))
    print(f'  TOTAL BUKU TERDAFTAR: {len(d)}')
    print()
    bidang = sorted(d[0].keys())
    print('  BIDANG YANG TERSEDIA (kunci REST):')
    for b in bidang:
        print('   -', b)
    print()
    print('  CONTOH 2 BUKU (judul, tanggal, kategori):')
    for x in d[:2]:
        print()
        print('   ──', (x['title'].get('rendered') or '')[:70])
        print('      id     :', x['id'], '| slug:', x['slug'][:50])
        print('      tanggal:', x.get('date'))
        print('      modified:', x.get('modified'))
        print('      link   :', x.get('link'))
        kat = x.get('kategori_buku') or x.get('class_list') or []
        print('      kategori:', kat)
        # cari jejak harga/field khas di isi
        isi = (x.get('content') or {}).get('rendered', '')
        for pola, label in [(r'Rp\s?[\d.]+', 'harga'),
                            (r'isbn[^<]{0,30}', 'isbn'),
                            (r'15,5|15\.5|UNESCO', 'ukuran'),
                            (r'\d+\s*(?:Hlm|hlm|halaman)', 'halaman')]:
            m = re.findall(pola, isi, re.I)
            if m:
                print(f'      {label:8}:', sorted(set(m))[:3])
except Exception as e:
    print('  gagal:', e)

print()
print('=' * 72)
print('3. CONTOH ISI MENTAH 1 BUKU (dipotong 1200 char)')
print('=' * 72)
try:
    d = json.loads(ambil(f'{BASIS}/wp-json/wp/v2/buku?per_page=1'))
    if d:
        isi = (d[0].get('content') or {}).get('rendered', '')
        bersih = re.sub(r'<[^>]+>', ' ', isi)
        bersih = re.sub(r'\s+', ' ', bersih).strip()
        print(bersih[:1200])
except Exception as e:
    print('  gagal:', e)
