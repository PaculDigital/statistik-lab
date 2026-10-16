"""Lanjutan bedah vinicho: di mana BUKU & HARGA disimpan?

Jejak: halaman buku = /katalog/<slug>/ (bukan posts, bukan pages).
Cari: post type kustom apa yang dipakai (via sitemap / REST jarang) +
menu + struktur halaman + jejak harga.
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
print('1. SITEMAP — daftar URL yang dikenal mesin pencari')
print('=' * 72)
try:
    idx = ambil(f'{BASIS}/sitemap.xml')
    lok = re.findall(r'<loc>(.*?)</loc>', idx)
    print(f'  sitemap index: {len(lok)} berkas')
    for l in lok[:12]:
        print('   -', l)
except Exception as e:
    print('  gagal:', e)

print()
print('=' * 72)
print('2. SITEMAP HALAMAN (semua URL publik)')
print('=' * 72)
try:
    idx = ambil(f'{BASIS}/sitemap.xml')
    lok = re.findall(r'<loc>(.*?)</loc>', idx)
    semua = []
    for l in lok:
        try:
            sm = ambil(l)
            semua += re.findall(r'<loc>(.*?)</loc>', sm)
        except Exception:
            pass
    print(f'  total URL: {len(semua)}')
    for u in semua[:60]:
        print('   -', u.replace(BASIS, ''))
except Exception as e:
    print('  gagal:', e)

print()
print('=' * 72)
print('3. JEJAK HARGA & MATA UANG di halaman buku')
print('=' * 72)
try:
    b = ambil(f'{BASIS}/katalog/material-teknik-pengantar-dan-aplikasi-lanjut/')
    for pola in [r'Rp\s?[\d.]+', r'"price"\s*:\s*"?[\d.]+', r'currency',
                 r'berat', r'ISBN', r'isbn']:
        m = re.findall(pola, b, re.I)
        print(f'  {pola[:24]:26} {len(m):3}x  {sorted(set(m))[:6]}')
except Exception as e:
    print('  gagal:', e)

print()
print('=' * 72)
print('4. MENU WORDPRESS')
print('=' * 72)
try:
    m = json.loads(ambil(f'{BASIS}/wp-json/wp/v2/menu-items?per_page=40'))
    print(f'  {len(m)} item menu')
    for x in m[:20]:
        print(f"   - {(x.get('title') or {}).get('rendered','')[:34]:36} "
              f"{(x.get('url') or '')[:60]}")
except Exception as e:
    print('  gagal:', e)

print()
print('=' * 72)
print('5. PLUGIN TERDETEKSI (dari HTML halaman buku)')
print('=' * 72)
try:
    b = ambil(f'{BASIS}/katalog/material-teknik-pengantar-dan-aplikasi-lanjut/')
    for p in sorted(set(re.findall(r'wp-content/plugins/([a-z0-9\-_]+)', b, re.I))):
        print('   plugin:', p)
    for t in sorted(set(re.findall(r'wp-content/themes/([a-z0-9\-_]+)', b, re.I))):
        print('   tema  :', t)
    for j in sorted(set(re.findall(r'(wp-includes/js/[a-z0-9\-\/\.]+\.js)', b, re.I)))[:8]:
        print('   js    :', j)
    print()
    print('   jejak Tailwind:', len(re.findall(r'tailwind', b, re.I)))
    print('   jejak e-commerce:', len(re.findall(
        r'woocommerce|add-to-cart|checkout|cart', b, re.I)))
except Exception as e:
    print('  gagal:', e)
