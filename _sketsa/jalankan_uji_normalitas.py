#!/usr/bin/env python3
"""JALANKAN uji_normalitas.py dengan SERVER UJI SENDIRI (pola gerbang lama).

Menyalin pola gerbang_kode_tumpah.py: jalankan uvicorn dari BERKAS yang akan
di-deploy di port 8122, tunggu sehat, baru serahkan ke uji_normalitas.py.

Pakai: .venv/bin/python _sketsa/jalankan_uji_normalitas.py
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

DIR = Path(__file__).resolve().parent.parent
PY = DIR / '.venv' / 'bin' / 'python'
PORT = 8122
srv = None


def sehat() -> bool:
    try:
        return urllib.request.urlopen(
            f'http://127.0.0.1:{PORT}/health', timeout=3).status == 200
    except Exception:
        return False


def main() -> int:
    global srv
    if sehat():
        print(f'   (memakai server uji yang sudah jalan di :{PORT})')
    else:
        env = dict(os.environ, PORT=str(PORT))
        srv = subprocess.Popen(
            [str(PY), '-m', 'uvicorn', 'app.main:app',
             '--host', '127.0.0.1', '--port', str(PORT),
             '--log-level', 'warning'],
            cwd=str(DIR), env=env,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for i in range(40):
            if sehat():
                print(f'   server uji siap di :{PORT} setelah {i}s')
                break
            if srv.poll() is not None:
                print('❌ server uji mati saat start')
                return 2
            time.sleep(1)
        else:
            print('❌ server uji tidak pernah sehat')
            return 2

    try:
        return subprocess.run(
            [str(PY), str(DIR / 'uji_normalitas.py')],
            cwd=str(DIR)).returncode
    finally:
        if srv:
            srv.terminate()
            try:
                srv.wait(timeout=5)
            except Exception:
                srv.kill()


if __name__ == '__main__':
    sys.exit(main())
