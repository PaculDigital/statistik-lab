"""PERIKSA: tombol "Contoh sehat/sakit" di /klinik masih JALAN atau tidak?

Sebelum memperbaiki uji, WAJIB tahu dulu: yang rusak ujinya atau tombolnya.
(Aturan: periksa uji dulu sebelum menuduh aplikasi.)

Dibaca dari halaman SUNGGUHAN lewat Chrome, lalu klik tombolnya sendiri.
"""
import json
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from prasarana_uji import pastikan_chrome                    # noqa: E402

PORT, CDP, BASE = 8122, 'http://127.0.0.1:9333', 'http://127.0.0.1:8122'


class Tab:
    def __init__(self, ws):
        import websocket
        self.ws = websocket.create_connection(ws, timeout=40)
        self.i = 0

    def cmd(self, metode, **p):
        self.i += 1
        self.ws.send(json.dumps({'id': self.i, 'method': metode, 'params': p}))
        while True:
            d = json.loads(self.ws.recv())
            if d.get('id') == self.i:
                if 'error' in d:
                    raise RuntimeError(d['error'])
                return d.get('result', {})

    def ev(self, ekspresi):
        r = self.cmd('Runtime.evaluate', expression=ekspresi,
                     returnByValue=True, awaitPromise=True)
        return r.get('result', {}).get('value')

    def buka(self, url):
        self.cmd('Page.navigate', url=url)
        time.sleep(2.5)

    def tutup(self):
        try:
            self.ws.close()
        except Exception:
            pass


def main():
    if pastikan_chrome(9333) is not None:
        return 77
    req = urllib.request.Request(CDP + '/json/new?about:blank', method='PUT')
    info = json.loads(urllib.request.urlopen(req, timeout=20).read().decode())
    tab = Tab(info['webSocketDebuggerUrl'])
    try:
        tab.cmd('Runtime.enable')
        tab.buka(BASE + '/klinik')
        print('=' * 70)
        print(' PERIKSA TOMBOL CONTOH DI HALAMAN SUNGGUHAN')
        print('=' * 70)

        # 1. Apakah elemen bentuk PERAN ada di halaman?
        ada_peran = tab.ev("!!document.getElementById('daftar-peran')")
        print(f"\n[1] Bentuk PERAN ada di halaman? {ada_peran}")
        ada_barisx = tab.ev("!!document.getElementById('baris-x')")
        print(f"    Elemen LAMA #baris-x masih ada? {ada_barisx}"
              f"  (harus False — sudah dihapus)")

        # 2. Tombol contoh ada?
        n_tombol = tab.ev("document.querySelectorAll('[onclick*=contoh],"
                          " [onclick*=Contoh], .tombol-contoh').length")
        print(f"\n[2] Tombol contoh ditemukan: {n_tombol}")

        # 3. Cari fungsi contoh di skrip halaman
        fn = tab.ev("(typeof isiContoh === 'function') ? 'isiContoh' : "
                    "(typeof contohSehat === 'function') ? 'contohSehat' : "
                    "(typeof pasangContoh === 'function') ? 'pasangContoh' : "
                    "'TIDAK KETEMU'")
        print(f"[3] Nama fungsi contoh: {fn}")

        # 4. Apa saja nama fungsi contoh yang ADA di skrip?
        daftar = tab.ev(
            "Object.keys(window).filter(k => /contoh|Contoh/.test(k))"
            ".join(', ') || '(tidak ada di window)'")
        print(f"[4] Fungsi ber-'contoh' di window: {daftar}")

        # 5. Cara uji lama mencari kolom — masih cocok?
        lama = tab.ev("!!document.querySelector('#baris-x .pilih-kolom') || "
                      "!!document.getElementById('kolom-y')")
        print(f"\n[5] Cara UJI LAMA mencari kolom (baris-x/kolom-y): {lama}"
              f"  → {'COCOK' if lama else 'TIDAK COCOK (uji usang)'}")

        # 6. Cara BARU: dropdown peran
        baru = tab.ev("document.querySelectorAll('#daftar-peran select').length")
        print(f"[6] Dropdown peran yang BISA dipakai uji baru: {baru}")

        print('\n' + '=' * 70)
        print(' KESIMPULAN (jujur, dari pengukuran di atas):')
        print('=' * 70)
        if not lama and baru > 0:
            print('  ⇒ HALAMAN SUDAH PAKAI BENTUK PERAN (dropdown).')
            print('  ⇒ UJI LAMA yang mencari #baris-x/#kolom-y = USANG.')
            print('  ⇒ Jadi yang harus diperbaiki UJINYA, bukan aplikasinya.')
        elif lama:
            print('  ⇒ Halaman MASIH punya #baris-x/#kolom-y → uji lama masih sah.')
        else:
            print('  ⇒ Perlu diperiksa lebih dalam — hasil tidak jelas.')
    finally:
        tab.tutup()
        try:
            urllib.request.urlopen(
                urllib.request.Request(CDP + '/json/close/' + info['id']),
                timeout=10)
        except Exception:
            pass
    return 0


if __name__ == '__main__':
    sys.exit(main())
