#!/usr/bin/env python3
"""CARI BARIS PERSIS SyntaxError di skrip /belajar — pakai Node.js (tanpa browser).

Node sudah ada (v26.5.1). Ini jauh lebih jujur daripada menebak lewat browser:
  1. Ambil HTML /belajar dari server uji (berkas yang AKAN di-deploy).
  2. Keluarkan isi <script> ke berkas .js sementara.
  3. node --check → Node melaporkan baris & kolom persis.

Pakai: .venv/bin/python _sketsa/cari_baris_salah.py
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

DIR = Path(__file__).resolve().parent.parent
P_SRV = 8152
TMP = Path('/opt/data/tmp_sintaks')
TMP.mkdir(parents=True, exist_ok=True)


def main() -> int:
    env = dict(os.environ, PORT=str(P_SRV))
    srv = subprocess.Popen(
        [str(DIR / '.venv' / 'bin' / 'python'), '-m', 'uvicorn',
         'app.main:app', '--host', '127.0.0.1', '--port', str(P_SRV),
         '--log-level', 'warning'],
        cwd=str(DIR), env=env,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(40):
        try:
            urllib.request.urlopen(f'http://127.0.0.1:{P_SRV}/health',
                                   timeout=2)
            break
        except Exception:
            time.sleep(0.5)

    try:
        html = urllib.request.urlopen(
            f'http://127.0.0.1:{P_SRV}/belajar', timeout=10).read().decode()

        # ambil SEMUA <script> tanpa src (inline)
        inline = re.findall(r'<script>(.*?)</script>', html, re.S)
        print(f'jumlah <script> inline: {len(inline)}')
        for i, isi in enumerate(inline):
            f = TMP / f'skrip_{i}.js'
            f.write_text(isi, encoding='utf-8')
            p = subprocess.run(['node', '--check', str(f)],
                               capture_output=True, text=True)
            if p.returncode == 0:
                print(f'  ✅ skrip_{i}.js ({len(isi)} byte) — sintaks OK')
            else:
                print(f'  ❌ skrip_{i}.js ({len(isi)} byte) — SYNTAX ERROR')
                print('     ' + (p.stderr.strip().replace('\n', '\n     ')))

                # tunjukkan baris terdakwa
                m = re.search(r'skrip_\d+\.js:(\d+)', p.stderr)
                if m:
                    no = int(m.group(1))
                    baris = isi.split('\n')
                    print(f'\n     ── 12 baris sekitar baris {no} ──')
                    for j in range(max(0, no - 12), min(len(baris), no + 6)):
                        tanda = '>>>' if j == no - 1 else '   '
                        print(f'     {tanda} {j+1:4}: {baris[j][:150]}')
    finally:
        srv.terminate()
        try:
            srv.wait(timeout=5)
        except Exception:
            srv.kill()
    return 0


if __name__ == '__main__':
    sys.exit(main())
