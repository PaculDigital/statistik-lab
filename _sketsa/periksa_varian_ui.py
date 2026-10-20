"""Apakah 9 varian jalur TERSAMBUNG di UI? Ukur halaman sungguhan via CDP.

Bukan grep: buka ?model=<varian>, cari panel form, tombol, dan apakah
halaman mengalihkan ke /kuantitatif.
"""
from __future__ import annotations

import json
import subprocess
import time
import urllib.request

import websocket  # type: ignore

VARIAN = [
    'mediasi-paralel', 'mediasi-berjenjang', 'moderasi-jalur-a',
    'moderasi-jalur-b', 'moderasi-keduanya', 'moderasi-dual',
    'moderasi-3jalur', 'mediasi-campuran', 'gabungan',
]


def ip() -> str:
    r = subprocess.run(
        ['docker', 'inspect', '-f',
         '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}',
         'simulasi-olah-data'], capture_output=True, text=True, timeout=60)
    return r.stdout.strip()


class Tab:
    def __init__(self) -> None:
        req = urllib.request.Request(
            'http://127.0.0.1:9333/json/new?about:blank', method='PUT')
        with urllib.request.urlopen(req, timeout=20) as r:
            self.info = json.loads(r.read().decode())
        self.ws = websocket.create_connection(
            self.info['webSocketDebuggerUrl'], timeout=90)
        self.i = 0
        self.kirim('Page.enable')
        self.kirim('Runtime.enable')

    def kirim(self, method: str, **params) -> dict:
        self.i += 1
        self.ws.send(json.dumps({'id': self.i, 'method': method,
                                 'params': params}))
        while True:
            m = json.loads(self.ws.recv())
            if m.get('id') == self.i:
                return m

    def buka(self, url: str) -> None:
        self.kirim('Page.navigate', url=url)
        for _ in range(80):
            time.sleep(0.4)
            r = self.kirim('Runtime.evaluate',
                           expression='document.readyState',
                           returnByValue=True)
            if r.get('result', {}).get('result', {}).get('value') == 'complete':
                return

    def js(self, expr: str):
        r = self.kirim('Runtime.evaluate', expression=expr,
                       returnByValue=True, awaitPromise=True)
        return r.get('result', {}).get('result', {}).get('value')

    def tutup(self) -> None:
        try:
            self.ws.close()
        finally:
            urllib.request.urlopen(
                'http://127.0.0.1:9333/json/close/' + self.info['id'],
                timeout=10).read()


def main() -> int:
    base = f'http://{ip()}:8000'
    print(f'BASE = {base}\n')
    tab = Tab()
    hidup, mati = [], []
    try:
        for v in VARIAN:
            tab.buka(f'{base}/buat-data?model={v}')
            d = tab.js("""JSON.stringify({
              url: location.pathname + location.search,
              judul: (document.querySelector('h1')||{}).innerText || '',
              adaTombolBangun: !!Array.from(document.querySelectorAll('button'))
                    .find(b=>/bangun|buat data|generate/i.test(b.innerText)),
              adaBidangJalur: !!document.querySelector(
                    '[id*=jalur],[class*=jalur],[id*=panel],[class*=panel]'),
              segera: /sedang disiapkan|belum siap/i.test(document.body.innerText),
              jumlahInput: document.querySelectorAll('input[type=number],input[type=range]').length,
              naskah: document.body.innerText.slice(0,90).replace(/\\n/g,' ')
            })""")
            try:
                o = json.loads(d)
            except Exception:  # noqa: BLE001
                o = {}
            nyata = (not o.get('segera')) and o.get('adaTombolBangun')
            (hidup if nyata else mati).append(v)
            print(f'  {v:22} url={o.get("url","?"):38} '
                  f'segera={o.get("segera")} bangun={o.get("adaTombolBangun")} '
                  f'input={o.get("jumlahInput")}')
            print(f'{"":26}naskah: {o.get("naskah","")[:80]}')
    finally:
        tab.tutup()

    print(f'\nUI TERSAMBUNG: {len(hidup)}/9')
    if mati:
        print(f'UI MASIH "SEGERA": {mati}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
