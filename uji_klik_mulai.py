#!/usr/bin/env python3
"""UJI KLIK SUNGGUHAN di halaman /mulai lewat CDP (port 9333).

MENGAPA LEWAT CDP, BUKAN LEWAT FETCH (pelajaran EduAi 15Sep26):
Uji lewat fetch/API MENIPU — dia melewati pemeriksaan JavaScript browser.
Jadi bug JS (skrip tumpah jadi teks, tombol tidak nyambung, localStorage
gagal) TIDAK akan ketemu. Di sini Wulan MENEKAN TOMBOL seperti user.

KENAPA WEBSOCKET MENTAH: CDP hanya bicara lewat websocket. Pustaka
standar Python tidak punya klien websocket, dan Wulan TIDAK boleh
menambah dependensi ke proyek hanya untuk alat uji. Jadi protokol
websocket ditulis sendiri di bawah (~40 baris). Tanpa dependensi baru.

YANG DIUJI:
 1. Halaman memuat tanpa galat JavaScript
 2. Tidak ada kode tumpah jadi teks
 3. Tombol "Cek rekomendasi" benar-benar mengisi kotak hasil
 4. Judul SAMA kedua kali TIDAK mengirim permintaan (hemat jatah/AI)
 5. Riwayat judul muncul & bisa dipakai lagi
 6. Tautan "Ya, pakai ini" menunjuk halaman model yang benar
 7. Jatah dari server tertampil

CARA JALAN:  .venv/bin/python uji_klik_mulai.py
"""
from __future__ import annotations

import base64
import json
import os
import socket
import struct
import sys
import urllib.request

CDP = 'http://127.0.0.1:9333'
HAL = os.environ.get('HAL_UJI', 'https://statistik.bikinaja.id/mulai')

LULUS = 0
GAGAL = 0


def cek(nama: str, syarat: bool, bukti: str = '') -> None:
    global LULUS, GAGAL
    if syarat:
        LULUS += 1
        print(f'  ✅ {nama}' + (f' → {bukti}' if bukti else ''))
    else:
        GAGAL += 1
        print(f'  ❌ {nama}' + (f' → {bukti}' if bukti else ''))


# ══════════════════════════════════════════════════════════════════════
#  WEBSOCKET MENTAH (tanpa dependensi) — cukup untuk CDP
# ══════════════════════════════════════════════════════════════════════
class WS:
    def __init__(self, url: str) -> None:
        tanpa = url.replace('ws://', '')
        hostport, _, path = tanpa.partition('/')
        host, _, port = hostport.partition(':')
        self.s = socket.create_connection((host, int(port or 80)), timeout=30)
        kunci = base64.b64encode(os.urandom(16)).decode()
        permintaan = (
            f'GET /{path} HTTP/1.1\r\nHost: {hostport}\r\n'
            f'Upgrade: websocket\r\nConnection: Upgrade\r\n'
            f'Sec-WebSocket-Key: {kunci}\r\nSec-WebSocket-Version: 13\r\n\r\n')
        self.s.sendall(permintaan.encode())
        buf = b''
        while b'\r\n\r\n' not in buf:
            buf += self.s.recv(4096)
        if b'101' not in buf.split(b'\r\n')[0]:
            raise RuntimeError('websocket ditolak')

    def _kirim_bingkai(self, data: bytes, opcode: int = 1) -> None:
        kepala = bytes([0x80 | opcode])
        n = len(data)
        if n < 126:
            kepala += bytes([0x80 | n])
        elif n < 65536:
            kepala += bytes([0x80 | 126]) + struct.pack('!H', n)
        else:
            kepala += bytes([0x80 | 127]) + struct.pack('!Q', n)
        mask = os.urandom(4)
        kepala += mask
        bertopeng = bytes(b ^ mask[i % 4] for i, b in enumerate(data))
        self.s.sendall(kepala + bertopeng)

    def _baca_tepat(self, n: int) -> bytes:
        buf = b''
        while len(buf) < n:
            potong = self.s.recv(n - len(buf))
            if not potong:
                raise RuntimeError('koneksi ditutup')
            buf += potong
        return buf

    def _baca_bingkai(self) -> str:
        b1, b2 = self._baca_tepat(2)
        n = b2 & 0x7F
        if n == 126:
            n = struct.unpack('!H', self._baca_tepat(2))[0]
        elif n == 127:
            n = struct.unpack('!Q', self._baca_tepat(8))[0]
        return self._baca_tepat(n).decode('utf-8', 'replace')

    def perintah(self, no: int, metode: str, **p) -> dict:
        self._kirim_bingkai(
            json.dumps({'id': no, 'method': metode, 'params': p}).encode())
        while True:
            d = json.loads(self._baca_bingkai())
            if d.get('id') == no:
                return d

    def tutup(self) -> None:
        try:
            self._kirim_bingkai(b'', opcode=8)
            self.s.close()
        except Exception:                               # noqa: BLE001
            pass


def tab_baru(url: str) -> tuple[WS, str]:
    req = urllib.request.Request(f'{CDP}/json/new?{url}', method='PUT')
    with urllib.request.urlopen(req, timeout=20) as r:
        d = json.loads(r.read().decode())
    return WS(d['webSocketDebuggerUrl']), d['id']


def main() -> int:
    print('═' * 66)
    print(f'UJI KLIK SUNGGUHAN /mulai lewat CDP → {HAL}')
    print('═' * 66)

    try:
        urllib.request.urlopen(f'{CDP}/json/version', timeout=6)
    except Exception:                                   # noqa: BLE001
        print('❌ Chrome debug (9333) tidak jalan.')
        return 1

    ws, _ = tab_baru('about:blank')
    no = 0

    def js(ekspresi: str):
        """Jalankan JS, kembalikan nilainya."""
        nonlocal no
        no += 1
        d = ws.perintah(no, 'Runtime.evaluate', expression=ekspresi,
                        returnByValue=True, awaitPromise=True)
        hasil = d.get('result', {}).get('result', {})
        if d.get('result', {}).get('exceptionDetails'):
            return {'__galat__': d['result']['exceptionDetails']
                    .get('exception', {}).get('description', 'galat')}
        return hasil.get('value')

    # kumpulkan galat konsol
    nonlocal_galat: list[str] = []
    no += 1
    ws.perintah(no, 'Runtime.enable')
    no += 1
    ws.perintah(no, 'Page.enable')

    print('\n[1] Halaman memuat')
    no += 1
    ws.perintah(no, 'Page.navigate', url=HAL)
    for _ in range(40):
        import time
        time.sleep(0.5)
        siap = js('document.readyState')
        if siap == 'complete':
            break
    cek('halaman selesai dimuat', js('document.readyState') == 'complete',
        str(js('document.readyState')))

    # ── pasang perekam galat SEBELUM berinteraksi ─────────────────────────
    js('window.__galat = [];'
       'window.addEventListener("error", function(e){ window.__galat.push('
       'String(e.message||e)); });'
       'window.__asliFetch = window.fetch;'
       'window.__panggilan = 0;'
       'window.fetch = function(){ window.__panggilan++; '
       'return window.__asliFetch.apply(this, arguments); };')

    # ── 2. tidak ada kode tumpah jadi teks ────────────────────────────────
    print('\n[2] Tidak ada kode tumpah jadi teks')
    teks = js('document.body.innerText') or ''
    cek('tidak ada "</strong>" jadi teks', '</strong>' not in teks)
    cek('tidak ada "function()" jadi teks', 'function()' not in teks)
    cek('tidak ada "</script>" jadi teks', '</script>' not in teks)

    # ── 3. elemen kunci ada ───────────────────────────────────────────────
    print('\n[3] Elemen kunci ada di halaman')
    cek('kotak judul ada', js('!!document.getElementById("judul")'))
    cek('tombol cek ada', js('!!document.getElementById("tombol-cek")'))
    cek('kotak hasil tersembunyi di awal',
        js('document.getElementById("hasil").hidden === true'))

    # ── 4. tekan tombol dengan judul jelas ────────────────────────────────
    print('\n[4] Tombol "Cek rekomendasi" benar-benar bekerja')
    js('''(() => {
      const t = document.getElementById('judul');
      t.value = 'Pengaruh Harga dan Promosi terhadap Keputusan Pembelian';
      window.__panggilan = 0;
      document.getElementById('tombol-cek').click();
    })()''')
    for _ in range(30):
        import time
        time.sleep(0.5)
        if js('document.getElementById("hasil").hidden === false'):
            break
    cek('kotak hasil tampil setelah tombol ditekan',
        js('document.getElementById("hasil").hidden === false'))
    model1 = js('document.getElementById("hasil-model").textContent') or ''
    cek('model terisi (bukan kosong)', len(model1.strip()) > 5, model1.strip())
    cek('menyebut model yang benar (Berganda)', 'Berganda' in model1, model1.strip())
    alasan1 = js('document.getElementById("hasil-alasan").textContent') or ''
    cek('alasan terisi', len(alasan1.strip()) > 10, alasan1.strip()[:70] + '…')
    tautan = js('(document.getElementById("pakai-ini")||{}).getAttribute '
                '? document.getElementById("pakai-ini").getAttribute("href") : ""')
    cek('tautan "Ya, pakai ini" menuju model berganda',
        tautan and 'model=berganda' in tautan, str(tautan))

    # ── 5. judul SAMA kedua kali → TIDAK mengirim permintaan ─────────────
    print('\n[5] Judul SAMA kedua kali tidak dikirim ke server (hemat jatah)')
    js('window.__panggilan = 0;'
       'document.getElementById("tombol-cek").click();')
    import time
    time.sleep(2.0)
    panggilan = js('window.__panggilan')
    cek('permintaan kedua = 0 (diambil dari simpanan browser)',
        panggilan == 0, f'{panggilan} permintaan')
    cek('hasil tetap tampil',
        js('document.getElementById("hasil").hidden === false'))

    # ── 6. riwayat judul muncul & bisa dipakai lagi ───────────────────────
    print('\n[6] Riwayat judul muncul dan bisa dipakai lagi')
    cek('kartu riwayat tampil',
        js('document.getElementById("kartu-riwayat").hidden === false'))
    n_riwayat = js('document.querySelectorAll(".baris-riwayat").length')
    cek('ada minimal 1 baris riwayat', (n_riwayat or 0) >= 1, f'{n_riwayat} baris')
    cek('CSS riwayat dibatasi 5 baris (max-height 342px)',
        js('''(() => { const d=document.querySelector('.daftar-riwayat');
             return !!d && getComputedStyle(d).maxHeight === '342px'; })()'''))
    cek('riwayat bisa di-scroll',
        js('''(() => { const d=document.querySelector('.daftar-riwayat');
             return !!d && getComputedStyle(d).overflowY === 'auto'; })()'''))

    # ── 7. jatah dari server tertampil ────────────────────────────────────
    print('\n[7] Jatah dari server tertampil (bukan angka di JS)')
    sisa = js('document.getElementById("sisa-jatah").textContent') or ''
    cek('sisa jatah tertampil', 'tersisa' in sisa, sisa.strip())

    # ── 8. galat JavaScript ───────────────────────────────────────────────
    print('\n[8] Tidak ada galat JavaScript')
    g = js('JSON.stringify(window.__galat || [])')
    cek('nol galat JavaScript', g in ('[]', None), str(g))

    # ── 9. judul kabur → jujur tidak memaksa ──────────────────────────────
    print('\n[9] Judul kabur dijawab jujur (tidak dipaksa tebak)')
    js('''(() => {
      const t = document.getElementById('judul');
      t.value = 'Analisis Determinan Pendapatan Petani Padi';
      window.__panggilan = 0;
      document.getElementById('tombol-cek').click();
    })()''')
    for _ in range(30):
        time.sleep(0.5)
        m = js('document.getElementById("hasil-model").textContent') or ''
        if 'dipastikan' in m or 'Belum' in m:
            break
    m2 = js('document.getElementById("hasil-model").textContent') or ''
    cek('judul kabur tidak dipaksa jadi model tertentu',
        ('dipastikan' in m2 or 'Belum' in m2), m2.strip())
    cek('tombol "Ya, pakai ini" disembunyikan saat ragu',
        js('document.getElementById("pakai-ini").hidden === true'))

    print('\n' + '=' * 66)
    print(f'HASIL UJI KLIK: {LULUS} LULUS / {GAGAL} GAGAL')
    print('=' * 66)
    ws.tutup()
    return 0 if GAGAL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
