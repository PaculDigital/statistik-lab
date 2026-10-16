#!/usr/bin/env python3
"""Uji halaman BUAT DATA seperti USER — pakai Chrome DevTools Protocol.

Cara kerja: Chrome dibuka dengan --remote-debugging-port, lalu Wulan kirim
perintah JS (Runtime.evaluate) ke halaman yang SUDAH terbuka. Ini menguji
halaman asli, bukan iframe.

Tanpa library tambahan — pakai websocket lewat socket mentah tidak praktis,
jadi Wulan pakai /json/new untuk membuka tab, lalu ambil DOM hasil
render dengan /json + Runtime lewat HTTP endpoint.

CATATAN: Chrome headless tidak punya endpoint HTTP untuk Runtime.evaluate,
jadi cara paling andal = memakai --dump-dom SETELAH halaman mengubah dirinya
sendiri lewat parameter URL (?uji=...). Halaman buat_data.html mendukung
parameter itu.
"""
import subprocess
import sys

CHROME = '/opt/data/home/.cloakbrowser/chromium-151.0.7922.108.6-pro/chrome'

ip = subprocess.run(
    ['docker', 'inspect', '-f',
     '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}',
     'simulasi-olah-data'], capture_output=True, text=True).stdout.strip()

skenario = sys.argv[1] if len(sys.argv) > 1 else 'x8berat'
url = f'http://{ip}:8000/buat-data?uji={skenario}'

hasil = subprocess.run(
    [CHROME, '--headless', '--disable-gpu', '--no-sandbox',
     '--window-size=1000,900', '--virtual-time-budget=15000', '--dump-dom', url],
    capture_output=True, text=True, timeout=170).stdout

# Ambil jejak uji dari elemen <div id="jejak">
import re
import subprocess
import sys

# Ambil jejak uji dari <title> (paling andal di headless --dump-dom)
m = re.search(r'<title>(.*?)</title>', hasil, re.S)
if m and 'JEJAK::' in m.group(1):
    isi = m.group(1).split('JEJAK::', 1)[1]
    for baris in isi.split('||'):
        b = baris.strip()
        if b:
            print('  ' + b.replace('&gt;', '>').replace('&amp;', '&'))
else:
    # cadangan: elemen <div id="jejak">
    m2 = re.search(r'id="jejak"[^>]*>(.*?)</div>', hasil, re.S)
    if m2:
        for baris in m2.group(1).split('|'):
            b = baris.strip()
            if b:
                print('  ' + b)
    else:
        print('  (jejak tidak ditemukan)')
        print('  panjang DOM:', len(hasil))
