#!/usr/bin/env python3
"""POTRET /belajar TANPA CDP — pakai Chrome --screenshot (pola terbukti).

Pelajaran 20Sep26: CDP websocket putus-putus ("Connection to remote host was
lost") kalau Chrome sisa masih hidup. Chrome `--headless --screenshot` TIDAK
butuh websocket sama sekali → jauh lebih andal untuk sekadar melihat.

Cara memilih istilah: halaman /belajar membaca `location.hash` untuk tab,
tapi istilah kamus dipilih lewat `pilih('nama')`. Karena itu kita buat
HALAMAN PEMBANTU kecil yang memanggil pilih() lewat hash, lalu Chrome
memotretnya. Tidak menyentuh aplikasi sama sekali.

Pakai: .venv/bin/python _sketsa/potret_belajar2.py
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

DIR = Path(__file__).resolve().parent.parent
CH = '/opt/data/home/.cloakbrowser/chromium-151.0.7922.108.6-pro/chrome'
P_SRV = 8162
SHOT = Path('/tmp/shot')
SHOT.mkdir(parents=True, exist_ok=True)

# halaman pembantu: buka /belajar di iframe? TIDAK — Chrome --screenshot hanya
# memotret URL yg diberikan. Jadi: inject lewat query yang dibaca halaman?
# Halaman /belajar tidak mendukung itu. Solusi paling jujur: potret apa adanya
# (bawaan = hetero), LALU untuk normalitas pakai potret ber-hash.
# Cek dulu: apakah /belajar mendukung #tab-N saja?


def potret(url: str, nama: str, tinggi: int, tunggu: int = 3) -> bool:
    out = SHOT / nama
    if out.exists():
        out.unlink()
    p = subprocess.run(
        [CH, '--headless=new', '--no-sandbox', '--disable-gpu',
         '--hide-scrollbars', f'--window-size=430,{tinggi}',
         '--virtual-time-budget=8000',
         f'--screenshot={out}', url],
        capture_output=True, text=True, timeout=120)
    ok = out.exists() and out.stat().st_size > 1000
    print(f'  {"✅" if ok else "❌"} {nama}'
          + (f'  ({out.stat().st_size} byte)' if ok else ''))
    if not ok and p.stderr:
        print('     ' + p.stderr.strip()[:200])
    return ok


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

    base = f'http://127.0.0.1:{P_SRV}/belajar'
    try:
        potret(base, 'b_hetero.png', 2400)
        potret(f'{base}#tab-2', 'b_normalitas.png', 2400)
        potret(f'{base}?kamus=normalitas', 'b_normalitas2.png', 2400)
    finally:
        srv.terminate()
        try:
            srv.wait(timeout=5)
        except Exception:
            srv.kill()

    # ukur tinggi isi sebenarnya (untuk potong)
    print('\n── ukur tinggi tiap potret ──')
    for f in sorted(SHOT.glob('b_*.png')):
        print(f'  {f.name}: {f.stat().st_size} byte')
    return 0


if __name__ == '__main__':
    sys.exit(main())
