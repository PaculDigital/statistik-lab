#!/usr/bin/env python3
"""KENAPA klik tombol kamus tidak berefek? Periksa dengan MATA yang jujur.

Tersangka yang diperiksa satu-satu:
  A. Apakah listener benar-benar menempel di tombol?
  B. Apakah pilih() bisa dipanggil (typeof)?
  C. Apakah #kartu-ujit ada & tidak melindungi (menutupi) tombol?
  D. Apakah .kamus-tombol ada DI DALAM #tab-1, dan #tab-1 sedang aktif?
  E. Geser slider langsung — apakah gambar() jalan?

Pakai: .venv/bin/python _sketsa/tanya_klik.py
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
P_SRV, P_CDP = 8127, 9344


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

        def js(expr):
            n[0] += 1
            mid = n[0]
            ws.send(json.dumps({'id': mid, 'method': 'Runtime.evaluate',
                                'params': {'expression': expr,
                                           'returnByValue': True,
                                           'awaitPromise': True}}))
            while True:
                m = json.loads(ws.recv())
                if m.get('id') == mid:
                    rr = m.get('result', {})
                    if 'exceptionDetails' in rr:
                        return '❌ ' + str(rr['exceptionDetails'].get(
                            'exception', {}).get('description'))[:200]
                    return rr.get('result', {}).get('value')

        js('1')
        ws.send(json.dumps({'id': 999, 'method': 'Page.enable', 'params': {}}))
        ws.send(json.dumps({'id': 1000, 'method': 'Page.navigate',
                            'params': {'url': base + '/belajar'}}))
        time.sleep(4)

        print('══ A. LISTENER MENEMPEL? ══')
        print('  typeof pilih        :', js("typeof pilih"))
        print('  typeof gambar       :', js("typeof gambar"))
        print('  typeof kalimatTafsir:', js("typeof kalimatTafsir"))
        print('  typeof pintasanPasang:', js("typeof pintasanPasang"))
        print('  KAMUS               :', js("typeof KAMUS"))
        print('  jumlah kamus-tombol :', js(
            "document.querySelectorAll('.kamus-tombol').length"))

        print('\n══ B. TOMBOL ADA DI TAB YANG TERLIHAT? ══')
        print(js("""(() => {
          const b = [...document.querySelectorAll('.kamus-tombol')]
                     .find(x => x.dataset.k === 'normalitas');
          if (!b) return 'tombol normalitas TIDAK ADA';
          const r = b.getBoundingClientRect();
          const cs = getComputedStyle(b);
          const induk = b.closest('[id^=tab-]');
          return JSON.stringify({
            induk: induk ? induk.id : '(bukan di tab)',
            indukTersembunyi: induk ? induk.hidden : null,
            rect: [Math.round(r.x), Math.round(r.y),
                   Math.round(r.width), Math.round(r.height)],
            display: cs.display, visibility: cs.visibility,
            pointerEvents: cs.pointerEvents,
            adaDiTitikItu: document.elementFromPoint(
              Math.round(r.x + r.width/2), Math.round(r.y + r.height/2))
              ?.className || '(kosong)'
          });
        })()"""))

        print('\n══ C. SLIDER LANGSUNG — apakah gambar() jalan? ══')
        print(js("""(() => {
          const s = document.getElementById('slider');
          s.value = 70;
          s.dispatchEvent(new Event('input', {bubbles: true}));
          return JSON.stringify({
            angka: document.getElementById('angka').textContent,
            pita: document.getElementById('pita-hasil').textContent,
            titik: document.getElementById('grafik').querySelectorAll('circle').length,
            pesan: document.getElementById('pesan-isi').innerText.slice(0, 60)
          });
        })()"""))

        print('\n══ D. PANGGIL pilih(\'normalitas\') LANGSUNG ══')
        print(js("""(() => {
          try { pilih('normalitas'); } catch (e) { return 'GALAT: ' + e.message }
          const s = document.getElementById('slider');
          return JSON.stringify({
            judul: document.getElementById('judul').textContent,
            min: s.min, max: s.max, nilai: s.value,
            batang: document.getElementById('grafik').querySelectorAll('rect').length,
            pita: document.getElementById('pita-hasil').textContent
          });
        })()"""))

        print('\n══ E. KLIK SUNGGUHAN (dispatch MouseEvent) ══')
        print(js("""(() => {
          const b = [...document.querySelectorAll('.kamus-tombol')]
                     .find(x => x.dataset.k === 'vif');
          b.dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}));
          return JSON.stringify({
            judul: document.getElementById('judul').textContent,
            aktif: b.classList.contains('aktif')
          });
        })()"""))

        print('\n══ F. GALAT YANG TERTANGKAP ══')
        print('  ', js("(window.__galatJs||[]).join(' | ') || '(tidak ada)'"))
    finally:
        srv.terminate()
        chr_.terminate()
    return 0


if __name__ == '__main__':
    sys.exit(main())
