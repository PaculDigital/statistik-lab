"""CETAK tombol & panel asli di /buat-data?model=<varian> — jangan tebak label."""
from __future__ import annotations

import json
import subprocess
import urllib.request
import time

import websocket  # type: ignore


def ip() -> str:
    r = subprocess.run(
        ['docker', 'inspect', '-f',
         '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}',
         'simulasi-olah-data'], capture_output=True, text=True, timeout=60)
    return r.stdout.strip()


def main() -> int:
    base = f'http://{ip()}:8000'
    req = urllib.request.Request(
        'http://127.0.0.1:9333/json/new?about:blank', method='PUT')
    with urllib.request.urlopen(req, timeout=20) as r:
        info = json.loads(r.read().decode())
    ws = websocket.create_connection(info['webSocketDebuggerUrl'], timeout=90)
    n = 0

    def kirim(method: str, **p) -> dict:
        nonlocal n
        n += 1
        ws.send(json.dumps({'id': n, 'method': method, 'params': p}))
        while True:
            m = json.loads(ws.recv())
            if m.get('id') == n:
                return m

    kirim('Page.enable')
    kirim('Runtime.enable')

    def buka(url: str) -> None:
        kirim('Page.navigate', url=url)
        for _ in range(80):
            time.sleep(0.4)
            r = kirim('Runtime.evaluate', expression='document.readyState',
                      returnByValue=True)
            if r.get('result', {}).get('result', {}).get('value') == 'complete':
                return

    def js(expr: str):
        r = kirim('Runtime.evaluate', expression=expr, returnByValue=True,
                  awaitPromise=True)
        return r.get('result', {}).get('result', {}).get('value')

    for v in ['mediasi-paralel', 'gabungan']:
        buka(f'{base}/buat-data?model={v}')
        print(f'\n===== {v} =====')
        print(js("""JSON.stringify({
          semuaTombol: Array.from(document.querySelectorAll('button'))
              .map(b => b.innerText.trim()).filter(t => t).slice(0, 14),
          panelTampak: Array.from(document.querySelectorAll('[id^=panel]'))
              .map(e => ({id: e.id, tampak: !e.hidden && e.offsetHeight > 0})),
          h1: (document.querySelector('h1')||{}).innerText || '',
          catatan: (Array.from(document.querySelectorAll('p,.catatan'))
              .map(e=>e.innerText).filter(t=>/segera|siap|belum/i.test(t))).slice(0,3)
        }, null, 1)"""))

    ws.close()
    urllib.request.urlopen(
        'http://127.0.0.1:9333/json/close/' + info['id'], timeout=10).read()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
