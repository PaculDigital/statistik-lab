#!/usr/bin/env python3
"""POTRET halaman /belajar dari server uji — untuk DIPERIKSA MATA (vision).

Menyalakan server dari BERKAS yang akan di-deploy, lalu Chrome headless
memotret: (1) tab Heteroskedastisitas dengan tombol pintasan,
(2) tab Normalitas, (3) kondisi sehat (slider 0).

Pakai: .venv/bin/python _sketsa/potret_belajar.py
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import websocket

DIR = Path(__file__).resolve().parent.parent
CH = '/opt/data/home/.cloakbrowser/chromium-151.0.7922.108.6-pro/chrome'
P_SRV, P_CDP = 8161, 9355
SHOT = Path('/tmp/shot')
SHOT.mkdir(parents=True, exist_ok=True)


class Tab:
    def __init__(self, port: int):
        self.port = port
        self.n = 0
        self.ws = None

    def buka(self) -> None:
        for _ in range(40):
            try:
                urllib.request.urlopen(
                    f'http://127.0.0.1:{self.port}/json/version', timeout=2)
                break
            except Exception:
                time.sleep(0.5)
        # buang tab sisa
        try:
            with urllib.request.urlopen(
                    f'http://127.0.0.1:{self.port}/json/list', timeout=5) as r:
                for t in json.loads(r.read().decode()):
                    if t.get('type') == 'page':
                        try:
                            urllib.request.urlopen(
                                f'http://127.0.0.1:{self.port}'
                                f'/json/close/{t["id"]}', timeout=3).read()
                        except Exception:
                            pass
        except Exception:
            pass
        req = urllib.request.Request(
            f'http://127.0.0.1:{self.port}/json/new', method='PUT')
        with urllib.request.urlopen(req, timeout=20) as r:
            t = json.loads(r.read().decode())
        self.ws = websocket.create_connection(
            t['webSocketDebuggerUrl'], timeout=30)
        self.kirim('Page.enable')

    def kirim(self, metode: str, **kw) -> dict:
        self.n += 1
        mid = self.n
        self.ws.send(json.dumps({'id': mid, 'method': metode, 'params': kw}))
        while True:
            m = json.loads(self.ws.recv())
            if m.get('id') == mid:
                return m

    def js(self, expr: str):
        self.n += 1
        mid = self.n
        self.ws.send(json.dumps({'id': mid, 'method': 'Runtime.evaluate',
                                 'params': {'expression': expr,
                                            'returnByValue': True}}))
        while True:
            m = json.loads(self.ws.recv())
            if m.get('id') == mid:
                rr = m.get('result', {})
                if 'exceptionDetails' in rr:
                    return '❌ ' + str(rr['exceptionDetails'].get(
                        'exception', {}).get('description'))[:250]
                return rr.get('result', {}).get('value')

    def potret(self, nama: str, tinggi: int = 2600) -> None:
        self.kirim('Emulation.setDeviceMetricsOverride', width=390,
                   height=tinggi, deviceScaleFactor=2, mobile=True)
        time.sleep(1.2)
        r = self.kirim('Page.captureScreenshot', format='png')
        import base64
        (SHOT / nama).write_bytes(
            base64.b64decode(r['result']['data']))
        print(f'  potret: {SHOT / nama}')


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

    subprocess.Popen(
        [CH, '--headless=new', '--no-sandbox', '--disable-gpu',
         f'--remote-debugging-port={P_CDP}', '--remote-allow-origins=*',
         '--window-size=390,900', '--hide-scrollbars'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    try:
        t = Tab(P_CDP)
        t.buka()
        t.kirim('Page.navigate', url=f'http://127.0.0.1:{P_SRV}/belajar')
        time.sleep(4)

        # ── hetero (bawaan) ─────────────────────────────────────────────
        t.js("document.getElementById('slider').value = 35;"
             "document.getElementById('slider').dispatchEvent("
             "new Event('input',{bubbles:true})); 1")
        time.sleep(1)
        t.potret('belajar_hetero.png')

        # ── normalitas ──────────────────────────────────────────────────
        t.js("[...document.querySelectorAll('.kamus-tombol')]"
             ".find(b => b.dataset.k === 'normalitas').click(); 1")
        time.sleep(1.2)
        t.potret('belajar_normalitas.png')

        # ── hetero SEHAT (0) ────────────────────────────────────────────
        t.js("[...document.querySelectorAll('.kamus-tombol')]"
             ".find(b => b.dataset.k === 'hetero').click(); 1")
        time.sleep(0.8)
        t.js("document.getElementById('pintasan-sehat').click(); 1")
        time.sleep(1.2)
        t.potret('belajar_hetero_sehat.png')

        # ringkasan teks
        ringkas = t.js("""JSON.stringify({
          entri: Object.keys(KAMUS),
          judulSehat: document.getElementById('pesan-isi').innerText.slice(0,120),
          pita: document.getElementById('pita-hasil').innerText
        })""")
        print('\nringkasan:', ringkas)
    finally:
        srv.terminate()
        try:
            srv.wait(timeout=5)
        except Exception:
            srv.kill()
    return 0


if __name__ == '__main__':
    sys.exit(main())
