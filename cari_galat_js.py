#!/usr/bin/env python3
"""Tangkap galat JS di halaman pakai Chrome DevTools Protocol lewat websocket.

Kalau tidak ada websocket-client, pakai cara cadangan: suntikkan penangkap
galat ke halaman lewat proxy sederhana.

CARA YANG DIPAKAI: kita tambahkan penangkap galat ke halaman web sungguhan
lewat parameter ?uji= — TAPI karena skrip mati sebelum baris itu, kita
sebaliknya menyuntikkan skrip penangkap PALING ATAS lewat berkas terpisah
yang dimuat lebih dulu (dasar.html sudah punya <script> untuk aman()).
"""
import re
import subprocess
import sys

CHROME = '/opt/data/home/.cloakbrowser/chromium-151.0.7922.108.6-pro/chrome'
ip = subprocess.run(
    ['docker', 'inspect', '-f',
     '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}',
     'simulasi-olah-data'], capture_output=True, text=True).stdout.strip()

# Buka halaman dengan --dump-dom; galat JS muncul di stderr kalau kita
# aktifkan log konsol. Chrome headless menulis galat konsol ke stderr
# dengan --enable-logging=stderr --log-level=0.
p = subprocess.run(
    [CHROME, '--headless', '--disable-gpu', '--no-sandbox',
     '--window-size=1280,900', '--virtual-time-budget=9000',
     '--enable-logging=stderr', '--log-level=0',
     '--dump-dom', f'http://{ip}:8000/buat-data'],
    capture_output=True, text=True, timeout=170)

print('═══ GALAT JS YANG DITANGKAP ═══')
ada = False
for baris in (p.stderr or '').splitlines():
    b = baris.lower()
    if any(k in b for k in ['uncaught', 'syntaxerror', 'referenceerror',
                            'typeerror', 'is not defined', 'unexpected']):
        print('  ' + baris.strip()[:220])
        ada = True
if not ada:
    print('  (tidak ada galat JS terdeteksi di stderr)')
    print()
    print('  Petunjuk: cek panjang DOM dan keberadaan #jejak')
    print('  panjang DOM:', len(p.stdout))
