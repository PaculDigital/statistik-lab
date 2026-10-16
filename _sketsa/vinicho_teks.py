"""Baca TEKS tampil halaman buku vinicho (via Chrome CDP :9333)."""
from __future__ import annotations

import base64
import json
import socket
import struct
import sys
import time
import urllib.request

PORT = 9333
URL = ('https://www.vinichopublisindo.com/katalog/'
       'material-teknik-pengantar-dan-aplikasi-lanjut/')


class Tab:
    def __init__(self, url: str = 'about:blank') -> None:
        req = urllib.request.Request(
            f'http://127.0.0.1:{PORT}/json/new?{url}', method='PUT')
        with urllib.request.urlopen(req, timeout=15) as f:
            d = json.load(f)
        self.tab_id = d['id']
        self.ws = d['webSocketDebuggerUrl']
        self.sock = self._sambung()
        self.n = 0

    def _sambung(self):
        u = self.ws.replace('ws://', '')
        host, sisa = u.split(':', 1)
        port, path = sisa.split('/', 1)
        s = socket.create_connection((host, int(port)), timeout=30)
        k = base64.b64encode(b'wulan-analisa-12345').decode()
        s.sendall((f'GET /{path} HTTP/1.1\r\nHost: {host}:{port}\r\n'
                   f'Upgrade: websocket\r\nConnection: Upgrade\r\n'
                   f'Sec-WebSocket-Key: {k}\r\n'
                   f'Sec-WebSocket-Version: 13\r\n\r\n').encode())
        buf = b''
        while b'\r\n\r\n' not in buf:
            buf += s.recv(4096)
        return s

    def _kirim(self, teks: str) -> None:
        data = teks.encode()
        p = len(data)
        if p < 126:
            hdr = struct.pack('!BB', 0x81, 0x80 | p)
        elif p < 65536:
            hdr = struct.pack('!BBH', 0x81, 0x80 | 126, p)
        else:
            hdr = struct.pack('!BBQ', 0x81, 0x80 | 127, p)
        self.sock.sendall(hdr + b'\x00\x00\x00\x00' + data)

    def _baca(self) -> dict:
        while True:
            b1 = self.sock.recv(1)
            if not b1:
                raise ConnectionError('socket tertutup')
            p = self.sock.recv(1)[0] & 0x7F
            if p == 126:
                p = struct.unpack('!H', self.sock.recv(2))[0]
            elif p == 127:
                p = struct.unpack('!Q', self.sock.recv(8))[0]
            isi = b''
            while len(isi) < p:
                isi += self.sock.recv(p - len(isi))
            m = json.loads(isi.decode('utf-8', 'replace'))
            if 'id' in m:
                return m

    def perintah(self, metode: str, **kw) -> dict:
        self.n += 1
        self._kirim(json.dumps({'id': self.n, 'method': metode,
                                'params': kw or {}}))
        while True:
            m = self._baca()
            if m.get('id') == self.n:
                return m.get('result') or m.get('error') or {}

    def js(self, e: str):
        r = self.perintah('Runtime.evaluate', expression=e,
                          returnByValue=True, awaitPromise=True)
        return (r.get('result') or {}).get('value')

    def tutup(self) -> None:
        try:
            self.sock.close()
        finally:
            try:
                urllib.request.urlopen(
                    f'http://127.0.0.1:{PORT}/json/close/{self.tab_id}',
                    timeout=10).read()
            except Exception:
                pass


def main() -> int:
    t = Tab('about:blank')
    try:
        t.perintah('Page.enable')
        t.perintah('Runtime.enable')
        t.perintah('Page.navigate', url=URL)
        time.sleep(9)
        teks = t.js('document.body.innerText') or ''
        with open('/tmp/vinicho_teks.txt', 'w') as f:
            f.write(teks)
        print(teks[:5000])
    finally:
        t.tutup()
    return 0


if __name__ == '__main__':
    sys.exit(main())
