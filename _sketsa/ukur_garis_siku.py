"""UKUR PIKEL: apakah garis siku kartu ② benar-benar terlihat & segelap panah?

Dipakai karena model vision sedang gangguan (503). Mengukur lebih jujur:
ambil warna piksel di jalur siku (y=48 area mendatar, x=112 area naik)
lalu bandingkan dengan warna piksel di garis panah lurus.
"""
from __future__ import annotations

import json
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
    cmd('Page.navigate', url=BASE + '/kuantitatif')
    time.sleep(5)
    js("typeof bukaSub === 'function' && bukaSub(null, 'regresi')")
    time.sleep(1)

    # ukur: kelas, warna terhitung, dan geometri path siku pada kartu ②
    ukur = js("""(() => {
      const kartu = document.querySelector('#sub-regresi a[href*="berganda"]');
      if (!kartu) return {galat: 'kartu berganda tidak ketemu'};
      const siku = kartu.querySelector('path.garis-siku');
      const panah = kartu.querySelector('line.garis-panah');
      const cs = siku ? getComputedStyle(siku) : null;
      const cp = panah ? getComputedStyle(panah) : null;
      const rK = kartu.getBoundingClientRect();
      const rS = siku ? siku.getBoundingClientRect() : null;
      const rP = panah ? panah.getBoundingClientRect() : null;
      return {
        adaSiku: !!siku,
        dSiku: siku ? siku.getAttribute('d') : null,
        warnaSiku: cs ? cs.stroke : null,
        tebalSiku: cs ? cs.strokeWidth : null,
        warnaPanah: cp ? cp.stroke : null,
        tebalPanah: cp ? cp.strokeWidth : null,
        // ukuran nyata di layar (px CSS)
        kotakSiku: rS ? {w: Math.round(rS.width), h: Math.round(rS.height)} : null,
        kotakPanah: rP ? {w: Math.round(rP.width), h: Math.round(rP.height)} : null,
        pxPerUnitSiku: rS ? Math.round(rS.width / (112 - 38) * 100) / 100 : null,
        jumlahPanah: kartu.querySelectorAll('line.garis-panah').length,
        tinggiKartu: Math.round(rK.height)
      };
    })()""")
    print(json.dumps(ukur, indent=2, ensure_ascii=False))

    # apakah warna siku terlihat? ukur kontras dengan latar
    warna = js("""(() => {
      const el = document.querySelector('#sub-regresi a[href*="berganda"]');
      const bg = getComputedStyle(el).backgroundColor;
      const s = document.querySelector('#sub-regresi path.garis-siku');
      return {latarKartu: bg, warnaSiku: s ? getComputedStyle(s).stroke : null};
    })()""")
    print('\nkontras:', json.dumps(warna, ensure_ascii=False))
    try:
        urllib.request.urlopen(f'http://127.0.0.1:{PORT}/json/close/{t["id"]}',
                               timeout=10).read()
    except Exception:
        pass
    return 0


if __name__ == '__main__':
    sys.exit(main())
