"""BUKTI 9 varian jalur benar-benar BERFUNGSI lewat UI: klik 'Buatkan data'.

Bukan grep, bukan cek atribut. Ukur: hasil muncul di halaman + tabel/angka.
Sesuai aturan: ukur PERILAKU, dan buktikan bisa GAGAL.
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
            self.info['webSocketDebuggerUrl'], timeout=120)
        self.i = 0
        self.kirim('Page.enable')
        self.kirim('Runtime.enable')

    def kirim(self, method: str, **p) -> dict:
        self.i += 1
        self.ws.send(json.dumps({'id': self.i, 'method': method, 'params': p}))
        while True:
            m = json.loads(self.ws.recv())
            if m.get('id') == self.i:
                return m

    def buka(self, url: str) -> None:
        self.kirim('Page.navigate', url=url)
        for _ in range(80):
            time.sleep(0.4)
            r = self.kirim('Runtime.evaluate', expression='document.readyState',
                           returnByValue=True)
            if r.get('result', {}).get('result', {}).get('value') == 'complete':
                return

    def js(self, expr: str):
        r = self.kirim('Runtime.evaluate', expression=expr, returnByValue=True,
                       awaitPromise=True)
        hasil = r.get('result', {}).get('result', {})
        if hasil.get('subtype') == 'error':
            return 'JSERR: ' + str(hasil.get('description'))[:160]
        return hasil.get('value')

    def tutup(self) -> None:
        try:
            self.ws.close()
        finally:
            urllib.request.urlopen(
                'http://127.0.0.1:9333/json/close/' + self.info['id'],
                timeout=10).read()


def main() -> int:
    base = f'http://{ip()}:8000'
    tab = Tab()
    lulus, gagal = [], []
    try:
        for v in VARIAN:
            tab.buka(f'{base}/buat-data?model={v}')
            # klik tombol nyata lewat JS (paling andal, tak tergantung koordinat)
            klik = tab.js("""(() => {
              const b = Array.from(document.querySelectorAll('button'))
                .find(x => /Buatkan data/i.test(x.innerText));
              if (!b) return 'TOMBOL TIDAK ADA';
              b.click(); return 'DIKLIK';
            })()""")
            # tunggu hasil muncul (maks 40 dtk)
            hasil = None
            for _ in range(40):
                time.sleep(1)
                hasil = tab.js("""(() => {
                  const t = document.body.innerText;
                  const adaTabel = !!document.querySelector('table');
                  const adaUnduh = Array.from(document.querySelectorAll('a,button'))
                      .some(e => /unduh|csv|xlsx|excel/i.test(e.innerText));
                  const galat = /Gagal membuat|terputus|error/i.test(t);
                  const sebut = (t.match(/galat maks[^\\n]{0,30}/i)||[''])[0];
                  return JSON.stringify({adaTabel, adaUnduh, galat, sebut,
                    panjang: t.length});
                })()""")
                try:
                    o = json.loads(hasil or '{}')
                except Exception:  # noqa: BLE001
                    o = {}
                if o.get('adaTabel') and o.get('adaUnduh'):
                    break
                if o.get('galat'):
                    break

            try:
                o = json.loads(hasil or '{}')
            except Exception:  # noqa: BLE001
                o = {}
            ok = o.get('adaTabel') and o.get('adaUnduh') and not o.get('galat')
            (lulus if ok else gagal).append(v)
            print(f'  {v:22} klik={klik:16} tabel={o.get("adaTabel")} '
                  f'unduh={o.get("adaUnduh")} galat={o.get("galat")} '
                  f'| {o.get("sebut","")[:26]}')
    finally:
        tab.tutup()

    print(f'\nHASIL: {len(lulus)} LULUS / {len(gagal)} GAGAL  (dari {len(VARIAN)})')
    if gagal:
        print(f'  GAGAL: {gagal}')
    return 0 if not gagal else 1


if __name__ == '__main__':
    raise SystemExit(main())
