#!/usr/bin/env python3
"""Bangun sprite ikon Lucide untuk Penelitian STATISTIK Lab.

Sprite = SATU berkas lucide.svg berisi <symbol> per ikon yang dipakai.
WAJIB inline di <body> (bukan <use href="file.svg#id">) — use lintas berkas
tidak jalan di sebagian peramban & WebView.

Pemeriksa bentuk dijalankan otomatis: rect/circle/ellipse/image TIDAK BOLEH
kehilangan atribut ukuran (bug 15Sep26 — gembok kehilangan kotaknya).
"""
import json
import re
import shutil
import subprocess
import sys
import tarfile
import urllib.request
from pathlib import Path

BASE = Path('/opt/data/services/statistik-lab')
OUT = BASE / 'app' / 'static' / 'ikon' / 'lucide.svg'
CACHE = Path('/tmp/lucide-x/package/icons')

# ── Daftar ikon (nama Lucide — SUDAH diverifikasi ada) ───────────────────
IKON = [
    # navigasi & modul
    'home', 'book-open', 'flask-conical', 'stethoscope', 'graduation-cap',
    'compass', 'settings', 'layout-grid', 'menu', 'chevron-right',
    'chevron-left', 'chevron-down', 'chevron-up', 'arrow-right', 'arrow-left',
    # tabel & data
    'table', 'database', 'file-spreadsheet', 'file-text', 'file-down',
    'download', 'upload', 'clipboard-list', 'list', 'grid-3x3',
    # statistik
    'trending-up', 'trending-down', 'bar-chart-3', 'line-chart', 'activity',
    'percent', 'divide', 'sigma', 'calculator', 'function-square',
    'scatter-chart',
    # model & jalur
    'git-branch', 'network', 'share-2', 'move-right', 'circle-dot',
    'boxes', 'workflow', 'split', 'merge',
    # status & tanda
    'check', 'check-circle-2', 'x', 'x-circle', 'alert-triangle',
    'alert-circle', 'info', 'help-circle', 'shield-check', 'shield-alert',
    # aksi
    'play', 'pause', 'refresh-cw', 'rotate-ccw', 'save', 'trash-2',
    'copy', 'eye', 'sparkles', 'wand-2', 'sliders-horizontal', 'filter',
    # orang & kelas
    'users', 'user', 'user-check', 'school', 'presentation', 'award',
    # misc
    'lightbulb', 'target', 'search', 'lock', 'unlock', 'zap', 'book-marked',
    'puzzle', 'rocket', 'timer', 'scale', 'ruler', 'gauge', 'microscope',
]


def pastikan_sumber() -> None:
    """Unduh lucide-static kalau belum ada di /tmp."""
    if CACHE.exists() and len(list(CACHE.glob('*.svg'))) > 100:
        print(f'  Sumber ikon sudah ada: {len(list(CACHE.glob("*.svg")))} berkas')
        return
    print('  Mengunduh lucide-static dari npm registry...')
    meta = json.loads(urllib.request.urlopen(
        'https://registry.npmjs.org/lucide-static', timeout=30).read())
    versi = meta['dist-tags']['latest']
    tgz = f'/tmp/lucide-{versi}.tgz'
    urllib.request.urlretrieve(
        f'https://registry.npmjs.org/lucide-static/-/lucide-static-{versi}.tgz', tgz)
    shutil.rmtree('/tmp/lucide-x', ignore_errors=True)
    Path('/tmp/lucide-x').mkdir(parents=True, exist_ok=True)
    with tarfile.open(tgz) as t:
        t.extractall('/tmp/lucide-x')
    print(f'  lucide-static {versi}: {len(list(CACHE.glob("*.svg")))} ikon tersedia')


def ambil(nama: str) -> str | None:
    p = CACHE / f'{nama}.svg'
    if not p.exists():
        return None
    isi = p.read_text(encoding='utf-8')
    # buang tag <svg ...> pembungkus, ambil isinya saja
    m = re.search(r'<svg[^>]*>(.*)</svg>', isi, re.S)
    return m.group(1).strip() if m else None


def bangun() -> int:
    pastikan_sumber()
    ada, hilang = [], []
    simbol = []
    for n in IKON:
        isi = ambil(n)
        if isi is None:
            hilang.append(n)
            continue
        ada.append(n)
        simbol.append(
            f'<symbol id="ik-{n}" viewBox="0 0 24 24" fill="none" '
            f'stroke="currentColor" stroke-width="2" stroke-linecap="round" '
            f'stroke-linejoin="round">{isi}</symbol>')

    svg = ('<svg xmlns="http://www.w3.org/2000/svg" style="display:none" '
           'aria-hidden="true">\n' + '\n'.join(simbol) + '\n</svg>\n')
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(svg, encoding='utf-8')

    print(f'\n  ✅ Sprite: {OUT}')
    print(f'     {len(ada)} ikon · {OUT.stat().st_size / 1024:.1f} KB')
    if hilang:
        print(f'  ⚠️  TIDAK ADA di Lucide ({len(hilang)}): {hilang}')

    # ── PEMERIKSA BENTUK ────────────────────────────────────────────────
    perlu = {'rect': ['width', 'height'], 'circle': ['r'],
             'ellipse': ['rx', 'ry'], 'image': ['width', 'height']}
    rusak = 0
    for m in re.finditer(r'<symbol id="(ik-[a-z0-9-]+)"[^>]*>(.*?)</symbol>',
                         svg, re.S):
        for t in re.finditer(r'<(\w+)([^>]*)/?>', m.group(2)):
            tag, atr = t.group(1), t.group(2)
            if tag in perlu:
                kurang = [k for k in perlu[tag]
                          if not re.search(r'\b%s="' % k, atr)]
                if kurang:
                    print(f'  ❌ RUSAK: {m.group(1)} <{tag}> kurang {kurang}')
                    rusak += 1
    if rusak == 0:
        print('  ✅ Pemeriksa bentuk: semua rect/circle/ellipse UTUH')
    return 0 if rusak == 0 else 1


if __name__ == '__main__':
    sys.exit(bangun())
