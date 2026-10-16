#!/usr/bin/env python3
"""TANGKAPAN LAYAR halaman ?model= — HP 390px, dari DOMAIN PRODUKSI.

MENGAPA ADA: Bos mengaudit dengan MATA dan minta BUKTI nyata, bukan klaim.
Uji lulus ≠ tampilan enak dilihat. Skrip ini menyimpan .png sungguhan
supaya Bos bisa menilai sendiri.

CARA: .venv/bin/python _sketsa/tangkap_jalur.py
Hasil: /tmp/jalur_<slug>.png
⚠️ WAJIB cek berkas > 10 KB ([ -s ]) — jangan percaya "berhasil".
"""
from __future__ import annotations

import base64
import json
import os
import socket
import sys
import time
import urllib.request
from urllib.parse import urlparse

CDP = 'http://127.0.0.1:9333'
HALAMAN = [
    ('mediasi', 'https://statistik.bikinaja.id/buat-data?model=mediasi'),
    ('kuantitatif', 'https://statistik.bikinaja.id/kuantitatif'),
]


class WS:
    def __init__(self, ws_url: str) -> None:
        p = urlparse(ws_url)
        self.s = socket.create_connection((p.hostname, p.port), timeout=40)
        k = base64.b64encode(os.urandom(16)).decode()
        self.s.sendall((
            f'GET {p.path} HTTP/1.1\r\nHost: {p.hostname}:{p.port}\r\n'
            f'Upgrade: websocket\r\nConnection: Upgrade\r\n'
            f'Sec-WebSocket-Key: {k}\r\nSec-WebSocket-Version: 13\r\n\r\n'
        ).encode())
        buf = b''
        while b'\r\n\r\n' not in buf:
            buf += self.s.recv(4096)
        self.buf = buf.split(b'\r\n\r\n', 1)[1]
        self.id = 0

    def kirim(self, metode: str, params: dict | None = None) -> dict:
        self.id += 1
        isi = json.dumps({'id': self.id, 'method': metode,
                          'params': params or {}}).encode()
        mask = os.urandom(4)
        n = len(isi)
        kepala = bytes([0x81])
        if n < 126:
            kepala += bytes([0x80 | n])
        elif n < 65536:
            kepala += bytes([0x80 | 126]) + n.to_bytes(2, 'big')
        else:
            kepala += bytes([0x80 | 127]) + n.to_bytes(8, 'big')
        kepala += mask
        self.s.sendall(kepala + bytes(b ^ mask[i % 4]
                                      for i, b in enumerate(isi)))
        return self.baca()

    def baca(self) -> dict:
        while True:
            data = self.buf
            self.buf = b''
            selesai = False
            while not selesai:
                if len(data) >= 2:
                    panjang = data[1] & 0x7F
                    if panjang == 126:
                        if len(data) >= 4:
                            n, awal = int.from_bytes(data[2:4], 'big'), 4
                        else:
                            data += self.s.recv(65536)
                            continue
                    elif panjang == 127:
                        if len(data) >= 10:
                            n, awal = int.from_bytes(data[2:10], 'big'), 10
                        else:
                            data += self.s.recv(65536)
                            continue
                    else:
                        n, awal = panjang, 2
                    if len(data) >= awal + n:
                        isi = data[awal:awal + n]
                        self.buf = data[awal + n:]
                        selesai = True
                        break
                potong = self.s.recv(65536)
                if not potong:
                    return {}
                data += potong
            try:
                pesan = json.loads(isi.decode('utf-8', 'replace'))
            except Exception:  # noqa: BLE001
                continue
            if 'id' in pesan:
                return pesan


def main() -> int:
    with urllib.request.urlopen(f'{CDP}/json/list', timeout=10) as r:
        daftar = json.load(r)
    hal = [t for t in daftar if t.get('type') == 'page']
    if not hal:
        print('tidak ada tab')
        return 1
    t = WS(hal[0]['webSocketDebuggerUrl'])
    t.kirim('Page.enable')
    t.kirim('Emulation.setDeviceMetricsOverride',
            {'width': 390, 'height': 900, 'deviceScaleFactor': 2,
             'mobile': True})

    for slug, url in HALAMAN:
        t.kirim('Page.navigate', {'url': url})
        time.sleep(7)
        # tinggi pas isi — hindari captureBeyondViewport (gagal di halaman tinggi)
        r = t.kirim('Runtime.evaluate', {
            'expression': 'Math.min(document.body.scrollHeight, 6000)',
            'returnByValue': True})
        tinggi = (r.get('result') or {}).get('result', {}).get('value') or 900
        t.kirim('Emulation.setDeviceMetricsOverride',
                {'width': 390, 'height': int(tinggi), 'deviceScaleFactor': 1,
                 'mobile': True})
        time.sleep(1.5)
        s = t.kirim('Page.captureScreenshot', {'format': 'png'})
        data = (s.get('result') or {}).get('data')
        if not data:
            print(f'  {slug}: GAGAL tangkap — {str(s)[:150]}')
            continue
        keluar = f'/tmp/jalur_{slug}.png'
        with open(keluar, 'wb') as f:
            f.write(base64.b64decode(data))
        ukuran = os.path.getsize(keluar)
        tanda = 'OK ' if ukuran > 10000 else 'KECIL'
        print(f'  {tanda} {keluar}  {ukuran} byte  (tinggi {tinggi}px)')

    t.s.close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
