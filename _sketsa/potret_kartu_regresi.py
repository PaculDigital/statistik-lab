"""POTRET kartu Regresi di /kuantitatif — bukti visual untuk Bos."""
from __future__ import annotations

import base64
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import websocket

PORT, PORT_UJI = 9333, 8122
BASE = f'http://127.0.0.1:{PORT_UJI}'
DIR = Path(__file__).resolve().parent.parent
PY = DIR / '.venv' / 'bin' / 'python'


def hidup():
    try:
        return urllib.request.urlopen(f'http://127.0.0.1:{PORT_UJI}/health',
                                      timeout=3).status == 200
    except Exception:
        return False


def siapkan():
    if hidup():
        return True
    os.environ['PORT'] = str(PORT_UJI)
    subprocess.Popen([str(PY), '-m', 'uvicorn', 'app.main:app',
                      '--host', '127.0.0.1', '--port', str(PORT_UJI),
                      '--log-level', 'warning'],
                     cwd=str(DIR), stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL)
    for _ in range(60):
        if hidup():
            return True
        time.sleep(0.5)
    return False


def main():
    if not siapkan():
        print('server gagal')
        return 1
    # bersihkan tab nyangkut
    try:
        d = json.load(urllib.request.urlopen(f'http://127.0.0.1:{PORT}/json/list',
                                             timeout=8))
        for t in d:
            if t.get('type') == 'page':
                try:
                    urllib.request.urlopen(
                        f'http://127.0.0.1:{PORT}/json/close/{t["id"]}',
                        timeout=8).read()
                except Exception:
                    pass
    except Exception:
        pass
    time.sleep(0.5)

    t = json.loads(urllib.request.urlopen(urllib.request.Request(
        f'http://127.0.0.1:{PORT}/json/new?about:blank', method='PUT'),
        timeout=20).read())
    ws = websocket.create_connection(t['webSocketDebuggerUrl'], timeout=90)
    n = 0

    def cmd(m, **p):
        nonlocal n
        n += 1
        ws.send(json.dumps({'id': n, 'method': m, 'params': p}))
        while True:
            r = json.loads(ws.recv())
            if r.get('id') == n:
                return r

    def js(e):
        r = cmd('Runtime.evaluate', expression=e, returnByValue=True,
                awaitPromise=True)
        return r.get('result', {}).get('result', {}).get('value')

    cmd('Page.enable')
    cmd('Runtime.enable')
    cmd('Emulation.setDeviceMetricsOverride',
        width=430, height=760, deviceScaleFactor=2, mobile=True)
    cmd('Page.navigate', url=BASE + '/kuantitatif')
    time.sleep(5)
    print('url:', js('location.href'))
    # buka panel sub-regresi
    js("typeof bukaSub === 'function' && bukaSub(null, 'regresi')")
    time.sleep(2)

    # potret panel sub-regresi
    kotak = js("""(() => {
      const p = document.getElementById('sub-regresi');
      if (!p) return null;
      const r = p.getBoundingClientRect();
      return {x: Math.round(r.x), y: Math.round(r.y + window.scrollY),
              w: Math.round(r.width), h: Math.round(r.height)};
    })()""")
    print('kotak panel:', kotak)

    out = DIR / '_bukti_kartu_regresi.png'
    shot = cmd('Page.captureScreenshot',
               format='png', captureBeyondViewport=True,
               clip={'x': kotak['x'], 'y': kotak['y'], 'width': kotak['w'], 'height': kotak['h'], 'scale': 2} if kotak else None)
    data = shot.get('result', {}).get('data')
    if not data:
        print('❌ potret gagal:', json.dumps(shot)[:200])
        return 1
    out.write_bytes(base64.b64decode(data))
    print(f'✅ potret: {out}  ({out.stat().st_size} byte)')

    # potret juga /buat-data (kartu cara)
    cmd('Page.navigate', url=BASE + '/buat-data?model=sederhana')
    time.sleep(5)
    print('url2:', js('location.href'))
    k2 = js("""(() => {
      const k = document.getElementById('cara-kisi');
      if (!k) return null;
      const r = k.getBoundingClientRect();
      return {x: Math.round(r.x), y: Math.round(r.y + window.scrollY),
              w: Math.round(r.width), h: Math.round(r.height)};
    })()""")
    shot2 = cmd('Page.captureScreenshot',
                format='png', captureBeyondViewport=True,
                clip={'x': k2['x'], 'y': k2['y'], 'width': k2['w'], 'height': k2['h'], 'scale': 2} if k2 else None)
    d2 = shot2.get('result', {}).get('data')
    if d2:
        out2 = DIR / '_bukti_kartu_cara.png'
        out2.write_bytes(base64.b64decode(d2))
        print(f'✅ potret: {out2}  ({out2.stat().st_size} byte)')
    try:
        urllib.request.urlopen(f'http://127.0.0.1:{PORT}/json/close/{t["id"]}',
                               timeout=10).read()
    except Exception:
        pass
    return 0


if __name__ == '__main__':
    sys.exit(main())
