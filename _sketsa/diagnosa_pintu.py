"""DIAGNOSA: kenapa uji pintu dapat kartu [] — cacat APP atau cacat UJI?"""
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


class Tab:
    def __init__(self):
        t = json.loads(urllib.request.urlopen(urllib.request.Request(
            f'http://127.0.0.1:{PORT}/json/new?about:blank', method='PUT'),
            timeout=20).read())
        self.tab_id = t['id']
        self.ws = websocket.create_connection(t['webSocketDebuggerUrl'],
                                              timeout=90)
        self.n = 0

    def cmd(self, m, **p):
        self.n += 1
        self.ws.send(json.dumps({'id': self.n, 'method': m, 'params': p}))
        while True:
            r = json.loads(self.ws.recv())
            if r.get('id') == self.n:
                return r

    def js(self, e):
        r = self.cmd('Runtime.evaluate', expression=e, returnByValue=True,
                     awaitPromise=True)
        res = r.get('result', {})
        if 'exceptionDetails' in res:
            return {'__galat': str(res['exceptionDetails'])[:400]}
        return res.get('result', {}).get('value')

    def tutup(self):
        try:
            urllib.request.urlopen(urllib.request.Request(
                f'http://127.0.0.1:{PORT}/json/close/{self.tab_id}'),
                timeout=10).read()
        except Exception:
            pass


def main():
    if not siapkan():
        print('server gagal')
        return 1
    tab = Tab()
    try:
        tab.cmd('Page.enable')
        tab.cmd('Runtime.enable')
        tab.cmd('Page.navigate', url=BASE + '/buat-data')
        time.sleep(5)
        out = tab.js("""(() => {
          const semua = document.querySelectorAll('.pilih-cara');
          const kisi = document.getElementById('cara-kisi');
          const rb = document.querySelectorAll('input[name="cara"]');
          return {
            url: location.href,
            judul: document.title,
            panjangHTML: document.documentElement.innerHTML.length,
            jumlahPilihCara: semua.length,
            kisiAda: !!kisi,
            kisiAnak: kisi ? kisi.children.length : -1,
            jumlahRadio: rb.length,
            radioNilai: Array.from(rb).map(r => r.value),
            judulKartu: Array.from(document.querySelectorAll('.cara-judul'))
                          .map(e => e.textContent.trim()),
            sliderAda: !!document.querySelector('input[type=range]'),
            sliderId: Array.from(document.querySelectorAll('input[type=range]'))
                          .map(s => s.id),
            galat: window.__galat || null
          };
        })()""")
        print(json.dumps(out, indent=2, ensure_ascii=False)[:2500])
    finally:
        tab.tutup()
    return 0


if __name__ == '__main__':
    sys.exit(main())
