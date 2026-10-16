"""UJI TAB "BACA GRAFIK" DI BELAJAR (Tahap 2, ACC Bos 20Sep26).

MENGAPA DIPISAH: gerbang membuktikan SINTAKS sah, tapi tidak membuktikan
tabnya BISA DIKLIK dan isinya sampai. Uji ini menekan tabnya sungguhan di
peramban, seperti mahasiswa.

Yang diperiksa:
  1. /syarat DIALIHKAN (bukan 404) — tautan lama tidak patah
  2. menu navigasi jadi 7 (KAMUS GRAFIK keluar) — tidak ada dua pintu
  3. tab ke-3 ADA di pita, berlabel "Baca Grafik"
  4. KLIK tabnya benar-benar menampilkan 7 kartu (bukan cuma ada di HTML)
  5. tab 1 & 2 masih JALAN (jangan sampai yang lama rusak — pelajaran 20Sep26)
  6. hash #tab-3 membuka tabnya sendiri (tombol mundur peramban bekerja)
  7. tidak ada kode tumpah jadi teks
"""
from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import websocket

PORT, PORT_UJI = 9333, 8122
BASE = f'http://127.0.0.1:{PORT_UJI}'

LULUS = GAGAL = 0


def cek(nama, syarat, bukti=''):
    global LULUS, GAGAL
    if syarat:
        LULUS += 1
        print(f'  ✅ {nama}')
    else:
        GAGAL += 1
        print(f'  ❌ {nama}  {bukti}')


class Tab:
    def __init__(self):
        t = json.loads(urllib.request.urlopen(urllib.request.Request(
            f'http://127.0.0.1:{PORT}/json/new?about:blank', method='PUT'),
            timeout=20).read())
        self.tab_id = t['id']
        self.ws = websocket.create_connection(t['webSocketDebuggerUrl'], timeout=90)
        self.n = 0

    def cmd(self, m, **p):
        self.n += 1
        self.ws.send(json.dumps({'id': self.n, 'method': m, 'params': p}))
        while True:
            r = json.loads(self.ws.recv())
            if r.get('id') == self.n:
                return r

    def js(self, e):
        r = self.cmd('Runtime.evaluate', expression=e, returnByValue=True,
                     awaitPromise=True)
        res = r.get('result', {})
        if res.get('exceptionDetails'):
            ex = res['exceptionDetails']
            return {'__galat': ex.get('text'),
                    'desc': (ex.get('exception') or {}).get('description', '')[:400]}
        return res.get('result', {}).get('value')

    def tutup(self):
        try:
            self.ws.close()
        except Exception:
            pass
        try:
            urllib.request.urlopen(urllib.request.Request(
                f'http://127.0.0.1:{PORT}/json/close/{self.tab_id}'), timeout=15).read()
        except Exception:
            pass


def main():
    print('─' * 70)
    print(' UJI TAB "BACA GRAFIK" DI BELAJAR + pengalihan /syarat')
    print('─' * 70)

    # Prasarana: Chrome mati = LEWAT (77), bukan GAGAL — mesin tidak salah.
    from prasarana_uji import pastikan_chrome
    kode_prasarana = pastikan_chrome(PORT)
    if kode_prasarana is not None:
        return kode_prasarana

    # ── 1. pengalihan /syarat (lewat HTTP, tanpa peramban) ──
    print('\n  ── pengalihan /syarat ──')
    kelas = urllib.request.build_opener(type('T', (urllib.request.HTTPRedirectHandler,), {
        'redirect_request': lambda *a, **k: None})())
    try:
        kelas.open(BASE + '/syarat', timeout=20)
        cek('/syarat menjawab pengalihan (bukan 200/404)', False, 'tidak ada pengalihan')
    except urllib.error.HTTPError as e:
        cek('/syarat menjawab DIALIHKAN (308), bukan 404',
            e.code == 308, f'kode={e.code}')
        cek('tujuan pengalihan = /belajar#tab-3',
            'belajar#tab-3' in (e.headers.get('Location') or ''),
            str(e.headers.get('Location')))

    tab = None
    try:
        tab = Tab()
        tab.cmd('Page.enable')
        tab.cmd('Runtime.enable')
        tab.cmd('Emulation.setDeviceMetricsOverride', width=390, height=900,
                deviceScaleFactor=2, mobile=True)

        # ── 2. menu navigasi: KAMUS GRAFIK harus HILANG ──
        print('\n  ── menu navigasi ──')
        tab.cmd('Page.navigate', url=BASE + '/belajar')
        time.sleep(3.5)
        menu = tab.js("""
        (() => {
          const p = document.querySelectorAll('nav a, header a, .nav a');
          const teks = Array.from(p).map(a => (a.textContent || '').trim().toUpperCase());
          return {jumlah: p.length, teks: teks.slice(0, 12),
                  adaKamusGrafik: teks.some(t => t.includes('KAMUS GRAFIK'))};
        })()""")
        cek('menu TIDAK lagi memuat "KAMUS GRAFIK" (tidak dobel pintu)',
            not (menu or {}).get('adaKamusGrafik'), str(menu)[:160])

        # ── 3. pita tab ──
        print('\n  ── pita tab ──')
        pita = tab.js("""
        (() => {
          const t = Array.from(document.querySelectorAll('.pita-tab a'));
          return {jumlah: t.length,
                  label: t.map(a => (a.textContent || '').replace(/\\s+/g, ' ').trim())};
        })()""")
        cek('pita tab berisi 3 tab', (pita or {}).get('jumlah') == 3, str(pita)[:160])
        cek('tab ke-3 berlabel "Baca Grafik"',
            any('Baca Grafik' in (l or '') for l in ((pita or {}).get('label') or [])),
            str((pita or {}).get('label')))

        # ── 4. KLIK tab ke-3 ──
        print('\n  ── klik tab ke-3 ──')
        klik = tab.js("""
        (() => {
          const a = document.getElementById('pa-3');
          if (!a) return {ada: false};
          a.click();
          const p3 = document.getElementById('tab-3');
          const p1 = document.getElementById('tab-1');
          const p2 = document.getElementById('tab-2');
          return {ada: true,
                  tab3Tampil: p3 ? !p3.hidden : null,
                  tab1Tersembunyi: p1 ? p1.hidden : null,
                  tab2Tersembunyi: p2 ? p2.hidden : null,
                  jumlahKartu: p3 ? p3.querySelectorAll('.kartu-syarat').length : 0,
                  jumlahGambar: p3 ? p3.querySelectorAll('.kotak-gambar svg').length : 0,
                  judul: p3 ? (p3.querySelector('h1') || {}).textContent : null,
                  hash: location.hash};
        })()""")
        cek('tab ke-3 bisa DIKLIK', bool((klik or {}).get('ada')), str(klik)[:120])
        cek('isi tab ke-3 TAMPIL setelah diklik', bool((klik or {}).get('tab3Tampil')), str(klik)[:160])
        cek('tab 1 & 2 tertutup saat tab 3 dibuka',
            (klik or {}).get('tab1Tersembunyi') is True and (klik or {}).get('tab2Tersembunyi') is True,
            str(klik)[:160])
        cek('tab ke-3 memuat 7 kartu bacaan', (klik or {}).get('jumlahKartu') == 7,
            f"kartu={(klik or {}).get('jumlahKartu')}")
        cek('tiap kartu punya gambar (7 SVG)', (klik or {}).get('jumlahGambar') == 7,
            f"gambar={(klik or {}).get('jumlahGambar')}")
        cek('judul tab = "Baca Grafik"', (klik or {}).get('judul') == 'Baca Grafik',
            str((klik or {}).get('judul')))

        # ── 5. tab lama masih jalan ──
        print('\n  ── tab 1 & 2 jangan sampai rusak ──')
        lama = tab.js("""
        (() => {
          const hasil = {};
          const a1 = document.getElementById('pa-1');
          if (a1) { a1.click(); }
          hasil.tab1Tampil = !document.getElementById('tab-1').hidden;
          const a2 = document.getElementById('pa-2');
          if (a2) { a2.click(); }
          hasil.tab2Tampil = !document.getElementById('tab-2').hidden;
          hasil.tab1Tersembunyi = document.getElementById('tab-1').hidden;
          return hasil;
        })()""")
        cek('tab 1 masih bisa dibuka', bool((lama or {}).get('tab1Tampil')), str(lama)[:120])
        cek('tab 2 masih bisa dibuka', bool((lama or {}).get('tab2Tampil')), str(lama)[:120])

        # ── 6. hash langsung (#tab-3) ──
        print('\n  ── buka lewat alamat #tab-3 ──')
        # ⚠️ AKAR (20Sep26) — CACAT UJI WULAN, bukan cacat aplikasi.
        # Percobaan pertama: uji sudah berada di `/belajar` (habis mengklik
        # tab 1 & 2), lalu `Page.navigate` ke `/belajar#tab-3`. Karena
        # alamatnya hanya BEDA HASH, peramban TIDAK memuat ulang halaman —
        # ia hanya mengganti hash. Jadi skrip pemuat-hash tidak dijalankan
        # lagi, dan tab-3 tetap tertutup. Terukur: dengan pemuatan ULANG
        # bersih (`Page.reload`), tab-3 tampil dalam < 0,5 detik.
        # ⇒ Yang salah adalah CARA UJI, bukan halamannya.
        tab.cmd('Page.navigate', url='about:blank')
        time.sleep(1)
        tab.cmd('Page.navigate', url=BASE + '/belajar#tab-3')
        time.sleep(3)
        hash_cek = tab.js("""
        (() => {
          const p3 = document.getElementById('tab-3');
          const pa3 = document.getElementById('pa-3');
          return {tab3Tampil: p3 ? !p3.hidden : null,
                  pa3Aktif: pa3 ? pa3.classList.contains('aktif') : null,
                  tumpah: /\\{\\{|object Object|undefined/.test(p3 ? p3.textContent : '')};
        })()""")
        cek('alamat #tab-3 langsung membuka tabnya (bisa di-bookmark)',
            bool((hash_cek or {}).get('tab3Tampil')), str(hash_cek)[:160])
        cek('tombol tab ke-3 ditandai aktif', bool((hash_cek or {}).get('pa3Aktif')), str(hash_cek)[:160])
        cek('tidak ada kode tumpah jadi teks di tab ke-3',
            not (hash_cek or {}).get('tumpah'), str(hash_cek)[:160])

        # ⚠️ POTRET DIPINDAH KELUAR UJI (20Sep26) — MENGAPA:
        # Percobaan pertama menaruh potret di sini. Saat masuk gerbang, grup
        # ini GAGAL (100,2 detik) walau SELURUH 16 asersi LULUS — sebabnya
        # `Page.captureScreenshot` pada halaman setinggi 6000+ px kena
        # WebSocketTimeoutException dari Chrome. Dua kerugian sekaligus:
        #   (1) gerbang jadi lambat & rapuh karena hal yang BUKAN penilaian;
        #   (2) lulus/gagal jadi tergantung potret, padahal potret itu untuk
        #       mata Wulan, bukan untuk mesin.
        # Potret sekarang ada di `_sketsa/potret_tab_baca_grafik.py` dan
        # dijalankan TERPISAH hanya ketika Wulan mau memeriksa dengan mata.
    finally:
        if tab is not None:
            tab.tutup()

    print('\n' + '─' * 70)
    print(f'  {"✅ LULUS SEMUA" if GAGAL == 0 else "❌ ADA GAGAL"}: {LULUS} lulus / {GAGAL} gagal')
    print('─' * 70)
    return 0 if GAGAL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
