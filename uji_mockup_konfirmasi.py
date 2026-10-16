#!/usr/bin/env python3

════════════════════════════════════════════════════════════════════════════
⚠️ PENINGGALAN — BUKAN PENJAGA MESIN PRODUKSI (ditandai 21Sep26)
   Modul/objek yang diuji : tampilan mockup lama
   Sebab                  : Mockup tampilan lama — bukan jalur produksi.
   ⇒ Kalau uji ini GAGAL, JANGAN simpulkan mesin produksi rusak.
     Lihat AUDIT_UJI_LUAR_GERBANG_21SEP2026.md (akar: PINTU UKUR SALAH).
   ⇒ Uji yang MENJAGA produksi ada di gerbang_uji.py (jalankan: bash gerbang_uji.sh).
════════════════════════════════════════════════════════════════════════════
"""Uji SUNGGUHAN mockup konfirmasi model: klik tab, klik tiap contoh, periksa tabel.

KENAPA lewat CDP: `chrome --screenshot` tidak menunggu skrip JS selesai (terukur:
7 keadaan hasil identik). CDP bisa KLIK lalu MEMERIKSA isi halaman lewat JS.
"""
from __future__ import annotations

import base64
import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import websocket

CHROME = '/opt/data/home/.cloakbrowser/chromium-146.0.7680.177.5/chrome'
PORT = 9341
HAL = Path('/opt/data/services/statistik-lab/_arsip/mockup_konfirmasi_model.html')

KIRIM_JS = """
window.__GALAT_JS = window.__GALAT_JS || [];
window.onerror = function(m,s,l){ window.__GALAT_JS.push(m + ' @' + l); };
"""


class Sisi:
    def __init__(self, ws):
        self.ws, self.n = ws, 0

    def kirim(self, metode, **kw):
        self.n += 1
        self.ws.send(json.dumps({'id': self.n, 'method': metode, 'params': kw}))
        while True:
            d = json.loads(self.ws.recv())
            if d.get('id') == self.n:
                if 'error' in d:
                    raise RuntimeError(f'{metode}: {d["error"]}')
                return d.get('result', {})

    def js(self, expr):
        r = self.kirim('Runtime.evaluate', expression=expr,
                       returnByValue=True, awaitPromise=True)
        return r.get('result', {}).get('value')


def main() -> int:
    proses = subprocess.Popen([
        CHROME, '--headless=new', '--disable-gpu', '--no-sandbox',
        '--hide-scrollbars', '--remote-allow-origins=*',
        f'--remote-debugging-port={PORT}', '--window-size=1200,900',
        'about:blank',
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    url_ws = None
    for _ in range(60):
        try:
            with urllib.request.urlopen(f'http://127.0.0.1:{PORT}/json/list',
                                        timeout=2) as r:
                for t in json.load(r):
                    if t.get('type') == 'page':
                        url_ws = t['webSocketDebuggerUrl']
                        break
            if url_ws:
                break
        except Exception:                                  # noqa: BLE001
            pass
        time.sleep(0.5)
    if not url_ws:
        print('GAGAL: Chrome debug tidak siap')
        proses.kill()
        return 1

    ws = websocket.create_connection(url_ws, timeout=30)
    s = Sisi(ws)
    s.kirim('Page.enable')
    s.kirim('Runtime.enable')
    s.kirim('Emulation.setDeviceMetricsOverride', width=1100, height=900,
            deviceScaleFactor=1, mobile=False)
    s.kirim('Page.addScriptToEvaluateOnNewDocument', source=KIRIM_JS)
    s.kirim('Page.navigate', url=f'file://{HAL}')
    time.sleep(1.4)

    gagal = 0

    # ── 1. Keadaan awal: tab & panel ──
    awal = s.js("""(function(){
      var t = document.querySelectorAll('.tab').length;
      var p = document.querySelectorAll('.panel').length;
      var aktif = document.querySelectorAll('.panel.aktif').length;
      var aktifId = document.querySelector('.panel.aktif').id;
      return [t, p, aktif, aktifId].join('|');
    })()""")
    print(f'1. tab={awal.split("|")[0]} panel={awal.split("|")[1]} '
          f'aktif={awal.split("|")[2]} id={awal.split("|")[3]}')
    if awal != '2|2|1|panel-tahu':
        print('   GAGAL: tab/panel tidak 2/2 atau panel awal salah')
        gagal += 1

    # ── 2. Klik tab "Beri saya contoh" ──
    s.js("document.getElementById('tab-contoh').click()")
    time.sleep(0.4)
    st2 = s.js("""(function(){
      var p = document.querySelector('.panel.aktif');
      return p ? p.id : 'TIDAK-ADA';
    })()""")
    print(f'2. setelah klik tab contoh → panel aktif = {st2}')
    if st2 != 'panel-contoh':
        print('   GAGAL: tab tidak berpindah')
        gagal += 1

    # ── 3. Hitung 6 kartu contoh ──
    jml = s.js("document.querySelectorAll('#kisi-contoh .contoh').length")
    print(f'3. kartu contoh terpasang = {jml}')
    if jml != 6:
        print(f'   GAGAL: harusnya 6, dapat {jml}')
        gagal += 1

    # ── 4. Klik SETIAP contoh, periksa tabel panah + kanvas ──
    for i in range(6):
        s.js(f"document.querySelectorAll('#kisi-contoh .contoh')[{i}].click()")
        time.sleep(0.35)
        d = s.js("""(function(){
          var tb = document.querySelectorAll('#tabel-contoh tbody tr').length;
          var sv = document.querySelectorAll('#kanvas-contoh svg').length;
          var kb = document.querySelectorAll('#kanvas-contoh svg rect').length;
          var pn = document.querySelectorAll('#kanvas-contoh svg line').length;
          var konf = document.getElementById('konfirmasi-rinci').textContent.trim();
          var judul = document.querySelector('#kisi-contoh .contoh.aktif .contoh-judul');
          return [tb, sv, kb, pn, (judul ? judul.textContent : '?'),
                  konf.length].join('|');
        })()""")
        tb, sv, kb, pn, judul, pk = d.split('|')
        tanda = 'OK ' if int(tb) >= 1 and int(sv) == 1 and int(pk) >= 2 else 'CEK'
        if tanda == 'CEK':
            gagal += 1
        print(f'4.{i+1} {tanda} baris={tb} svg={sv} kotak={kb} garis={pn} · {judul[:38]}')
        if int(pk) < 20:
            print(f'      GAGAL: ringkasan konfirmasi kosong ({pk} huruf)')
            gagal += 1

    # ── 5. Tombol konfirmasi ──
    s.js("document.getElementById('btn-ya').click()")
    time.sleep(0.3)
    ya = s.js("""(function(){
      var k = document.getElementById('hasil-contoh');
      return k.style.display + '|' + k.textContent.trim().slice(0,60);
    })()""")
    print(f'5. tombol YA → {ya}')
    if not ya.startswith('block'):
        print('   GAGAL: tombol YA tidak menampilkan jawaban')
        gagal += 1

    s.js("document.getElementById('btn-ubah').click()")
    time.sleep(0.3)
    ub = s.js("""(function(){
      var k = document.getElementById('hasil-contoh');
      return k.className + '|' + k.textContent.trim().slice(0,50);
    })()""")
    print(f'6. tombol UBAH → {ub}')
    if 'batal' not in ub:
        print('   GAGAL: tombol UBAH tidak menandai batal')
        gagal += 1

    # ── 7. Galat JS ──
    g = s.js("(window.__GALAT_JS||[]).join(' | ')")
    print(f'7. galat JS = {g if g else "tidak ada"}')
    if g:
        gagal += 1

    # ── 8. Tangkap potret keadaan contoh C6 (paling ramai) ──
    s.js("document.querySelectorAll('#kisi-contoh .contoh')[5].click()")
    time.sleep(0.5)
    tinggi = s.js('Math.ceil(document.body.scrollHeight)') or 2400
    s.kirim('Emulation.setDeviceMetricsOverride', width=1100,
            height=min(int(tinggi) + 40, 12000), deviceScaleFactor=1, mobile=False)
    time.sleep(0.5)
    r = s.kirim('Page.captureScreenshot', format='png', captureBeyondViewport=True)
    ke = Path('/tmp/mock_konfirmasi_c6.png')
    ke.write_bytes(base64.b64decode(r['data']))
    print(f'8. potret C6 → {ke} ({ke.stat().st_size} byte)')
    if ke.stat().st_size < 20000:
        print('   GAGAL: potret kosong')
        gagal += 1

    # ── 9. Potret keadaan HP 390px ──
    s.kirim('Emulation.setDeviceMetricsOverride', width=390, height=900,
            deviceScaleFactor=1, mobile=True)
    time.sleep(0.6)
    ganti = s.js("document.getElementById('tab-tahu').click()")
    time.sleep(0.4)
    tinggi2 = s.js('Math.ceil(document.body.scrollHeight)') or 2600
    s.kirim('Emulation.setDeviceMetricsOverride', width=390,
            height=min(int(tinggi2) + 40, 14000), deviceScaleFactor=1, mobile=True)
    time.sleep(0.5)
    r2 = s.kirim('Page.captureScreenshot', format='png', captureBeyondViewport=True)
    ke2 = Path('/tmp/mock_konfirmasi_hp.png')
    ke2.write_bytes(base64.b64decode(r2['data']))
    print(f'9. potret HP 390px → {ke2} ({ke2.stat().st_size} byte)')
    if ke2.stat().st_size < 20000:
        print('   GAGAL: potret HP kosong')
        gagal += 1

    ws.close()
    proses.kill()
    print(f'\n=== HASIL: {"LULUS" if gagal == 0 else str(gagal) + " GAGAL"} ===')
    return 1 if gagal else 0


if __name__ == '__main__':
    sys.exit(main())
