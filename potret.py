#!/usr/bin/env python3
"""Potret halaman HTML apa pun via CDP (klik/JS SUNGGUHAN), lalu lapor ukuran.

KENAPA: `chrome --screenshot` TIDAK menunggu skrip selesai (terukur 18Sep26:
7 keadaan menghasilkan ukuran IDENTIK → gambar sama). CDP bisa menunggu lalu
memeriksa isi halaman lewat JS.

Pakai:
  .venv/bin/python potret.py <berkas-html> <keluaran.png> [lebar] [tinggi]
"""
from __future__ import annotations

import base64
import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import websocket

CHROME = '/opt/data/home/.cloakbrowser/chromium-146.0.7680.177.5/chrome'
PORT = 9333


class Sisi:
    def __init__(self, ws):
        self.ws, self.n = ws, 0

    def kirim(self, metode: str, **kw) -> dict:
        self.n += 1
        self.ws.send(json.dumps({'id': self.n, 'method': metode, 'params': kw}))
        while True:
            d = json.loads(self.ws.recv())
            if d.get('id') == self.n:
                if 'error' in d:
                    raise RuntimeError(f'{metode}: {d["error"]}')
                return d.get('result', {})

    def js(self, expr):
        r = self.kirim('Runtime.evaluate', expression=expr,
                       returnByValue=True, awaitPromise=True)
        return r.get('result', {}).get('value')


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    berkas = Path(sys.argv[1]).resolve()
    keluar = Path(sys.argv[2]).resolve()
    lebar = int(sys.argv[3]) if len(sys.argv) > 3 else 1100
    tinggi = int(sys.argv[4]) if len(sys.argv) > 4 else 3200

    proses = subprocess.Popen([
        CHROME, '--headless=new', '--disable-gpu', '--no-sandbox',
        '--hide-scrollbars', '--remote-allow-origins=*',
        f'--remote-debugging-port={PORT}', '--window-size=1200,900',
        'about:blank',
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    url_ws = None
    for _ in range(60):
        try:
            with urllib.request.urlopen(
                    f'http://127.0.0.1:{PORT}/json/list', timeout=2) as r:
                for t in json.load(r):
                    if t.get('type') == 'page':
                        url_ws = t['webSocketDebuggerUrl']
                        break
            if url_ws:
                break
        except Exception:                                   # noqa: BLE001
            pass
        time.sleep(0.5)
    if not url_ws:
        print('❌ Chrome debug tidak siap')
        proses.kill()
        return 1

    ws = websocket.create_connection(url_ws, timeout=30)
    s = Sisi(ws)
    s.kirim('Page.enable')
    s.kirim('Runtime.enable')
    s.kirim('Emulation.setDeviceMetricsOverride', width=lebar, height=900,
            deviceScaleFactor=1, mobile=(lebar < 500))
    s.kirim('Page.navigate', url=f'file://{berkas}')
    time.sleep(1.2)

    galat = s.js("(function(){var e=window.__GALAT_JS||[];return e.length?e.join(' | '):'';})()")
    ringkas = s.js("window.__RINGKAS ? window.__RINGKAS.join('\\n') : ''")
    tinggi_isi = s.js('Math.ceil(document.body.scrollHeight)') or tinggi
    s.kirim('Emulation.setDeviceMetricsOverride', width=lebar,
            height=min(int(tinggi_isi) + 40, 12000), deviceScaleFactor=1,
            mobile=(lebar < 500))
    time.sleep(0.6)
    r = s.kirim('Page.captureScreenshot', format='png', captureBeyondViewport=True)
    keluar.parent.mkdir(parents=True, exist_ok=True)
    keluar.write_bytes(base64.b64decode(r['data']))

    ws.close()
    proses.kill()

    print(f'   berkas   : {keluar}  ({keluar.stat().st_size} byte)')
    print(f'   lebar    : {lebar}px · tinggi isi {tinggi_isi}px')
    if ringkas:
        print('   ringkasan:')
        for baris in str(ringkas).split('\n'):
            print(f'      · {baris}')
    if galat:
        print(f'   ⚠️ GALAT JS: {galat}')
    # penjaga mutu: gambar < 20 KB biasanya kosong
    gagal = 0
    if keluar.stat().st_size < 20000:
        print('   ❌ gambar terlalu kecil — kemungkinan GAGAL')
        gagal = 1
    return gagal


if __name__ == '__main__':
    raise SystemExit(main())
