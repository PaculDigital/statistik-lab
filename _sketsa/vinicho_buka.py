"""Pelajari struktur web vinichopublisindo.com — halaman katalog buku.

Tujuan: analisa DETAIL (struktur, framework, halaman buku, sistem pembelian).
Metode: Chrome CDP :9333 (sudah terbukti dipakai statistik-lab) — socket mentah,
tanpa `websockets` (tak ada Origin header → tak kena 403).

Keluaran: ringkasan teks + simpan HTML mentah ke /tmp untuk diperiksa lanjut.
"""
from __future__ import annotations

import base64
import json
import socket
import struct
import sys
import urllib.request

PORT = 9333
URL = ('https://www.vinichopublisindo.com/katalog/'
       'material-teknik-pengantar-dan-aplikasi-lanjut/')


class Tab:
    """Tab CDP sederhana (pola uji_jalur_tampilan.py statistik-lab)."""

    def __init__(self, url: str = 'about:blank') -> None:
        # Chrome baru butuh METHOD PUT untuk /json/new (GET → 405)
        req = urllib.request.Request(
            f'http://127.0.0.1:{PORT}/json/new?{url}', method='PUT')
        with urllib.request.urlopen(req, timeout=15) as f:
            d = json.load(f)
        self.tab_id = d['id']
        self.ws = d['webSocketDebuggerUrl']
        self.sock = self._sambung()
        self.n = 0

    def _sambung(self) -> socket.socket:
        u = self.ws.replace('ws://', '')
        host, sisa = u.split(':', 1)
        port, path = sisa.split('/', 1)
        s = socket.create_connection((host, int(port)), timeout=30)
        kunci = base64.b64encode(b'wulan-analisa-12345').decode()
        s.sendall((
            f'GET /{path} HTTP/1.1\r\nHost: {host}:{port}\r\n'
            f'Upgrade: websocket\r\nConnection: Upgrade\r\n'
            f'Sec-WebSocket-Key: {kunci}\r\nSec-WebSocket-Version: 13\r\n\r\n'
        ).encode())
        buf = b''
        while b'\r\n\r\n' not in buf:
            buf += s.recv(4096)
        return s

    def _kirim(self, teks: str) -> None:
        data = teks.encode()
        panjang = len(data)
        if panjang < 126:
            hdr = struct.pack('!BB', 0x81, 0x80 | panjang)
        elif panjang < 65536:
            hdr = struct.pack('!BBH', 0x81, 0x80 | 126, panjang)
        else:
            hdr = struct.pack('!BBQ', 0x81, 0x80 | 127, panjang)
        mask = b'\x00\x00\x00\x00'
        self.sock.sendall(hdr + mask + data)

    def _baca(self) -> dict:
        while True:
            b1 = self.sock.recv(1)
            if not b1:
                raise ConnectionError('socket tertutup')
            b2 = self.sock.recv(1)[0]
            panjang = b2 & 0x7F
            if panjang == 126:
                panjang = struct.unpack('!H', self.sock.recv(2))[0]
            elif panjang == 127:
                panjang = struct.unpack('!Q', self.sock.recv(8))[0]
            isi = b''
            while len(isi) < panjang:
                isi += self.sock.recv(panjang - len(isi))
            pesan = json.loads(isi.decode('utf-8', 'replace'))
            if 'id' in pesan:          # event tanpa id → buang
                return pesan

    def perintah(self, metode: str, **kw) -> dict:
        self.n += 1
        self._kirim(json.dumps({'id': self.n, 'method': metode,
                                'params': kw or {}}))
        while True:
            pesan = self._baca()
            if pesan.get('id') == self.n:
                return pesan.get('result') or pesan.get('error') or {}

    def js(self, ekspresi: str):
        r = self.perintah('Runtime.evaluate', expression=ekspresi,
                          returnByValue=True, awaitPromise=True)
        v = (r.get('result') or {}).get('value')
        return v

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
        import time
        time.sleep(9)
        print('URL sekarang :', t.js('location.href'))
        print('Judul        :', t.js('document.title'))
        print('Panjang HTML :', t.js('document.documentElement.outerHTML.length'))
        # simpan HTML lengkap untuk diperiksa
        html = t.js('document.documentElement.outerHTML')
        with open('/tmp/vinicho_buku.html', 'w') as f:
            f.write(html or '')
        print('tersimpan    : /tmp/vinicho_buku.html',
              len(html or ''), 'char')
    finally:
        t.tutup()
    return 0


if __name__ == '__main__':
    sys.exit(main())
