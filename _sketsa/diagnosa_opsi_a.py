"""DIAGNOSA OPSI A: Page.navigate tidak jalan — telusuri dengan attachToTarget.

Bedanya dengan uji lama: kita SIMPAN hasil Page.navigate & baca url setelah
tiap langkah, plus buktikan target mana yang benar-benar ter-attach.
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


def json_get(path):
    return json.load(urllib.request.urlopen(
        f'http://127.0.0.1:{PORT}{path}', timeout=10))


def main():
    if not siapkan():
        print('server gagal')
        return 1

    # ── 0. keadaan awal ──
    ver = json_get('/json/version')
    print('Browser :', ver.get('Browser'))
    tabs = [t for t in json_get('/json/list') if t.get('type') == 'page']
    print(f'Tab page awal: {len(tabs)}')
    for t in tabs:
        print('   -', (t.get('url') or '')[:70], '|', t.get('id')[:12])

    if tabs:
        print('!! ADA TAB NYANGKUT — ini yang dulu membuat uji salah tab')

    # ── 1. cara Wulan dulu: PUT /json/new?about:blank ──
    t = json.loads(urllib.request.urlopen(urllib.request.Request(
        f'http://127.0.0.1:{PORT}/json/new?about:blank', method='PUT'),
        timeout=20).read())
    print(f'\n[json/new] dapat tab id={t.get("id","")[:12]} url={t.get("url")}')
    ws = websocket.create_connection(t['webSocketDebuggerUrl'], timeout=60)
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
        res = r.get('result', {})
        if 'exceptionDetails' in res:
            return {'__galat': str(res['exceptionDetails'])[:200]}
        return res.get('result', {}).get('value')

    cmd('Page.enable')
    cmd('Runtime.enable')
    print('   url sebelum navigate:', js('location.href'))

    hasil_nav = cmd('Page.navigate', url=BASE + '/buat-data')
    print('   balasan Page.navigate:', json.dumps(hasil_nav.get('result'))[:200])
    for i in range(12):
        time.sleep(0.5)
        u = js('location.href')
        print(f'   +{(i+1)*0.5:.1f}s url:', u)

    print('\n   jumlah .pilih-cara:', js("document.querySelectorAll('.pilih-cara').length"))

    # ── 2. OPSI A: tutup semua tab dulu, BARU buat tab bersih ──
    print('\n═══ OPSI A: kosongkan tab dulu lalu buat tab baru ═══')
    try:
        ws.close()
    except Exception:
        pass
    for tt in json_get('/json/list'):
        if tt.get('type') == 'page':
            try:
                urllib.request.urlopen(
                    f'http://127.0.0.1:{PORT}/json/close/{tt["id"]}',
                    timeout=10).read()
            except Exception:
                pass
    time.sleep(1)
    sisa = [x for x in json_get('/json/list') if x.get('type') == 'page']
    print(f'   tab page sisa setelah dibersihkan: {len(sisa)}')

    t2 = json.loads(urllib.request.urlopen(urllib.request.Request(
        f'http://127.0.0.1:{PORT}/json/new?{BASE}/buat-data', method='PUT'),
        timeout=20).read())
    print(f'   tab baru id={t2.get("id","")[:12]} url={t2.get("url")}')
    ws2 = websocket.create_connection(t2['webSocketDebuggerUrl'], timeout=60)
    n2 = 0

    def cmd2(m, **p):
        nonlocal n2
        n2 += 1
        ws2.send(json.dumps({'id': n2, 'method': m, 'params': p}))
        while True:
            r = json.loads(ws2.recv())
            if r.get('id') == n2:
                return r

    def js2(e):
        r = cmd2('Runtime.evaluate', expression=e, returnByValue=True,
                 awaitPromise=True)
        res = r.get('result', {})
        if 'exceptionDetails' in res:
            return {'__galat': str(res['exceptionDetails'])[:200]}
        return res.get('result', {}).get('value')

    cmd2('Page.enable')
    cmd2('Runtime.enable')
    for i in range(8):
        time.sleep(0.5)
        u = js2('location.href')
        if i in (0, 3, 7):
            print(f'   +{(i+1)*0.5:.1f}s url:', u)
    print('   URL AKHIR   :', js2('location.href'))
    print('   .pilih-cara :', js2("document.querySelectorAll('.pilih-cara').length"))
    print('   judul kartu :', js2("Array.from(document.querySelectorAll('.cara-judul')).map(e=>e.textContent.trim())"))
    print('   #x-slider   :', js2("!!document.getElementById('x-slider')"))
    print('   kartu berantai gaya:', js2("(document.getElementById('cara-berantai-kartu')||{}).className"))

    for w in (ws, ws2):
        try:
            w.close()
        except Exception:
            pass
    return 0


if __name__ == '__main__':
    sys.exit(main())
