#!/usr/bin/env python3
"""Cari BERKAS MANA yang 404 di halaman /belajar (dan halaman lain).

Terukur: Chrome mencatat 1 galat 404 di /belajar dan skrip ke-3 tidak jalan.
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
PORT = 8124


def main() -> int:
    env = dict(os.environ, PORT=str(PORT))
    srv = subprocess.Popen(
        [str(DIR / '.venv' / 'bin' / 'python'), '-m', 'uvicorn',
         'app.main:app', '--host', '127.0.0.1', '--port', str(PORT),
         '--log-level', 'warning'],
        cwd=str(DIR), env=env,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    base = f'http://127.0.0.1:{PORT}'
    for _ in range(40):
        try:
            urllib.request.urlopen(base + '/health', timeout=2)
            break
        except Exception:
            time.sleep(0.5)

    try:
        for hal in ['/belajar']:
            print(f'══ {hal} ══')
            html = urllib.request.urlopen(base + hal, timeout=10).read().decode()
            urls = sorted(set(re.findall(r'(?:src|href)="(/[^"]+)"', html)))
            for r in urls:
                try:
                    with urllib.request.urlopen(base + r, timeout=5) as rr:
                        print(f'  ✅ {rr.status}  {r}')
                except Exception as e:
                    kode = getattr(e, 'code', '???')
                    print(f'  ❌ {kode}  {r}   <-- RUSAK')
    finally:
        srv.terminate()
        try:
            srv.wait(timeout=5)
        except Exception:
            srv.kill()
    return 0


if __name__ == '__main__':
    sys.exit(main())
