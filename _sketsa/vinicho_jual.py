"""Teliti SISTEM PEMBELIAN halaman buku vinicho.

1. Baca tombol/tautan "Pesan Sekarang" → ke mana perginya (href/onclick)?
2. Periksa halaman BERANDA + KATALOG → pola katalog.
3. Simpan bukti ke /tmp.
"""
from __future__ import annotations

import base64
import json
import socket
import struct
import sys
import time
import urllib.request

PORT = 9333
URL_BUKU = ('https://www.vinichopublisindo.com/katalog/'
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
                raise ConnectionError('tutup')
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

    def ke(self, url: str, tunggu: float = 8.0) -> None:
        self.perintah('Page.navigate', url=url)
        time.sleep(tunggu)

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


js_tombol = r"""
(() => {
  const out = [];
  document.querySelectorAll('a, button').forEach(el => {
    const t = (el.innerText || el.value || '').trim();
    if (!t) return;
    if (t.length > 60) return;
    out.push({teks: t, tag: el.tagName,
              href: el.getAttribute('href') || '',
              onclick: (el.getAttribute('onclick') || '').slice(0,120),
              kelas: (el.className || '').toString().slice(0,90)});
  });
  return JSON.stringify(out);
})()
"""


def main() -> int:
    t = Tab('about:blank')
    try:
        t.perintah('Page.enable')
        t.perintah('Runtime.enable')

        # ── A. Halaman BUKU: semua tombol/tautan ──────────────────────
        t.ke(URL_BUKU)
        print('=' * 72)
        print('A. TOMBOL & TAUTAN DI HALAMAN BUKU')
        print('=' * 72)
        tombol = json.loads(t.js(js_tombol) or '[]')
        for b in tombol:
            if b['href'] and b['href'] != '#':
                print(f"  [{b['tag']:6}] {b['teks'][:34]:36} href={b['href'][:70]}")
            elif b['onclick']:
                print(f"  [{b['tag']:6}] {b['teks'][:34]:36} onclick={b['onclick'][:70]}")
            else:
                print(f"  [{b['tag']:6}] {b['teks'][:34]:36} kelas={b['kelas'][:60]}")

        # ── B. Beranda ────────────────────────────────────────────────
        t.ke('https://www.vinichopublisindo.com/')
        print()
        print('=' * 72)
        print('B. BERANDA — menu & tautan utama')
        print('=' * 72)
        print('  judul:', t.js('document.title'))
        nav = t.js(r"""JSON.stringify([...document.querySelectorAll('nav a, header a')]
          .map(a => a.innerText.trim() + ' -> ' + (a.getAttribute('href')||'')).filter(x=>x.length>4).slice(0,25))""")
        for x in json.loads(nav or '[]'):
            print('  ', x[:110])

        # ── C. Katalog ────────────────────────────────────────────────
        t.ke('https://www.vinichopublisindo.com/katalog/')
        print()
        print('=' * 72)
        print('C. HALAMAN KATALOG')
        print('=' * 72)
        print('  judul:', t.js('document.title'))
        print('  jumlah kartu buku:',
              t.js("document.querySelectorAll('article, .card, .product').length"))

        # ── D. Cek endpoint /cara-pesan / keranjang ───────────────────
        print()
        print('=' * 72)
        print('D. HALAMAN LAIN YANG MUNGKIN (status HTTP)')
        print('=' * 72)
        for p in ('/cara-pesan/', '/keranjang/', '/cart/', '/checkout/',
                  '/tentang/', '/kontak/', '/penerbitan/', '/beranda/',
                  '/katalog/', '/wp-json/', '/wp-admin/'):
            kode = t.js(f"""fetch('https://www.vinichopublisindo.com{p}',
              {{redirect:'manual'}}).then(r=>r.status).catch(e=>'ERR')""")
            print(f'  {p:16} -> {kode}')
    finally:
        t.tutup()
    return 0


if __name__ == '__main__':
    sys.exit(main())
