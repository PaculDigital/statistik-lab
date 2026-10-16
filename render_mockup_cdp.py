#!/usr/bin/env python3
"""Render mockup dengan CDP — KLIK SUNGGUHAN lalu potret.

KENAPA pakai CDP (bukan `chrome --screenshot`):
  `--screenshot` TIDAK menunggu skrip klik selesai. Terukur 18Sep26:
  7 keadaan dihasilkan dengan UKURAN IDENTIK (233091 byte) → gambar sama →
  klik otomatis tidak berpengaruh. Pelajaran: "hasil identik = perubahan
  tidak berpengaruh".

Pakai: .venv/bin/python render_mockup_cdp.py
"""
from __future__ import annotations

import base64
import json
import subprocess
import time
import urllib.request
from pathlib import Path

import websocket

BASE = Path(__file__).resolve().parent
CHROME = '/opt/data/home/.cloakbrowser/chromium-146.0.7680.177.5/chrome'
MOCK = BASE / '_arsip' / 'mockup_setelan_model.html'
KELUAR = BASE / '_arsip' / 'shot'
KELUAR.mkdir(parents=True, exist_ok=True)
PORT = 9331

KEADAAN = [
    ('langsung', 'langsung', 0, 0, 1100),
    ('perantara', 'perantara', 0, 0, 1100),
    ('perantara_dual', 'perantara', 2, 0, 1100),
    ('penguat', 'penguat', 0, 0, 1100),
    ('keduanya', 'keduanya', 0, 0, 1100),
    ('hp_langsung', 'langsung', 0, 0, 390),
    ('hp_keduanya', 'keduanya', 0, 0, 390),
]


class Sisi:
    """Pembungkus CDP sederhana."""

    def __init__(self, ws):
        self.ws = ws
        self.n = 0

    def kirim(self, metode: str, **kw) -> dict:
        self.n += 1
        self.ws.send(json.dumps({'id': self.n, 'method': metode, 'params': kw}))
        while True:
            d = json.loads(self.ws.recv())
            if d.get('id') == self.n:
                if 'error' in d:
                    raise RuntimeError(f'{metode}: {d["error"]}')
                return d.get('result', {})

    def js(self, expr: str):
        r = self.kirim('Runtime.evaluate', expression=expr,
                       returnByValue=True, awaitPromise=True)
        return r.get('result', {}).get('value')

    def tunggu(self, detik: float = 0.45):
        time.sleep(detik)


def main() -> int:
    # ── 1. jalankan chrome dengan port debug ──
    proses = subprocess.Popen([
        CHROME, '--headless=new', '--disable-gpu', '--no-sandbox',
        '--hide-scrollbars', '--remote-allow-origins=*',
        '--remote-debugging-port=%d' % PORT,
        '--window-size=1200,900', 'about:blank',
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
        except Exception:                               # noqa: BLE001
            pass
        time.sleep(0.5)
    if not url_ws:
        print('❌ Chrome debug tidak siap')
        proses.kill()
        return 1

    ws = websocket.create_connection(url_ws, timeout=25)
    s = Sisi(ws)
    s.kirim('Page.enable')
    s.kirim('Runtime.enable')

    asal = f'file://{MOCK}'
    print('═' * 70)
    print('  RENDER MOCKUP via CDP — klik SUNGGUHAN lalu potret')
    print('═' * 70)

    gagal, ukuran = 0, {}
    for nama, bentuk, klik_m, klik_z, lebar in KEADAAN:
        # atur ukuran jendela (HP atau desktop)
        s.kirim('Emulation.setDeviceMetricsOverride',
                width=lebar, height=900, deviceScaleFactor=1, mobile=(lebar < 500))
        s.kirim('Page.navigate', url=asal)
        s.tunggu(0.9)

        # KLIK kartu bentuk
        s.js(f"document.querySelector('[data-bentuk=\"{bentuk}\"]').click();")
        s.tunggu(0.25)
        for _ in range(klik_m):
            s.js("document.getElementById('btn-m').click();")
            s.tunggu(0.2)
        for _ in range(klik_z):
            s.js("document.getElementById('btn-z').click();")
            s.tunggu(0.2)

        # pastikan klik BERBEKAS: baca bentuk terpakai
        terpakai = s.js("document.getElementById('bentuk-terpakai').textContent")
        tinggi = s.js("Math.ceil(document.body.scrollHeight)") or 2400
        s.kirim('Emulation.setDeviceMetricsOverride',
                width=lebar, height=min(int(tinggi) + 40, 8000),
                deviceScaleFactor=1, mobile=(lebar < 500))
        s.tunggu(0.5)

        r = s.kirim('Page.captureScreenshot', format='png', captureBeyondViewport=True)
        kel = KELUAR / f'mockup_{nama}.png'
        kel.write_bytes(base64.b64decode(r['data']))
        ukuran[nama] = kel.stat().st_size
        ok = kel.stat().st_size > 20000
        gagal += 0 if ok else 1
        print(f'   {"✅" if ok else "❌"} {nama:16} {lebar:4}px  '
              f'{kel.stat().st_size:7} byte   [{terpakai[:58]}]')

    ws.close()
    proses.kill()

    # ── periksa: apakah gambar BENAR-BENAR berbeda? ──
    print('\n  ── PERIKSA GAMBAR BENAR-BENAR BERBEDA ──')
    unik = len(set(ukuran.values()))
    print(f'   ukuran unik: {unik} dari {len(ukuran)} keadaan')
    if unik < len(ukuran) - 1:
        print('   ⚠️  banyak ukuran SAMA → klik mungkin tidak berpengaruh')
        gagal += 1
    else:
        print('   ✅ tiap keadaan menghasilkan gambar berbeda')
    return 1 if gagal else 0


if __name__ == '__main__':
    raise SystemExit(main())
