"""UJI MODERASI LEWAT HALAMAN SUNGGUHAN (jalur mahasiswa).

⚠️ PELAJARAN K-18 (21Sep26): uji moderasi sebelumnya mengirim `kolom_z`
LANGSUNG ke API, padahal HALAMAN tidak pernah mengirimnya → moderasi
selalu kosong di pemakaian nyata. Menguji API langsung MENYEMBUNYIKAN
cacat jalur halaman.

Uji ini memakai Chrome nyata: buka /klinik → unggah berkas → tandai peran
(X/M/Z/Y lewat dropdown) → tekan periksa → baca hasilnya.

Nilai LULUS/GAGAL dari EXIT CODE.
"""
from __future__ import annotations
import base64, json, os, sys, time, urllib.request

sys.path.insert(0, '.')
CDP = 'http://127.0.0.1:9333'
URL = 'http://127.0.0.1:8122/klinik'
lulus = 0
gagal = 0
pesan: list[str] = []


def catat(ok: bool, teks: str, tambahan: str = '') -> None:
    global lulus, gagal
    if ok:
        lulus += 1
        pesan.append(f'  ✅ {teks}' + (f'   {tambahan}' if tambahan else ''))
    else:
        gagal += 1
        pesan.append(f'  ❌ {teks}' + (f'   {tambahan}' if tambahan else ''))


def nilai(r):
    return (r.get('result', {}).get('result', {}) or {}).get('value')


class Tab:
    """CDP socket mentah — pola sama uji_jalur_tampilan.Tab (terbukti)."""

    def __init__(self, ws):
        import socket
        from urllib.parse import urlparse
        u = urlparse(ws)
        self.s = socket.create_connection((u.hostname, u.port), timeout=60)
        kunci = base64.b64encode(os.urandom(16)).decode()
        self.s.sendall((
            f'GET {u.path} HTTP/1.1\r\nHost: {u.hostname}:{u.port}\r\n'
            f'Upgrade: websocket\r\nConnection: Upgrade\r\n'
            f'Sec-WebSocket-Key: {kunci}\r\nSec-WebSocket-Version: 13\r\n\r\n'
        ).encode())
        b = b''
        while b'\r\n\r\n' not in b:
            b += self.s.recv(4096)
        self.n = 0

    def _frm(self, data, op=1):
        p = data.encode() if isinstance(data, str) else data
        h = bytearray([0x80 | op])
        n = len(p)
        if n < 126:
            h.append(0x80 | n)
        elif n < 65536:
            h.append(0x80 | 126)
            h += n.to_bytes(2, 'big')
        else:
            h.append(0x80 | 127)
            h += n.to_bytes(8, 'big')
        import struct
        m = os.urandom(4)
        return bytes(h) + m + bytes(c ^ m[i % 4] for i, c in enumerate(p))

    def kirim(self, method, params=None):
        self.n += 1
        self.s.sendall(self._frm(json.dumps(
            {'id': self.n, 'method': method, 'params': params or {}})))
        while True:
            f = self._baca()
            d = json.loads(f)
            if d.get('id') == self.n:
                return d

    def _baca(self):
        b = self.s.recv(2)
        if not b:
            raise EOFError('socket tutup')
        n = b[1] & 0x7F
        if n == 126:
            n = int.from_bytes(self.s.recv(2), 'big')
        elif n == 127:
            n = int.from_bytes(self.s.recv(8), 'big')
        d = b''
        while len(d) < n:
            d += self.s.recv(n - len(d))
        return d.decode(errors='replace')

    def tutup(self):
        try:
            self.s.close()
        except Exception:
            pass


def data_csv(nama_berkas: str) -> str:
    import numpy as np
    rng = np.random.default_rng(77)
    n = 400
    Xa = rng.normal(size=n)
    Za = rng.normal(size=n)
    Zb = 0.75 * Za + rng.normal(scale=0.6, size=n)
    Ya = (0.20*Xa + 0.20*Za + 0.20*Zb + 0.35*Xa*Za
          + rng.normal(scale=0.9, size=n))
    hdr = ['X1a', 'X1b', 'Z1a', 'Z1b', 'Z2a', 'Z2b', 'Y1a', 'Y1b']
    b = [','.join(hdr)]
    for i in range(n):
        b.append(','.join(str(round(float(v[i]), 4)) for v in
                          (Xa, Xa, Za, Za, Zb, Zb, Ya, Ya)))
    with open(nama_berkas, 'w') as f:
        f.write('\n'.join(b) + '\n')
    return nama_berkas


def main() -> int:
    try:
        with urllib.request.urlopen(f'{CDP}/json/version', timeout=8):
            pass
    except Exception as e:
        print(f'  ⏭️  Chrome CDP tak hidup ({e}) — prasarana, bukan mesin')
        return 77

    try:
        with urllib.request.urlopen(urllib.request.Request(
                f'{CDP}/json/new?about:blank', method='PUT'), timeout=20) as r:
            baru = json.load(r)
    except Exception as e:
        print(f'  ❌ tak bisa buka tab: {e}')
        return 1

    tab = None
    try:
        tab = Tab(baru['webSocketDebuggerUrl'])
        tab.kirim('Page.enable')
        tab.kirim('Runtime.enable')
        tab.kirim('Page.navigate', {'url': URL})
        time.sleep(6)
        got = nilai(tab.kirim('Runtime.evaluate',
                              {'expression': 'location.href',
                               'returnByValue': True}))
        catat('klinik' in (got or ''), '/klinik termuat', str(got))
        if 'klinik' not in (got or ''):
            raise RuntimeError('halaman tidak termuat')

        # ── 1. Unggah berkas sungguhan (DOM.setFileInputFiles) ──
        berkas = data_csv('/tmp/uji_halaman_moderasi.csv')
        doc = tab.kirim('DOM.getDocument', {'depth': -1})
        root = doc['result']['root']['nodeId']
        node = tab.kirim('DOM.querySelector',
                         {'nodeId': root, 'selector': 'input[type=file]'})
        nid = node['result']['nodeId']
        catat(nid > 0, 'kotak unggah ADA', f'nodeId={nid}')
        tab.kirim('DOM.setFileInputFiles', {'nodeId': nid,
                                            'files': [berkas]})
        time.sleep(9)

        # ── 2. Apakah baris peran muncul? `data-kolom` ada di <select>. ──
        jml = nilai(tab.kirim('Runtime.evaluate', {
            'expression': 'document.querySelectorAll('
                          '"select.pilih-peran[data-kolom]").length',
            'returnByValue': True}))
        catat((jml or 0) >= 8, 'baris peran muncul setelah unggah',
              f'baris={jml}')
        if not (jml or 0):
            raise RuntimeError('daftar peran kosong')

        # ── 3. Tandai peran: X1, Z1, Z2, Y1 ──
        js = ('(() => {'
              'const peta = {X1a:"X1",X1b:"X1",Z1a:"Z1",Z1b:"Z1",'
              'Z2a:"Z2",Z2b:"Z2",Y1a:"Y1",Y1b:"Y1"};'
              'let n = 0;'
              'document.querySelectorAll("select.pilih-peran[data-kolom]")'
              '.forEach(sel => {'
              '  const kol = sel.getAttribute("data-kolom");'
              '  if (peta[kol]) { sel.value = peta[kol];'
              '    sel.dispatchEvent(new Event("change", {bubbles:true}));'
              '    n++; }'
              '});'
              'return n;})()')
        ditandai = nilai(tab.kirim('Runtime.evaluate',
                                   {'expression': js,
                                    'returnByValue': True}))
        catat((ditandai or 0) == 8, 'peran ditandai (8 kolom)',
              f'ditandai={ditandai}')

        # ── 4. Tekan tombol periksa ──
        tekan = nilai(tab.kirim('Runtime.evaluate', {
            'expression': ('(() => {const b = document.querySelector('
                           '"#tombol-periksa, #btn-periksa, '
                           '[data-tombol=periksa]");'
                           'if(!b) return "tidak ada"; b.click();'
                           'return "diklik";})()'),
            'returnByValue': True}))
        catat(tekan == 'diklik', 'tombol periksa DIKLIK', str(tekan))
        time.sleep(16)

        # ── 5. Baca hasil dari halaman ──
        teks = nilai(tab.kirim('Runtime.evaluate', {
            'expression': 'document.body.innerText',
            'returnByValue': True})) or ''
        ada_mod = ('memoderasi' in teks.lower()
                   or 'memperkuat' in teks.lower()
                   or 'melemahkan' in teks.lower())
        catat(ada_mod, 'kartu MODERASI muncul di halaman',
              f'panjang teks={len(teks)}')

        catat('Z1' in teks and 'Z2' in teks, 'Z1 & Z2 disebut di hasil',
              f'Z1={"Z1" in teks} Z2={"Z2" in teks}')

        catat('dikendalikan' in teks.lower(),
              'tulisan "dikendalikan" muncul (Opsi A sampai halaman)')

        print()
        for p in pesan:
            print(p)
        print()
        print(f'  {lulus} LULUS / {gagal} GAGAL')
        return 1 if gagal else 0
    except Exception as e:
        print()
        for p in pesan:
            print(p)
        print(f'  ❌ galat: {type(e).__name__}: {e}')
        return 1
    finally:
        if tab is not None:
            tab.tutup()
        try:
            urllib.request.urlopen(
                f'{CDP}/json/close/{baru["id"]}', timeout=5).read()
        except Exception:
            pass


if __name__ == '__main__':
    sys.exit(main())
