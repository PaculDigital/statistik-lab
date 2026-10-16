#!/usr/bin/env python3
"""DIAGNOSA: baca DOM halaman ?model=mediasi apa adanya (tanpa asersi).

Dipakai saat uji resmi gagal baca DOM — biar tahu APA yang sebenarnya
terjadi di browser, bukan menebak.
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
URL = 'https://statistik.bikinaja.id/buat-data?model=mediasi'


class WS:
    def __init__(self, ws_url: str) -> None:
        p = urlparse(ws_url)
        self.s = socket.create_connection((p.hostname, p.port), timeout=30)
        k = base64.b64encode(os.urandom(16)).decode()
        self.s.sendall((
            f'GET {p.path} HTTP/1.1\r\nHost: {p.hostname}:{p.port}\r\n'
            f'Upgrade: websocket\r\nConnection: Upgrade\r\n'
            f'Sec-WebSocket-Key: {k}\r\nSec-WebSocket-Version: 13\r\n\r\n'
        ).encode())
        b = b''
        while b'\r\n\r\n' not in b:
            b += self.s.recv(4096)
        self.id = 0
        self.buf = b.split(b'\r\n\r\n', 1)[1]

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
        data = self.buf
        self.buf = b''
        while True:
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
                    sisa = data[awal + n:]
                    self.buf = sisa
                    try:
                        return json.loads(isi.decode('utf-8', 'replace'))
                    except Exception:  # noqa: BLE001
                        return {}
            try:
                potong = self.s.recv(65536)
            except Exception:  # noqa: BLE001
                return {}
            if not potong:
                return {}
            data += potong


def main() -> int:
    with urllib.request.urlopen(f'{CDP}/json/list', timeout=10) as r:
        daftar = json.load(r)
    hal = [t for t in daftar if t.get('type') == 'page'
           and 'buat-data' in (t.get('url') or '')]
    if not hal:
        print('TIDAK ADA tab buat-data')
        return 1
    t = WS(hal[0]['webSocketDebuggerUrl'])
    t.kirim('Runtime.enable')

    for label, expr in [
        ('URL', 'location.href'),
        ('ada JALUR_MODEL?', 'typeof JALUR_MODEL'),
        ('ada terapkanJalurModel?', 'typeof terapkanJalurModel'),
        ('X nilai', '(document.querySelector("#x-nilai")||{}).textContent'),
        ('slider', '(document.querySelector("#x-slider")||{}).value'),
        ('jumlah .nama-var', 'document.querySelectorAll(".nama-var").length'),
        ('isi NAMA', 'JSON.stringify((typeof NAMA!=="undefined")?NAMA.slice(0,4):null)'),
        ('nilai input nama', 'JSON.stringify([...document.querySelectorAll(".nama-var")].map(i=>i.value))'),
        ('ada spanduk', 'document.body.innerText.includes("Kamu memilih")'),
        ('h1', '(document.querySelector("h1")||{}).textContent'),
        ('panjang body', 'document.body.innerText.length'),
    ]:
        r = t.kirim('Runtime.evaluate',
                    {'expression': expr, 'returnByValue': True})
        # ⚠️ JANGAN ambil .get('value') lewat rantai yang bisa pecah — CDP
        # kadang mengembalikan bentuk berbeda. Ambil apa adanya lalu cetak.
        hasil = (r.get('result') or {})
        v = (hasil.get('result') or {}).get('value')
        exc = hasil.get('exceptionDetails')
        tampil = repr(v) if v is not None else (
            f'EXC {str(exc)[:110]}' if exc else 'None')
        print(f'  {label:26s}: {tampil}')

    t.s.close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
