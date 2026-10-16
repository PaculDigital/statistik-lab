"""DIAGNOSA: kenapa cek 'kolom SS/df/MS' gagal — cacat APP atau cacat UJI?

Ukur isi halaman apa adanya, jangan menebak.
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


def server_hidup():
    try:
        return urllib.request.urlopen(
            f'http://127.0.0.1:{PORT_UJI}/health', timeout=3).status == 200
    except Exception:
        return False


def siapkan():
    if server_hidup():
        return True
    os.environ['PORT'] = str(PORT_UJI)
    subprocess.Popen([str(PY), '-m', 'uvicorn', 'app.main:app',
                      '--host', '127.0.0.1', '--port', str(PORT_UJI),
                      '--log-level', 'warning'],
                     cwd=str(DIR), stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL)
    for _ in range(60):
        if server_hidup():
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
            return {'__galat': str(res['exceptionDetails'])[:300]}
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
        tab.cmd('Page.navigate', url=BASE + '/buat-data?model=berganda')
        time.sleep(4)
        out = tab.js("""(async () => {
          const r = await fetch('/api/buat-data', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({n:200, x:3, beta:[0.3,0.25,0.2],
              skala:5, alpha:0.85, mode:'presisi', cara:'berganda',
              kunci:'diag', nama_x:['Harga','Promosi','Layanan']})
          });
          const d = await r.json();
          tampilkanHasil(d);
          const kotak = document.getElementById('hasil');
          // cari SEMUA tabel di dalam hasil
          const tabel = Array.from(kotak.querySelectorAll('table'));
          const info = tabel.map(t => ({
            header: Array.from(t.querySelectorAll('th')).map(h => h.innerText.trim()),
            baris: t.querySelectorAll('tbody tr').length,
            baris1: Array.from(t.querySelectorAll('tbody tr')[0]?.querySelectorAll('td')||[])
                     .map(c => c.innerText.trim())
          }));
          const teks = kotak.innerText || '';
          return {jumlahTabel: tabel.length, info: info,
                  adaKataSS: teks.includes('SS'),
                  adaKataMS: teks.includes('MS'),
                  adaKatadf: teks.includes('df'),
                  panjangTeks: teks.length,
                  cariSS: teks.indexOf('SS'),
                  cariMS: teks.indexOf('MS'),
                  cariANOVA: teks.toUpperCase().indexOf('ANOVA'),
                  ekor: teks.slice(-600)};
        })()""")
        print(json.dumps(out, indent=2, ensure_ascii=False)[:3000])
    finally:
        tab.tutup()
    return 0


if __name__ == '__main__':
    sys.exit(main())
