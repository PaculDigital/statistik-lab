#!/usr/bin/env python3
"""UJI SINTAKS skrip /belajar: apakah skrip 50.177 karakter itu BISA di-parse?

Hipotesis (belum terbukti): skrip ada di DOM tapi tidak jalan = SYNTAX ERROR
di suatu tempat. SyntaxError mematikan SELURUH skrip (bukan cuma satu bagian),
dan browser hanya melaporkannya kalau kita memasang penangkap SEBELUM skrip
jalan. Di sini kita pakai CDP: ambil isi skrip, lalu `new Function(isi)` —
kalau SyntaxError, kita cetak baris & kolomnya.

Pakai: .venv/bin/python _sketsa/uji_sintaks.py
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
P_SRV, P_CDP = 8129, 9346


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
                                         timeout=60)
        n = [0]

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
                            'exception', {}).get('description'))[:300]
                    return rr.get('result', {}).get('value')

        js('1')
        ws.send(json.dumps({'id': 999, 'method': 'Page.enable', 'params': {}}))
        ws.send(json.dumps({'id': 1000, 'method': 'Page.navigate',
                            'params': {'url': base + '/belajar'}}))
        time.sleep(4)

        print('══ UJI SINTAKS TIAP SKRIP (new Function) ══')
        hasil = js("""(() => {
          const sk = [...document.querySelectorAll('script')];
          const lap = [];
          sk.forEach((s, i) => {
            if (s.src) { lap.push({i, jenis: 'src', src: s.src}); return; }
            const kode = s.textContent || '';
            const nama = 'SkripInline' + i;
            try {
              new Function(kode);
              lap.push({i, jenis: 'inline', panjang: kode.length, hasil: 'OK'});
            } catch (e) {
              // cari baris & kolom dari SyntaxError
              lap.push({i, jenis: 'inline', panjang: kode.length,
                        hasil: e.name + ': ' + e.message,
                        baris: e.lineNumber, kolom: e.columnNumber});
            }
          });
          return JSON.stringify(lap, null, 1);
        })()""")
        print(hasil)

        print('\n══ BARIS YANG DITUDUH (kalau ada SyntaxError) ══')
        print(js("""(() => {
          const sk = [...document.querySelectorAll('script')]
                       .filter(s => !s.src);
          const lap = [];
          sk.forEach((s, i) => {
            const kode = s.textContent || '';
            try { new Function(kode); }
            catch (e) {
              // cari baris mencurigakan: yang memuat backslash atau tag
              const baris = kode.split('\\n');
              const curiga = [];
              baris.forEach((b, no) => {
                if (/<\\/[a-zA-Z]/.test(b)) {
                  curiga.push({no: no + 1, isi: b.trim().slice(0, 140)});
                }
              });
              lap.push({skrip: i, pesan: e.message,
                        curigaTagPenutup: curiga.slice(0, 20)});
            }
          });
          return JSON.stringify(lap, null, 1);
        })()"""))

        print('\n══ APAKAH SKRIP DIJALANKAN? (cek variabel global) ══')
        for nama in ['KAMUS', 'pilih', 'gambar', 'kalimatTafsir',
                     'pintasanPasang', 'ujitLot', 'ambGambar', 'UJI_T']:
            print(f'  {nama:16} = {js("typeof " + nama)}')

        print('\n══ BARIS PERTAMA SKRIP KE-3 (cek awal blok) ══')
        print(js("""(() => {
          const s = [...document.querySelectorAll('script')]
                     .filter(x => !x.src)[1];
          return (s?.textContent || '').split('\\n').slice(0, 3).join('\\n');
        })()"""))
    finally:
        srv.terminate()
        chr_.terminate()
    return 0


if __name__ == '__main__':
    sys.exit(main())
