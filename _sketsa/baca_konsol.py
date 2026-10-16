#!/usr/bin/env python3
"""BACA KONSOL BROWSER sungguhan: GALAT APA yang mematikan skrip belajar.html?

Pelajaran (memori): HTTP 403 misterius → BACA LOG SERVER, jangan menebak dari
sisi klien. Di sini kita balik: skrip tidak jalan → BACA KONSOL browser
lewat CDP (Runtime.exceptionThrown + Log.entryAdded + consoleAPICalled),
BUKAN menebak dari luar.

Pakai: .venv/bin/python _sketsa/baca_konsol.py
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

DIR = Path(__file__).resolve().parent.parent
CH = '/opt/data/home/.cloakbrowser/chromium-151.0.7922.108.6-pro/chrome'
P_SRV, P_CDP = 8128, 9345


def main() -> int:
    env = dict(os.environ, PORT=str(P_SRV))
    srv = subprocess.Popen(
        [str(DIR / '.venv' / 'bin' / 'python'), '-m', 'uvicorn',
         'app.main:app', '--host', '127.0.0.1', '--port', str(P_SRV),
         '--log-level', 'warning'],
        cwd=str(DIR), env=env,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    base = f'http://127.0.0.1:{P_SRV}'
    for _ in range(40):
        try:
            urllib.request.urlopen(base + '/health', timeout=2)
            break
        except Exception:
            time.sleep(0.5)

    subprocess.run(['pkill', '-f', f'remote-debugging-port={P_CDP}'],
                   capture_output=True)
    time.sleep(1)
    chr_ = subprocess.Popen(
        [CH, '--headless=new', '--no-sandbox', '--disable-gpu',
         f'--remote-debugging-port={P_CDP}', '--remote-allow-origins=*',
         '--window-size=390,900'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    try:
        for _ in range(40):
            try:
                urllib.request.urlopen(
                    f'http://127.0.0.1:{P_CDP}/json/version', timeout=2)
                break
            except Exception:
                time.sleep(0.5)
        req = urllib.request.Request(f'http://127.0.0.1:{P_CDP}/json/new',
                                     method='PUT')
        tab = json.loads(urllib.request.urlopen(req, timeout=20).read())
        ws = websocket.create_connection(tab['webSocketDebuggerUrl'],
                                         timeout=30)
        n = [0]

        def perintah(method, **params):
            n[0] += 1
            mid = n[0]
            ws.send(json.dumps({'id': mid, 'method': method, 'params': params}))
            simpan = []
            while True:
                m = json.loads(ws.recv())
                if m.get('id') == mid:
                    return m.get('result', {}), simpan
                simpan.append(m)

        perintah('Runtime.enable')
        perintah('Log.enable')
        perintah('Page.enable')
        # sembunyikan gangguan jaringan biar konsol bersih
        perintah('Network.enable')
        perintah('Page.navigate', url=base + '/belajar')
        time.sleep(5)
        # kuras semua peristiwa yang masih mengantre
        ws.settimeout(2)
        peristiwa = []
        try:
            while True:
                peristiwa.append(json.loads(ws.recv()))
        except Exception:
            pass
        ws.settimeout(30)

        print('══ PERISTIWA KONSOL (semua) ══')
        for m in peristiwa:
            me = m.get('method', '')
            p = m.get('params', {})
            if me == 'Runtime.exceptionThrown':
                d = p['exceptionDetails']
                print(f'  🔴 EXCEPTION  : {d.get("text")}')
                print(f'     baris {d.get("lineNumber")} kolom '
                      f'{d.get("columnNumber")}')
                print(f'     url   {d.get("url")}')
                print(f'     detail: {d.get("exception", {}).get("description", "")[:600]}')
            elif me == 'Log.entryAdded':
                e = p['entry']
                if e.get('level') in ('error', 'warning'):
                    print(f'  🟠 LOG[{e.get("level")}]: {e.get("text")[:400]}')
                    if e.get('url'):
                        print(f'     url: {e["url"]}')
            elif me == 'Runtime.consoleAPICalled':
                t = p.get('type')
                args = ' '.join(
                    str(a.get('value') or a.get('description'))[:200]
                    for a in p.get('args', []))
                print(f'  🔵 CONSOLE[{t}]: {args[:400]}')
            elif me == 'Network.loadingFailed':
                print(f'  ⚫ GAGAL MUAT: {p.get("errorText")} '
                      f'(type={p.get("type")})')
            elif me == 'Network.responseReceived':
                r = p.get('response', {})
                if r.get('status', 200) >= 400:
                    print(f'  ⚫ HTTP {r.get("status")} {r.get("url")}')
        print()

        # ── Berapa <script> yang benar-benar DIEKSEKUSI? ────────────────
        def js(expr):
            n[0] += 1
            mid = n[0]
            ws.send(json.dumps({'id': mid, 'method': 'Runtime.evaluate',
                                'params': {'expression': expr,
                                           'returnByValue': True}}))
            while True:
                m = json.loads(ws.recv())
                if m.get('id') == mid:
                    rr = m.get('result', {})
                    if 'exceptionDetails' in rr:
                        return '❌ ' + str(rr['exceptionDetails'].get(
                            'exception', {}).get('description'))[:200]
                    return rr.get('result', {}).get('value')

        print('══ SCRIPT DI DOKUMEN ══')
        print(js("""(() => {
          const sk = [...document.querySelectorAll('script')];
          return JSON.stringify(sk.map((s, i) => ({
            i,
            src: s.src ? s.src.split('/').pop() : '(inline)',
            panjang: (s.textContent || '').length,
            potong: (s.textContent || '').slice(0, 60).replace(/\\s+/g, ' ')
          })), null, 1);
        })()"""))
        print()
        print('typeof WulanCek :', js("typeof KAMUS"))
        print('elemen script ke-3 isi awal:', js(
            "document.querySelectorAll('script')[2]?.textContent.slice(0,80)"))
    finally:
        srv.terminate()
        chr_.terminate()
    return 0


if __name__ == '__main__':
    sys.exit(main())
