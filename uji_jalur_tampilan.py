#!/usr/bin/env python3
"""UJI TAMPILAN MODE JALUR — pakai Chrome CDP nyata (HP 390px).

MENGAPA ADA: uji HTTP (uji_jalur_model.py) hanya membuktikan KODE TERKIRIM.
Ia TIDAK membuktikan bahwa jalurnya benar-benar bekerja di browser:
slider berubah, nama terisi, spanduk muncul, tidak ada galat JS.

Uji ini menjalankan Chrome sungguhan lewat CDP port 9333 dan MEMBACA DOM.

CARA: .venv/bin/python uji_jalur_tampilan.py
Nilai LULUS/GAGAL dari EXIT CODE.
"""
from __future__ import annotations

import json
import sys
import time
import urllib.request

CDP = 'http://127.0.0.1:9333'
URL = 'https://statistik.bikinaja.id/buat-data?model=mediasi'

lulus = 0
gagal = 0
pesan: list[str] = []


def catat(ok: bool, teks: str) -> None:
    global lulus, gagal
    if ok:
        lulus += 1
        pesan.append(f'  ✅ {teks}')
    else:
        gagal += 1
        pesan.append(f'  ❌ {teks}')


class Tab:
    def __init__(self, ws_url: str) -> None:
        import socket
        import base64
        import os
        from urllib.parse import urlparse
        p = urlparse(ws_url)
        self.s = socket.create_connection((p.hostname, p.port), timeout=25)
        kunci = base64.b64encode(os.urandom(16)).decode()
        self.s.sendall((
            f'GET {p.path} HTTP/1.1\r\nHost: {p.hostname}:{p.port}\r\n'
            f'Upgrade: websocket\r\nConnection: Upgrade\r\n'
            f'Sec-WebSocket-Key: {kunci}\r\nSec-WebSocket-Version: 13\r\n\r\n'
        ).encode())
        buf = b''
        while b'\r\n\r\n' not in buf:
            buf += self.s.recv(4096)
        # ⚠️ WAJIB: simpan sisa byte setelah header HTTP — Chrome sering
        # mengirim sebagian pesan WebSocket bersamaan dengan handshake.
        # Tanpa ini, pesan pertama hilang / terbaca setengah (cacat 19Sep26).
        self.buf = buf.split(b'\r\n\r\n', 1)[1]
        self.id = 0

    def kirim(self, metode: str, params: dict | None = None) -> dict:
        import base64
        import os
        self.id += 1
        isi = json.dumps({'id': self.id, 'method': metode,
                          'params': params or {}}).encode()
        mask = os.urandom(4)
        kepala = bytes([0x81])
        n = len(isi)
        if n < 126:
            kepala += bytes([0x80 | n])
        elif n < 65536:
            kepala += bytes([0x80 | 126]) + n.to_bytes(2, 'big')
        else:
            kepala += bytes([0x80 | 127]) + n.to_bytes(8, 'big')
        kepala += mask
        ter = bytes(b ^ mask[i % 4] for i, b in enumerate(isi))
        self.s.sendall(kepala + ter)
        return self.baca()

    def baca(self) -> dict:
        """Baca SATU pesan, tapi ABAIKAN event (yang tak punya 'id').

        ⚠️ CACAT YANG DIPERBAIKI 19Sep26 (terukur: label bergeser 1 baris):
        Chrome mengirim EVENT (mis. dari Runtime.enable / Page.navigate) yang
        bentuknya MIRIP balasan tapi tanpa 'id'. Kalau Wulan mengembalikan
        event itu sebagai 'balasan', perintah berikutnya membaca hasil
        perintah SEBELUMNYA → nilai None / data tertukar.
        ATURAN: balasan yang sah WAJIB punya 'id'.
        """
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
            # HANYA kembalikan yang punya 'id' (balasan sungguhan).
            if 'id' in pesan:
                return pesan
            # event → lanjut baca pesan berikutnya


def main() -> int:
    try:
        with urllib.request.urlopen(f'{CDP}/json/list', timeout=10) as r:
            daftar = json.load(r)
    except Exception as e:  # noqa: BLE001
        catat(False, f'CDP tak terjangkau: {e}')
        print('\n'.join(pesan))
        return 1

    hal = [t for t in daftar if t.get('type') == 'page']
    catat(len(hal) < 6, f'tab wajar ({len(hal)} tab, <6)')
    if not hal:
        catat(False, 'tidak ada tab')
        print('\n'.join(pesan))
        return 1

    ws = hal[0]['webSocketDebuggerUrl']
    t = Tab(ws)
    t.kirim('Page.enable')
    t.kirim('Emulation.setDeviceMetricsOverride',
            {'width': 390, 'height': 844, 'deviceScaleFactor': 2,
             'mobile': True})
    t.kirim('Page.navigate', {'url': URL})
    time.sleep(6)

    js = ('(() => {'
          'const x = document.querySelector("#x-nilai");'
          'const sld = document.querySelector("#x-slider");'
          'const nama = [...document.querySelectorAll(".nama-var")].map(i => i.value);'
          'const teks = document.body.innerText;'
          'const h1 = (document.querySelector("h1")||{}).textContent || "";'
          'const ada = teks.includes("Kamu memilih");'
          'const ganti = !!document.querySelector(\'a[href="/kuantitatif"]\');'
          'const cara = [...document.querySelectorAll(".pilih-cara")]'
          '  .filter(c => c.checked).map(c => c.dataset.cara);'
          'return JSON.stringify({x: x ? x.textContent : null,'
          '  slider: sld ? sld.value : null, nama, h1, ada, ganti, cara});'
          '})()')
    r = t.kirim('Runtime.evaluate',
                {'expression': js, 'returnByValue': True})
    # ⚠️ CDP mengembalikan nilai di result.result.value — dan hasilnya
    # SUDAH berupa STRING JSON. Salah baca di sini pernah bikin Wulan
    # menyatakan "gagal" padahal aplikasinya jalan (19Sep26).
    hasil = (r.get('result', {}).get('result', {}) or {}).get('value')
    if isinstance(hasil, dict):
        d = hasil
    elif isinstance(hasil, str) and hasil.startswith('{'):
        d = json.loads(hasil)
    else:
        catat(False, f'gagal baca DOM (nilai: {str(hasil)[:200]})')
        print('\n'.join(pesan))
        return 1
    catat(d['ada'], 'spanduk "Kamu memilih" MUNCUL ("Ada perantara (X → perantara → Y)")')
    catat(d['ganti'], 'tombol "Pilih model lain" ADA')
    catat(d['x'] == '2', f'jumlah X tersetel 2 (terbaca: {d["x"]})')
    catat(d['slider'] == '2', f'slider di posisi 2 (terbaca: {d["slider"]})')
    catat(any(n.strip() for n in d['nama']),
          f'nama variabel TERISI contoh: {[n for n in d["nama"] if n][:3]}')
    catat('perantara' in d['h1'].lower() or 'pengaruh' in d['h1'].lower(),
          f'judul halaman disesuaikan: "{d["h1"][:50]}"')

    # galat JS di konsol
    r2 = t.kirim('Runtime.evaluate', {
        'expression': 'JSON.stringify(window.__galatJS || [])',
        'returnByValue': True})
    g = r2.get('result', {}).get('result', {}).get('value') or '[]'
    catat(g in ('[]', None, ''), f'tidak ada galat JS tercatat ({g[:80]})')

    t.s.close()
    print('\n'.join(pesan))
    print(f'\n{lulus} LULUS / {gagal} GAGAL')
    return 0 if gagal == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
