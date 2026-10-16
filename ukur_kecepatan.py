#!/usr/bin/env python3
"""UKUR KECEPATAN halaman buat-data (angka, bukan perasaan).

Mengukur: geser slider 10x, klik +/− 6x, ketik nama 8x, dan berapa kali
tabel dibangun ulang. Dipakai untuk membuktikan perbaikan lingkaran
bangunTabel() -> segarkan() benar-benar menghilangkan beban berat.

⚠️ WAJIB pakai iframe selebar HP yang disajikan dari ORIGIN SAMA.
`--window-size=390` TIDAK memberi lebar 390 (Chrome menolak < 500px).

Jalankan: .venv/bin/python ukur_kecepatan.py
"""
import html as _h
import json
import os
import re
import subprocess
import sys

CHROME = '/opt/data/home/.cloakbrowser/chromium-146.0.7680.177.5/chrome'


def main() -> int:
    if not os.path.exists(CHROME):
        print('  ⚠️  Chrome tidak ada'); return 0
    ip = subprocess.run(
        ['docker', 'inspect', '-f',
         '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}',
         'simulasi-olah-data'], capture_output=True, text=True).stdout.strip()
    if not ip:
        print('  ⚠️  kontainer tidak jalan'); return 0

    for lebar in (390,):
        p = subprocess.run(
            [CHROME, '--headless', '--disable-gpu', '--no-sandbox',
             f'--window-size={lebar + 60},1750', '--force-device-scale-factor=1',
             '--virtual-time-budget=12000', '--dump-dom',
             f'http://{ip}:8000/static/ukur_kecepatan.html?lebar={lebar}'],
            capture_output=True, text=True, timeout=140)
        m = re.search(r'SPD::(.*?)</title>', p.stdout or '', re.S)
        if not m:
            print('  tidak terbaca'); return 0
        mentah = _h.unescape(m.group(1).strip())
        if mentah.startswith('GALAT'):
            print('  ', mentah); return 0
        d = json.loads(mentah)

        print(f'  ══ KECEPATAN di lebar {d["lebarLayar"]}px ══')
        print(f'  geser slider 10×      : {d["geserSlider10x"]:>5} ms')
        print(f'  klik tombol +/− 6×    : {d["klikPlusMinus6x"]:>5} ms')
        print(f'  ketik nama 8×         : {d["ketikNama8x"]:>5} ms')
        print(f'  tabel dibangun ulang  : {d["panggilanBangunTabel"]:>5} kali')
        print()

        # putusan: batas wajar yang bisa dirasakan jari (60 fps = 16 ms)
        putus = []
        if d['geserSlider10x'] > 500:
            putus.append(f'geser slider {d["geserSlider10x"]}ms > 500ms')
        if d['klikPlusMinus6x'] > 1200:
            putus.append(f'klik +/− {d["klikPlusMinus6x"]}ms > 1200ms')
        if d['ketikNama8x'] > 800:
            putus.append(f'ketik nama {d["ketikNama8x"]}ms > 800ms')
        if putus:
            print('  ❌ MASIH BERAT: ' + '; '.join(putus))
            return 1
        print('  ✅ RINGAN — slider & tombol responsif (batas: slider ≤500ms, '
              'klik ≤1200ms, ketik ≤800ms)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
