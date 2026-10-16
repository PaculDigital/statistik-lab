#!/usr/bin/env python3
"""GERBANG: galat JavaScript di halaman web.

AKAR yang dijaga: galat JS seperti
    "SyntaxError: Identifier 'x' has already been declared"
membuat SELURUH blok <script> MATI. Halaman tetap tampak rapi (HTML-nya tetap
terkirim), jadi uji HTTP 200 GAGAL MENANGKAPNYA. Gejalanya halus: tabel kosong,
tombol tidak berfungsi — hanya ketahuan kalau dilihat mata.

CARA KERJA (penting, hindari lingkaran mati):
  JANGAN menguji kontainer lama — kalau begitu gerbang selalu gagal sebelum
  deploy dan deploy tidak pernah jalan. Gerbang ini memeriksa SINTAKS blok
  <script> dari BERKAS template memakai node, jadi menguji kode yang AKAN
  di-deploy, bukan yang sedang jalan.

Kalau node tidak ada, jatuh ke Chrome headless sebagai cadangan.
"""
import glob
import os
import re
import shutil
import subprocess
import sys

CHROME_KANDIDAT = [
    '/opt/data/home/.cloakbrowser/chromium-151.0.7922.108.6-pro/chrome',
    '/opt/data/home/.cloakbrowser/chromium-151.0.7922.108.4-pro/chrome',
]

KATA_GALAT = ['uncaught', 'syntaxerror', 'referenceerror', 'typeerror',
              'is not defined', 'unexpected token', 'is not a function']


def nodejs():
    return shutil.which('node')


def chrome():
    for c in CHROME_KANDIDAT:
        if os.path.exists(c):
            return c
    p = subprocess.run(['find', '/opt/data/home/.cloakbrowser', '-maxdepth', '2',
                        '-name', 'chrome', '-type', 'f'],
                       capture_output=True, text=True)
    for baris in (p.stdout or '').splitlines():
        if baris.strip():
            return baris.strip()
    return None


def bersihkan_jinja(blok: str) -> str:
    """Ganti sintaks Jinja supaya blok JS bisa diperiksa node."""
    b = re.sub(r'\{\{.*?\}\}', '0', blok, flags=re.S)
    b = re.sub(r'\{%.*?%\}', '', b, flags=re.S)
    b = re.sub(r'\{#.*?#\}', '', b, flags=re.S)
    return b


def periksa_sintaks_node() -> int:
    node = nodejs()
    print('═══ GERBANG: sintaks JavaScript (periksa BERKAS, bukan kontainer) ═══')
    total_blok = 0
    galat_semua = []

    for P in sorted(glob.glob('app/templates/*.html')):
        s = open(P).read()
        pos = 0
        n = 0
        while True:
            a = s.find('<script>', pos)
            if a == -1:
                break
            b = s.find('</script>', a)
            if b == -1:
                break
            n += 1
            total_blok += 1
            blok = bersihkan_jinja(s[a + 8:b])
            p = subprocess.run([node, '--check'], input=blok,
                               capture_output=True, text=True)
            if p.returncode != 0:
                pesan = [x for x in (p.stderr or '').strip().splitlines() if x.strip()]
                ringkas = pesan[-1][:170] if pesan else 'galat sintaks'
                # nomor baris relatif ke blok
                m = re.search(r':(\d+)', ringkas)
                no = (s[:a].count('\n') + 1 + int(m.group(1)) - 1) if m else '?'
                galat_semua.append((P, no, ringkas))
            pos = b + 9
    print(f'  {total_blok} blok <script> diperiksa dari {len(glob.glob("app/templates/*.html"))} template')
    print()
    if galat_semua:
        for P, no, pesan in galat_semua:
            print(f'  ❌ {P}:{no}')
            print(f'       {pesan}')
        print()
        print(f'  {len(galat_semua)} blok skrip bermasalah — PERBAIKI dulu.')
        print('  Galat JS membuat SELURUH blok skrip mati walaupun halaman')
        print('  tetap tampak rapi dan HTTP 200 tetap hijau.')
        return 1
    print('  ✅ 0 galat sintaks JavaScript')
    return 0


def periksa_dengan_chrome(ch) -> int:
    ip = subprocess.run(
        ['docker', 'inspect', '-f',
         '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}',
         'simulasi-olah-data'], capture_output=True, text=True).stdout.strip()
    if not ip:
        print('  ⚠️  kontainer tidak jalan — gerbang JS dilewati')
        return 0

    print('═══ GERBANG: galat JavaScript (Chrome, kontainer) ═══')
    total = 0
    for jalur in ['/', '/belajar', '/buat-data', '/pengaturan', '/segera/klinik']:
        try:
            p = subprocess.run(
                [ch, '--headless', '--disable-gpu', '--no-sandbox',
                 '--window-size=1280,900', '--virtual-time-budget=7000',
                 '--enable-logging=stderr', '--log-level=0',
                 '--dump-dom', f'http://{ip}:8000{jalur}'],
                capture_output=True, text=True, timeout=120)
        except subprocess.TimeoutExpired:
            print(f'  ❌ {jalur}: waktu habis')
            total += 1
            continue
        galat = []
        for baris in (p.stderr or '').splitlines():
            b = baris.lower()
            if 'console' in b and any(k in b for k in KATA_GALAT):
                galat.append(re.sub(r'^.*?INFO:CONSOLE:\d+\]\s*', '',
                                    baris).strip()[:160])
        if galat:
            print(f'  ❌ {jalur}: {len(galat)} galat')
            for g in galat[:4]:
                print(f'       {g}')
            total += len(galat)
        else:
            print(f'  ✅ {jalur}: bersih')
    print()
    if total:
        print(f'  {total} galat JS — PERBAIKI dulu')
        return 1
    print('  ✅ 0 galat JS')
    return 0


def main() -> int:
    # Utamakan node: menguji BERKAS yang akan di-deploy → tidak ada lingkaran mati
    if nodejs():
        return periksa_sintaks_node()
    ch = chrome()
    if not ch:
        print('  ⚠️  node & Chrome tidak ada — gerbang JS dilewati')
        return 0
    return periksa_dengan_chrome(ch)


if __name__ == '__main__':
    sys.exit(main())
