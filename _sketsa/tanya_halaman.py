#!/usr/bin/env python3
"""Periksa HALAMAN NYATA dari server uji: HTML apa yang keluar, dan kenapa
JS mati. Satu putaran, tidak menebak.

Pakai: .venv/bin/python _sketsa/tanya_halaman.py
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
PY = DIR / '.venv' / 'bin' / 'python'
CH = '/opt/data/home/.cloakbrowser/chromium-151.0.7922.108.6-pro/chrome'
PORT_SRV = 8122
PORT_CDP = 9343


def main() -> int:
    env = dict(os.environ, PORT=str(PORT_SRV))
    srv = subprocess.Popen(
        [str(PY), '-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1',
         '--port', str(PORT_SRV), '--log-level', 'warning'],
        cwd=str(DIR), env=env,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(40):
        try:
            urllib.request.urlopen(
                f'http://127.0.0.1:{PORT_SRV}/health', timeout=2)
            break
        except Exception:
            time.sleep(0.5)

    subprocess.run(['pkill', '-f', f'remote-debugging-port={PORT_CDP}'],
                   capture_output=True)
    time.sleep(1)
    chr_ = subprocess.Popen(
        [CH, '--headless=new', '--no-sandbox', '--disable-gpu',
         f'--remote-debugging-port={PORT_CDP}', '--remote-allow-origins=*',
         '--window-size=390,900'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    try:
        # ── A. HTML mentah dari server ──────────────────────────────────
        print('══ A. APA YANG DIKIRIM SERVER (sebelum JS) ══')
        r = urllib.request.urlopen(
            f'http://127.0.0.1:{PORT_SRV}/belajar', timeout=10)
        html = r.read().decode()
        print(f'  status={r.status}  panjang={len(html)}')
        for nama, pola in [('KAMUS', 'KAMUS'),
                           ('normalitas', 'normalitas'),
                           ('pintasan-baris', 'pintasan-baris'),
                           ('masalah uji t', 'masalah uji t'),
                           ('kalimatTafsir', 'kalimatTafsir'),
                           ('<script', '<script'),
                           ('</script>', '</script>')]:
            print(f'  {nama:16} : {html.count(pola)}×')
        # di mana letak <script> terakhir & apakah isinya lengkap?
        akhir = html.rfind('</script>')
        print(f'  posisi </script> terakhir: {akhir} dari {len(html)}')
        print(f'  120 karakter terakhir  : {html[-120:]!r}')

        # ── B. Kenapa JS mati? baca KONSOL browser ──────────────────────
        print('\n══ B. BUKA DI CHROME & BACA GALATNYA ══')
        for _ in range(40):
            try:
                urllib.request.urlopen(
                    f'http://127.0.0.1:{PORT_CDP}/json/version', timeout=2)
                break
            except Exception:
                time.sleep(0.5)
        req = urllib.request.Request(
            f'http://127.0.0.1:{PORT_CDP}/json/new', method='PUT')
        tab = json.loads(urllib.request.urlopen(req, timeout=20).read())
        ws = websocket.create_connection(tab['webSocketDebuggerUrl'],
                                         timeout=30)
        n = [0]

        def cdp(method, **params):
            n[0] += 1
            mid = n[0]
            ws.send(json.dumps({'id': mid, 'method': method,
                                'params': params}))
            peristiwa = []
            while True:
                m = json.loads(ws.recv())
                if m.get('id') == mid:
                    return m.get('result', {}), peristiwa
                peristiwa.append(m)

        cdp('Runtime.enable')
        cdp('Log.enable')
        cdp('Page.enable')
        hasil, peristiwa = cdp(
            'Page.navigate', url=f'http://127.0.0.1:{PORT_SRV}/belajar')
        # tunggu & kumpulkan peristiwa konsol
        time.sleep(4)
        ws.settimeout(2)
        galat = []
        try:
            while True:
                m = json.loads(ws.recv())
                peristiwa.append(m)
        except Exception:
            pass
        for m in peristiwa:
            me = m.get('method', '')
            if me == 'Runtime.exceptionThrown':
                d = m['params']['exceptionDetails']
                galat.append('EXCEPTION: ' + str(d.get('text')) + ' | '
                             + str(d.get('exception', {}).get('description'))[:500])
            if me == 'Log.entryAdded':
                e = m['params']['entry']
                if e.get('level') in ('error', 'warning'):
                    galat.append(f"LOG[{e.get('level')}]: {e.get('text')[:500]}")
            if me == 'Runtime.consoleAPICalled':
                t = m['params']['type']
                if t in ('error', 'warning'):
                    args = [str(a.get('value') or a.get('description'))[:300]
                            for a in m['params'].get('args', [])]
                    galat.append(f'CONSOLE[{t}]: ' + ' '.join(args))
        print(f'  {len(galat)} galat ditemukan:')
        for g in galat[:15]:
            print('   •', g)

        # ── C. Keadaan dokumen nyata ───────────────────────────────────
        print('\n══ C. KEADAAN DOKUMEN NYATA ══')
        ws.settimeout(30)
        for nama, expr in [
            ('title', 'document.title'),
            ('jumlah <script>', 'document.querySelectorAll("script").length'),
            ('typeof KAMUS', 'typeof KAMUS'),
            ('typeof pilih', 'typeof pilih'),
            ('jumlah .kamus-tombol',
             'document.querySelectorAll(".kamus-tombol").length'),
            ('ada #slider', '!!document.getElementById("slider")'),
            ('ada #judul', '!!document.getElementById("judul")'),
            ('ada #pintasan-baris',
             '!!document.getElementById("pintasan-baris")'),
            ('teks 150 char', 'document.body.innerText.slice(0,150)'),
        ]:
            _, _ = None, None
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
                        val = '❌ ' + str(rr['exceptionDetails'].get('exception', {}).get('description'))[:120]
                    else:
                        val = rr.get('result', {}).get('value')
                    print(f'  {nama:22} : {val}')
                    break
    finally:
        srv.terminate()
        chr_.terminate()
        try:
            srv.wait(timeout=5)
        except Exception:
            srv.kill()
    return 0


if __name__ == '__main__':
    sys.exit(main())
