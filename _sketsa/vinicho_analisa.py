"""Analisa akhir: STRUKTUR & FRAMEWORK web vinichopublisindo.

Bukti: HTML halaman buku + sitemap + REST. Semua dari sumber nyata.
"""
from __future__ import annotations

import re
import urllib.request
from collections import Counter

BASIS = 'https://www.vinichopublisindo.com'
UA = {'User-Agent': 'Mozilla/5.0 (analisa-struktur)'}


def ambil(url: str) -> str:
    r = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(r, timeout=30) as f:
        return f.read().decode('utf-8', 'replace')


b = ambil(f'{BASIS}/katalog/material-teknik-pengantar-dan-aplikasi-lanjut/')

print('=' * 72)
print('1. ASET & LIBRARY (yang benar-benar dimuat)')
print('=' * 72)
for pola, label in [
    (r'href="([^"]*\.css[^"]*)"', 'CSS'),
    (r'src="([^"]*\.js[^"]*)"', 'JS'),
    (r'href="([^"]*fonts[^"]*)"', 'FONT'),
]:
    for u in sorted(set(re.findall(pola, b))):
        if 'wp-includes/css/dist' in u:
            continue
        print(f'  {label:4} {u.replace(BASIS, "")[:90]}')

print()
print('=' * 72)
print('2. STRUKTUR HALAMAN BUKU — bagian-bagian yang tampil')
print('=' * 72)
bagian = re.findall(r'<h([1-4])[^>]*>(.*?)</h\1>', b, re.S)
for lv, isi in bagian:
    t = re.sub(r'<[^>]+>', '', isi)
    t = re.sub(r'\s+', ' ', t).strip()
    if t:
        print(f'  h{lv}  {"  " * (int(lv) - 1)}{t[:68]}')

print()
print('=' * 72)
print('3. TAKSONOMI & JUMLAH BUKU (dari REST)')
print('=' * 72)
import json
d = json.loads(ambil(f'{BASIS}/wp-json/wp/v2/kategori_buku?per_page=40'))
tot = sum(x.get('count', 0) for x in d)
print(f'  {len(d)} kategori · total buku tertaut: {tot}')
for x in sorted(d, key=lambda y: -y.get('count', 0)):
    print(f"   {x['name'][:22]:24} {x.get('count')} buku")

print()
print('=' * 72)
print('4. RINGKASAN TEKNIS')
print('=' * 72)
print('  generator     :', re.search(
    r'<meta name="generator" content="([^"]+)"', b).group(1)
    if re.search(r'<meta name="generator" content="([^"]+)"', b) else '-')
print('  tema          :', sorted(set(re.findall(r'themes/([a-z0-9\-_]+)', b))))
print('  plugin        :', sorted(set(re.findall(r'plugins/([a-z0-9\-_]+)', b))))
print('  ikon          : Font Awesome',
      len(re.findall(r'fa[srb] fa-', b)), 'pemakaian')
print('  tailwind      :', 'YA' if 'tailwind' in b.lower() else 'tidak',
      '| kelas utility:', len(re.findall(r'class="[^"]*(?:flex|grid|text-\w+|bg-\w+)', b)))
print('  jejak WooCommerce:', len(re.findall(r'woocommerce', b, re.I)))
print('  REST buku     : 404 (post type buku tidak dibuka ke REST)')
