"""POTRET tab "Baca Grafik" (+ tab lain) — DIJALANKAN TERPISAH dari gerbang.

MENGAPA TERPISAH (20Sep26, terukur): potret halaman setinggi 6000+ px lewat
`Page.captureScreenshot` bisa kena WebSocketTimeoutException. Waktu potret itu
ditaruh DI DALAM uji gerbang, grup uji GAGAL (100,2 detik) walau seluruh 16
asserinya LULUS. Gerbang harus menilai KODE, bukan kemampuan memotret.

Pakai:
    .venv/bin/python _sketsa/potret_tab_baca_grafik.py     # tab Baca Grafik
    .venv/bin/python _sketsa/potret_tab_baca_grafik.py materikamus
    .venv/bin/python _sketsa/potret_tab_baca_grafik.py ruanguji
"""
import base64
import json
import sys
import time
import urllib.request
from pathlib import Path

import websocket

PORT, PORT_UJI = 9333, 8122
BASE = f'http://127.0.0.1:{PORT_UJI}'
DIR = Path(__file__).resolve().parent

# nama pendek → (alamat, gulir ke, nama berkas)
TAB = {
    'bacagrafik': ('/belajar#tab-3', 0, 'potret_baca_grafik_pita.png'),
    'materikamus': ('/belajar#tab-1', 0, 'potret_tab_materi.png'),
    'ruanguji': ('/belajar#tab-2', 0, 'potret_tab_ruang_uji.png'),
    'klinik': ('/klinik', 0, 'potret_klinik.png'),
}


class Tab:
    def __init__(self):
        t = json.loads(urllib.request.urlopen(urllib.request.Request(
            f'http://127.0.0.1:{PORT}/json/new?about:blank', method='PUT'),
            timeout=20).read())
        self.tab_id = t['id']
        # timeout besar: memotret halaman panjang memang lambat
        self.ws = websocket.create_connection(t['webSocketDebuggerUrl'], timeout=120)
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
        return r.get('result', {}).get('result', {}).get('value')

    def tutup(self):
        try:
            self.ws.close()
        except Exception:
            pass
        try:
            urllib.request.urlopen(urllib.request.Request(
                f'http://127.0.0.1:{PORT}/json/close/{self.tab_id}'), timeout=15).read()
        except Exception:
            pass


def main():
    kunci = (sys.argv[1] if len(sys.argv) > 1 else 'bacagrafik').lower()
    if kunci not in TAB:
        print(f'  pilihan: {", ".join(TAB)}')
        return 2
    alamat, gulir, nama = TAB[kunci]

    tab = Tab()
    try:
        tab.cmd('Page.enable')
        tab.cmd('Runtime.enable')
        # ⚠️ TINGGI JENDELA WAJIB DIKECILKAN (390×900 seperti HP sungguhan).
        # Percobaan dengan tinggi 1400 px membuat potret lambat & timeout.
        tab.cmd('Emulation.setDeviceMetricsOverride', width=390, height=900,
                deviceScaleFactor=2, mobile=True)
        # dari about:blank dulu supaya hash benar-benar dijalankan
        tab.cmd('Page.navigate', url='about:blank')
        time.sleep(1)
        tab.cmd('Page.navigate', url=BASE + alamat)
        time.sleep(3.5)
        tab.js(f'window.scrollTo(0, {gulir})')
        time.sleep(1.5)
        png = tab.cmd('Page.captureScreenshot', format='png').get('result', {}).get('data')
        if not png:
            print('  ❌ potret kosong — Chrome tidak mengembalikan gambar')
            return 1
        p = DIR / nama
        p.write_bytes(base64.b64decode(png))
        print(f'  ✅ {p}  ({len(base64.b64decode(png))} byte)')
        return 0
    except Exception as e:
        print(f'  ❌ potret gagal: {type(e).__name__}: {e}')
        return 1
    finally:
        tab.tutup()


if __name__ == '__main__':
    sys.exit(main())
