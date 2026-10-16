"""Bedah struktur halaman buku vinichopublisindo (HTML tersimpan)."""
from __future__ import annotations

import re
from pathlib import Path

html = Path('/tmp/vinicho_buku.html').read_text(errors='replace')

print('=' * 72)
print('1. FRAMEWORK / CMS — dari jejak di HTML')
print('=' * 72)
jejak = {
    'WordPress (wp-content)': r'wp-content',
    'WordPress (wp-includes)': r'wp-includes',
    'WooCommerce': r'woocommerce|wc-|add_to_cart|add-to-cart',
    'Elementor': r'elementor',
    'Theme (nama)': r'themes/([a-z0-9\-_]+)/',
    'Plugin (nama)': r'plugins/([a-z0-9\-_]+)/',
    'Yoast SEO': r'yoast',
    'Rank Math': r'rank-math',
    'Midtrans (ID payment)': r'midtrans',
    'Xendit': r'xendit',
    'Duitku': r'duitku',
    'Tripay': r'tripay',
    'QRIS': r'qris',
    'WhatsApp link': r'wa\.me|api\.whatsapp',
    'Shopee': r'shopee',
    'Tokopedia': r'tokopedia',
    'Instagram': r'instagram\.com',
    'Facebook': r'facebook\.com',
    'Next.js': r'__NEXT_DATA__|_next/static',
    'React': r'react',
    'Bootstrap': r'bootstrap',
    'Tailwind': r'tailwind',
    'Google Analytics': r'gtag|google-analytics|analytics\.js',
    'Google Tag Manager': r'googletagmanager',
}
for nama, pola in jejak.items():
    cari = re.findall(pola, html, re.I)
    if cari:
        unik = sorted(set(cari))[:4]
        print(f'  ✅ {nama:26} {len(cari):4}x   {unik}')

print()
print('=' * 72)
print('2. TEMA & VERSI (bukti konkret)')
print('=' * 72)
for m in sorted(set(re.findall(r'wp-content/themes/([a-z0-9\-_]+)', html, re.I))):
    print('  tema   :', m)
for m in sorted(set(re.findall(r'wp-content/plugins/([a-z0-9\-_]+)', html, re.I))):
    print('  plugin :', m)
for m in sorted(set(re.findall(r'wordpress[^"\']{0,20}?([\d.]+)', html, re.I)))[:6]:
    print('  versi  :', m)
gen = re.findall(r'<meta name="generator" content="([^"]+)"', html, re.I)
for g in gen:
    print('  generator:', g)

print()
print('=' * 72)
print('3. JUDUL & META (SEO)')
print('=' * 72)
for pola, label in [
    (r'<title>(.*?)</title>', 'title'),
    (r'<meta name="description" content="([^"]*)"', 'description'),
    (r'<meta property="og:title" content="([^"]*)"', 'og:title'),
    (r'<meta property="og:description" content="([^"]*)"', 'og:description'),
    (r'<meta property="og:image" content="([^"]*)"', 'og:image'),
    (r'<meta property="og:type" content="([^"]*)"', 'og:type'),
]:
    m = re.search(pola, html, re.S | re.I)
    if m:
        print(f'  {label:16}: {m.group(1).strip()[:150]}')
