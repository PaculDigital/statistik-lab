#!/usr/bin/env python3
"""CEK MASALAH HP — ukur & laporkan APA yang menyebabkan halaman melebar.

Dipakai sebelum memperbaiki: lebih baik tahu elemen pelakunya daripada
menebak dari gambar. Jalankan: .venv/bin/python ukur_hp.py
"""
import html as _h
import json
import os
import re
import subprocess
import sys

CHROME = '/opt/data/home/.cloakbrowser/chromium-146.0.7680.177.5/chrome'
LEBAR = [412, 390, 375, 360]


def main() -> int:
    if not os.path.exists(CHROME):
        print('  ⚠️  Chrome tidak ada'); return 0
    ip = subprocess.run(
        ['docker', 'inspect', '-f',
         '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}',
         'simulasi-olah-data'], capture_output=True, text=True).stdout.strip()
    if not ip:
        print('  ⚠️  kontainer tidak jalan'); return 0

    for lebar in LEBAR:
        p = subprocess.run(
            [CHROME, '--headless', '--disable-gpu', '--no-sandbox',
             f'--window-size={lebar + 40},1700', '--virtual-time-budget=9000',
             '--dump-dom',
             f'http://{ip}:8000/static/ukur_hp.html?lebar={lebar}&tinggi=1600'],
            capture_output=True, text=True, timeout=140)
        m = re.search(r'HP::(.*?)</title>', p.stdout or '', re.S)
        if not m:
            print(f'  lebar {lebar}: tidak terbaca'); continue
        d = json.loads(_h.unescape(m.group(1).strip()))

        print(f'  ══ lebar {lebar}px (terukur {d["lebarLayar"]}px) ══')
        melebar = d['scrollW'] - d['lebarLayar']
        if melebar > 1:
            print(f'  ❌ MELEBAR {melebar}px  (scrollW {d["scrollW"]} > layar {d["lebarLayar"]})')
        else:
            print(f'  ✅ tidak melebar (scrollW {d["scrollW"]})')

        if d['pelaku']:
            print(f'  pelaku melebar ({len(d["pelaku"])} elemen):')
            for e in d['pelaku'][:6]:
                nm = e['tag'] + (f'#{e["id"]}' if e['id'] else '') + \
                     (f'.{e["cls"]}' if e['cls'] else '')
                print(f'    • {nm[:70]}  kanan={e["kanan"]} lebar={e["lebar"]}'
                      f'  "{e["teks"]}"')

        pr = d['preset']
        if pr:
            xs = [x['x'] for x in pr]
            ys = [x['cy'] for x in pr]
            naik = all(xs[i] < xs[i + 1] + 1 for i in range(len(xs) - 1))
            sebaris = (max(ys) - min(ys)) <= 12
            tanda = '✅' if (naik and sebaris) else '❌'
            print(f'  {tanda} preset {len(pr)} tombol: x={xs}, sebaran Y={max(ys) - min(ys)}px')
        print()
    return 0


if __name__ == '__main__':
    sys.exit(main())
