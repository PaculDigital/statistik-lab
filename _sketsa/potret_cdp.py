"""Potret halaman via CDP — SATU perintah per sambungan (lebih tahan putus).

⚠️ PELAJARAN (20Sep26): satu skrip panjang yang memakai SATU sambungan
websocket untuk banyak perintah GAMPANG PUTUS (`Connection timed out`).
Cara yang TAHAN: buka sambungan → kirim SATU perintah → baca → tutup.
Perintah yang tahan: `Page.captureScreenshot` LANGSUNG (tanpa
`Emulation.setDeviceMetricsOverride`, tanpa baca tinggi halaman dulu).
"""
import base64
import json
import pathlib
import sys
import urllib.request

CDP = "http://127.0.0.1:9333"


def _put(path):
    return json.loads(urllib.request.urlopen(
        urllib.request.Request(CDP + path, method='PUT'), timeout=20).read())


def _get(path):
    return json.loads(urllib.request.urlopen(CDP + path, timeout=20).read())


def potret(url: str, keluar: str, lebar: int = 760, tinggi: int = 1400,
           skala: float = 2) -> bool:
    """Potret `url` → `keluar`. True kalau berhasil."""
    import websocket
    tab = _put(f'/json/new?{url}')
    try:
        ws = websocket.create_connection(tab['webSocketDebuggerUrl'],
                                         timeout=120)
        try:
            # ⚠️ AKAR 20Sep26 — `clip` + `captureBeyondViewport` DITOLAK Chrome
            # di lingkungan ini: "Unable to capture screenshot" (code -32000).
            # JANGAN dipakai. Yang JALAN: `Page.enable` lalu
            # `Page.captureScreenshot` bentuk PALING SEDERHANA ({format:png}),
            # sementara ukuran jendela diatur lewat flag Chrome
            # `--window-size=LEBAR,TINGGI` saat Chrome dinyalakan.
            for i, (m, p) in enumerate(
                    [('Page.enable', {}),
                     ('Page.captureScreenshot', {'format': 'png'})], 1):
                ws.send(json.dumps({'id': i, 'method': m, 'params': p}))
                while True:
                    r = json.loads(ws.recv())
                    if r.get('id') == i:
                        break
            if 'result' not in r:
                print('  ❌ CDP menolak:', json.dumps(r)[:220])
                return False
            pathlib.Path(keluar).write_bytes(
                base64.b64decode(r['result']['data']))
            return True
        finally:
            try:
                ws.close()
            except Exception:
                pass
    finally:
        try:
            urllib.request.urlopen(
                urllib.request.Request(CDP + '/json/close/' + tab['id']),
                timeout=15).read()
        except Exception:
            pass


if __name__ == '__main__':
    url, keluar = sys.argv[1], sys.argv[2]
    tinggi = int(sys.argv[3]) if len(sys.argv) > 3 else 1400
    ok = potret(url, keluar, tinggi=tinggi)
    if ok:
        p = pathlib.Path(keluar)
        print(f'  ✅ {keluar} ({p.stat().st_size} byte)')
    sys.exit(0 if ok else 1)
