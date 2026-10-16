#!/usr/bin/env python3
"""RENDER SKETSA + POTONG RUANG PUTIH OTOMATIS (18Sep26).

MENGAPA BERKAS INI ADA:
Sketsa pertama Wulan dirender di jendela 430px, padahal isi halaman butuh
lebih lebar → SEMUA sisi kanan terpotong (ditemukan vision, bukan dikira).
Menebak lebar jendela = menebak. Cara yang benar: render di jendela SANGAT
besar, lalu UKUR sampai mana isi sesungguhnya, dan potong sisanya.

CARA JALAN: .venv/bin/python _sketsa/render_sketsa.py
"""
from __future__ import annotations

import pathlib
import subprocess

CH = '/opt/data/home/.cloakbrowser/chromium-146.0.7680.177.5/chrome'
OUT = pathlib.Path('/tmp/shot')


def render(nama: str) -> pathlib.Path:
    f = OUT / f'sketsa_{nama}.html'
    png = OUT / f'sketsa_{nama}.png'
    # jendela besar: 820 cukup untuk tampilan HP-lebar, tinggi longgar
    subprocess.run([CH, '--headless=new', '--no-sandbox', '--disable-gpu',
                    '--hide-scrollbars', '--window-size=820,2600',
                    f'--screenshot={png}', f'file://{f}'],
                   capture_output=True, timeout=150)
    return png


def potong_putih(png: pathlib.Path) -> None:
    """Buang tepi putih/kertas di kanan & bawah supaya tidak ada sisa kosong."""
    try:
        from PIL import Image, ImageChops
    except ImportError:
        print('  (PIL tidak ada — lewati pemotongan)')
        return
    im = Image.open(png).convert('RGB')
    w, h = im.size
    latar = im.getpixel((w - 3, h - 3))          # warna kertas di sudut
    dasar = Image.new('RGB', im.size, latar)
    kotak = ImageChops.difference(im, dasar).getbbox()
    if not kotak:
        return
    kiri, atas, kanan, bawah = kotak
    pad = 14
    im.crop((max(0, kiri - pad), max(0, atas - pad),
             min(w, kanan + pad), min(h, bawah + pad))).save(png)
    print(f'  dipotong: {w}×{h} → {min(w, kanan + pad) - max(0, kiri - pad)}'
          f'×{min(h, bawah + pad) - max(0, atas - pad)}')


if __name__ == '__main__':
    for nama in ['uji_t_A', 'uji_t_B']:
        p = render(nama)
        if p.exists() and p.stat().st_size > 20000:
            print(f'{nama}: {p} {p.stat().st_size} byte')
            potong_putih(p)
            print(f'  akhir: {p.stat().st_size} byte')
        else:
            print(f'{nama}: GAGAL')
