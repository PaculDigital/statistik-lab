"""POTRET MATA untuk ruang MANOVA — kartu ke-5 & hasil di halaman.

⚠️ Potret HANYA untuk diperiksa MATA (aturan 20Sep26: gerbang TIDAK BOLEH
   memotret — Page.captureScreenshot di halaman panjang bikin grup GAGAL).
   Jadi berkas ini ada di _sketsa/, BUKAN di gerbang.

Berguna untuk menjawab: "kartu ke-5 menyambung penuh itu seimbang tidak?"
dan "tabel hasil MANOVA terbaca atau berantakan?"
"""
from __future__ import annotations

import base64
import json
import sys
import time
import urllib.request

import websocket

CDP, APP = 9333, 8122
KELUAR = '/opt/data/services/statistik-lab/_sketsa'


def potret(nama_berkas: str, url: str, persiapan: str = '',
           tunggu: float = 2.5) -> str:
    with urllib.request.urlopen(urllib.request.Request(
            f'http://127.0.0.1:{CDP}/json/new?about:blank',
            method='PUT'), timeout=20) as f:
        tab = json.load(f)
    ws = websocket.create_connection(tab['webSocketDebuggerUrl'],
                                     timeout=90)
    try:
        ws.send(json.dumps({'id': 1, 'method': 'Page.enable'}))
        ws.send(json.dumps({'id': 2, 'method': 'Emulation.setDeviceMetricsOver'
                            'ride', 'params': {
                                'width': 1280, 'height': 900,
                                'deviceScaleFactor': 1, 'mobile': False}}))
        ws.send(json.dumps({'id': 3, 'method': 'Page.navigate',
                            'params': {'url': url}}))
        time.sleep(tunggu)
        if persiapan:
            ws.send(json.dumps({'id': 4, 'method': 'Runtime.evaluate',
                                'params': {'expression': persiapan,
                                           'awaitPromise': True,
                                           'returnByValue': True}}))
            time.sleep(tunggu)
        ws.send(json.dumps({'id': 9, 'method': 'Page.captureScreenshot',
                            'params': {'format': 'png',
                                       'captureBeyondViewport': True}}))
        for _ in range(200):
            r = json.loads(ws.recv())
            if r.get('id') == 9:
                data = r['result']['data']
                jalur = f'{KELUAR}/{nama_berkas}'
                with open(jalur, 'wb') as f:
                    f.write(base64.b64decode(data))
                return jalur
        return ''
    finally:
        ws.close()
        try:
            urllib.request.urlopen(
                f'http://127.0.0.1:{CDP}/json/close/{tab["id"]}',
                timeout=5).read()
        except Exception:                                # noqa: BLE001
            pass


def main() -> int:
    # 1) halaman pilih model — kartu ke-5 harus MENYAMBUNG PENUH
    p1 = potret('manova_1_kuantitatif.png',
                f'http://127.0.0.1:{APP}/kuantitatif')
    print('potret kartu  :', p1)

    # 2) halaman MANOVA — isi & klik, lalu potret HASILNYA
    siap = ("el('mn-nama-y').value='Minat, Nilai';"
            "el('mn-beda').value='0.90, 0.54';"
            "el('mn-isi').value='60';"
            "el('mn-tombol').click();")
    p2 = potret('manova_2_hasil.png',
                f'http://127.0.0.1:{APP}/buat-data?model=banding-kelompok',
                persiapan=siap, tunggu=9.0)
    print('potret hasil  :', p2)
    return 0


if __name__ == '__main__':
    sys.exit(main())
