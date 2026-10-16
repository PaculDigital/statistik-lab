#!/usr/bin/env python3
"""UJI NORMALITAS + PINTASAN di HALAMAN NYATA (20Sep26).

MENGAPA BERKAS INI ADA (dan bukan cuma gerbang lama):
  Gerbang yang ada menguji HALAMAN SATU-SATU, tapi belum ada yang menguji
  KARTU NORMALITAS: apakah tombolnya muncul, apakah slidernya benar mendapat
  rentang −100…+100 (sementara istilah lain TETAP 0…100), apakah gambar
  histogramnya benar-benar berubah, dan apakah tombol pintasan menyala.

  Tanpa uji ini, "sudah kelihatan benar" = tebakan.

CARA JALAN: .venv/bin/python uji_normalitas.py
KELUAR 0 = LULUS.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import websocket

DIR = Path(__file__).resolve().parent
CHROME = ('/opt/data/home/.cloakbrowser/'
          'chromium-151.0.7922.108.6-pro/chrome')
PORT = 9333
# ⚠️ AKAR (20Sep26) — MENGAPA SERVER DIJALANKAN SENDIRI, BUKAN PAKAI
# KONTANER PRODUKSI:
#   Wulan berjalan DI DALAM kontainer Docker (terukur: hostname 68d027889611,
#   /.dockerenv ada). Jadi `127.0.0.1:8120` dari sini menunjuk ke DALAM
#   kontainer Wulan sendiri — BUKAN ke host tempat aplikasi dipublikasikan.
#   Terukur: curl 127.0.0.1:8120 → 000, port 8120 tidak listening di sini.
#   Itu juga sebabnya gerbang lama (gerbang_kode_tumpah.py) menjalankan
#   server uji SENDIRI di port 8121 dari berkas yang akan di-deploy: menguji
#   BERKAS, bukan kontainer yang entah sudah diperbarui atau belum.
#   Menguji kontainer produksi juga SALAH UKUR — bisa saja ia masih memuat
#   kode lama, sehingga uji lulus/gagal karena sebab yang keliru.
PORT_UJI = 8122
URL = f'http://127.0.0.1:{PORT_UJI}/belajar'

LULUS = 0
GAGAL = 0


def cek(nama: str, syarat: bool, ket: str = '') -> None:
    global LULUS, GAGAL
    if syarat:
        LULUS += 1
        print(f'  ✅ {nama}' + (f'  ({ket})' if ket else ''))
    else:
        GAGAL += 1
        print(f'  ❌ {nama}' + (f'  ({ket})' if ket else ''))


class Tab:
    """Sambungan CDP ke Chrome headless — pola disalin dari potret.py.

    ⚠️ AKAR (20Sep26): cara Wulan yang LAMA (membuka /json/new?about:blank
    lewat urllib, lalu menyambung) GAGAL — 'Chrome CDP tidak siap' walau
    Chrome hidup. Yang BENAR (terbukti di potret.py): TUNGGU sampai
    /json/version menjawab, baru buka tab baru dengan METHOD PUT (bukan GET).
    """

    def __init__(self, port: int):
        self.port = port
        self.ws = None
        self.n = 0

    def _tunggu_chrome(self) -> str:
        for _ in range(40):
            try:
                with urllib.request.urlopen(
                        f'http://127.0.0.1:{self.port}/json/version',
                        timeout=3) as r:
                    return json.loads(r.read())['webSocketDebuggerUrl']
            except Exception:
                time.sleep(0.5)
        raise RuntimeError(f'Chrome CDP di :{self.port} tidak siap')

    def buka(self) -> None:
        self._tunggu_chrome()
        # ⚠️ AKAR (20Sep26) — JANGAN menutup SEMUA tab di sini.
        # Dulu kode ini menutup setiap tab lama dengan alasan "tab yatim bikin
        # ConnectionResetError". SALAH — terukur: `uji_sub_regresi.py`
        # (gerbang lain, Chrome :9333 sama) MENSYARATKAN minimal 1 tab
        # sudah ada; kalau kita tutup semua → dia gagal "tidak ada tab".
        # Jalan benar: tutup HANYA tab milik kita sendiri (di `tutup()`),
        # dan buka tab BARU untuk diri sendiri.
        req = urllib.request.Request(f'http://127.0.0.1:{self.port}/json/new',
                                     method='PUT')
        with urllib.request.urlopen(req, timeout=20) as r:
            kosong = json.loads(r.read().decode())
        self.ws = websocket.create_connection(
            kosong['webSocketDebuggerUrl'], timeout=30)
        self.tab_id = kosong.get('id')          # untuk menutup tab ini nanti

    def tutup(self) -> None:
        """Tutup tab MILIK UJI INI saja — Chrome-nya JANGAN dimatikan.

        ⚠️ AKAR (20Sep26): Chrome :9333 dipakai BERSAMA gerbang lain
        (`uji_sub_regresi.py`). Mematikan Chrome-nya = merusak gerbang lain
        (terukur: 2 grup GAGAL PALSU). Yang boleh kita lakukan cuma menutup
        tab yang KITA buka, supaya tidak menumpuk jadi "tab yatim" yang
        membuat sambungan CDP berikutnya putus.
        """
        if getattr(self, 'ws', None) is not None:
            try:
                self.ws.close()
            except Exception:
                pass
            self.ws = None
        tid = getattr(self, 'tab_id', None)
        if tid:
            try:
                urllib.request.urlopen(
                    f'http://127.0.0.1:{self.port}/json/close/{tid}',
                    timeout=4).read()
            except Exception:
                pass
            self.tab_id = None

    def kirim(self, method: str, **params):
        self.n += 1
        mid = self.n
        self.ws.send(json.dumps({'id': mid, 'method': method, 'params': params}))
        while True:
            pesan = json.loads(self.ws.recv())
            if pesan.get('id') == mid:
                return pesan

    def js(self, expr: str):
        r = self.kirim('Runtime.evaluate', expression=expr,
                       returnByValue=True, awaitPromise=True)
        hasil = r.get('result', {})
        if 'exceptionDetails' in hasil:
            return {'__galat__': str(hasil['exceptionDetails'])[:300]}
        return hasil.get('result', {}).get('value')


def _cdp_hidup(port: int) -> bool:
    """Chrome CDP di `port` benar-benar menjawab? (bukan cuma 'ada proses')."""
    try:
        with urllib.request.urlopen(
                f'http://127.0.0.1:{port}/json/version', timeout=4) as r:
            return r.status == 200
    except Exception:
        return False


def _server_hidup(port: int) -> bool:
    try:
        return urllib.request.urlopen(
            f'http://127.0.0.1:{port}/health', timeout=3).status == 200
    except Exception:
        return False


def _nyalakan_server() -> 'subprocess.Popen | None':
    """Jalankan server uji SENDIRI dari BERKAS yang akan di-deploy.

    ⚠️ AKAR (20Sep26): dulu penyiapan server ada di BERKAS TERPISAH
    (`_sketsa/jalankan_uji_normalitas.py`). Akibatnya, begitu `uji_normalitas.py`
    dimasukkan ke gerbang, ia menguji `URL` yang TIDAK ADA yang melayani →
    halaman kosong → "Tombol kamus berjumlah 8 (dapat 0)" = GAGAL PALSU.
    Perbaikan di akar: uji ini MENYIAPKAN DIRINYA SENDIRI, supaya bisa
    dipanggil dari mana saja (gerbang, terminal, cron) tanpa pembungkus.
    """
    if _server_hidup(PORT_UJI):
        print(f'   (server uji sudah jalan di :{PORT_UJI})')
        return None
    env = dict(os.environ, PORT=str(PORT_UJI))
    srv = subprocess.Popen(
        [sys.executable, '-m', 'uvicorn', 'app.main:app',
         '--host', '127.0.0.1', '--port', str(PORT_UJI),
         '--log-level', 'warning'],
        cwd=str(DIR), env=env,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for i in range(40):
        if _server_hidup(PORT_UJI):
            print(f'   server uji siap di :{PORT_UJI} setelah {i}s')
            return srv
        if srv.poll() is not None:
            print('   ❌ server uji mati saat start')
            return srv
        time.sleep(1)
    print('   ❌ server uji tidak pernah sehat')
    return srv


def main() -> int:
    print('=' * 74)
    print(' UJI NORMALITAS + PINTASAN — halaman nyata /belajar')
    print('=' * 74)

    # ⚠️ AKAR (20Sep26) — JANGAN MENYALAKAN CHROME SENDIRI DARI SINI.
    # Tiga cara dicoba, TIGA-TIGANYA GAGAL (jangan ulang):
    #   (a) `pkill -f 'remote-debugging-port=9341'` → mematikan SHELL sendiri
    #       (pola ada di dalam baris perintah shell) + kena Chrome tetangga;
    #   (b) `subprocess.Popen(...)` + `--user-data-dir` → Chrome keluar sendiri
    #       (dbus/GLib-GIO-CRITICAL: "g_settings_schema_source_lookup" gagal);
    #   (c) `nohup ... &` dari shell → CDP sempat "DevTools listening on
    #       ws://...", lalu MATI begitu shell pemanggil selesai.
    # Terukur: Chrome 9333 dan 9444 yang BERTAHAN punya PPID = 1 (di-reparent
    # ke init) sebab dijalankan lewat `terminal(background=true)` Hermes.
    # ⇒ CARA BENAR: PAKAI Chrome 9333 yang SUDAH HIDUP (sama seperti
    #   `uji_sub_regresi.py` yang sudah terbukti jalan di dalam gerbang).
    #   Kalau 9333 tidak hidup → uji ini GAGAL dengan pesan JELAS, bukan
    #   diam-diam menguji sesuatu yang lain.
    # Prasarana: Chrome mati = LEWAT (77), bukan GAGAL — mesin tidak salah.
    # (Pesan jelas + perintah menyalakan ada di prasarana_uji.pesan_chrome)
    from prasarana_uji import pastikan_chrome
    kode_prasarana = pastikan_chrome(PORT)
    if kode_prasarana is not None:
        return kode_prasarana

    # Server uji: jalankan SENDIRI dari berkas yang akan di-deploy.
    srv = _nyalakan_server()
    if not _server_hidup(PORT_UJI):
        print(f'  ❌ Server uji :{PORT_UJI} tidak sehat — uji dibatalkan')
        return 1

    # ⚠️ `tab` disiapkan SEBELUM `try` supaya `finally` tidak meledak kalau
    # `Tab.buka()` sendiri yang gagal (dulu: NameError menutupi galat asli).
    tab = None
    try:
        tab = Tab(PORT)
        tab.buka()
        tab.kirim('Page.enable')
        tab.kirim('Runtime.enable')
        tab.kirim('Page.navigate', url=URL)
        time.sleep(4)

        # tangkap galat JS
        galat = tab.js("""(() => {
          const e = window.__galatJs || [];
          return JSON.stringify(e);
        })()""")
        print(f'\n  galat JS tertangkap: {galat}')

        # ── 1. PANEL KAMUS ADA & TOMBOL NORMALITAS ADA ──────────────────
        print('\n── 1. Kartu & tombol ──')
        d = tab.js("""(() => {
          const tom = [...document.querySelectorAll('.kamus-tombol')];
          return JSON.stringify({
            jumlah: tom.length,
            daftar: tom.map(b => (b.dataset.k || '?') + ':' + b.textContent.trim()),
            biji: (document.querySelector('.pita-tab a .biji') || {}).textContent
          });
        })()""")
        info = json.loads(d)
        cek('Tombol kamus berjumlah 8', info['jumlah'] == 8, f"dapat {info['jumlah']}")
        cek('Tombol normalitas ada', any(x.startswith('normalitas:')
                                         for x in info['daftar']))
        cek('Judul uji t sudah "Masalah uji t"',
            any('masalah uji t' in x.lower() for x in info['daftar']),
            [x for x in info['daftar'] if 'ujit' in x][0] if any(
                'ujit' in x for x in info['daftar']) else '-')
        cek('Biji pita "Materi & Kamus" = 8', info['biji'] == '8',
            f"dapat {info['biji']}")

        # ── 2. NORMALITAS: SLIDER DAPAT RENTANG −100…+100 ───────────────
        print('\n── 2. Normalitas (klik tombol, periksa slider) ──')
        tab.js("""(() => {
          const b = [...document.querySelectorAll('.kamus-tombol')]
                     .find(x => x.dataset.k === 'normalitas');
          if (b) b.click();
          return true;
        })()""")
        time.sleep(0.6)
        n = json.loads(tab.js("""(() => {
          const s = document.getElementById('slider');
          const g = document.getElementById('grafik');
          return JSON.stringify({
            min: s.min, max: s.max, nilai: s.value,
            judul: document.getElementById('judul').textContent,
            batang: g.querySelectorAll('rect').length,
            pita: document.getElementById('pita-hasil').textContent,
            pesan: document.getElementById('pesan-isi').innerText.slice(0, 90),
            pintasanTersembunyi:
              document.getElementById('pintasan-baris').hidden
          });
        })()"""))
        cek('Judul panel = "Normalitas"', n['judul'] == 'Normalitas', n['judul'])
        cek('Slider min = -100', n['min'] == '-100', n['min'])
        cek('Slider max = 100', n['max'] == '100', n['max'])
        cek('Nilai awal = 0 (lonceng)', n['nilai'] == '0', n['nilai'])
        cek('Histogram tergambar (>10 batang)', n['batang'] > 10,
            f"{n['batang']} batang")
        cek('Pita = "Normal"', n['pita'] == 'Normal', n['pita'])
        cek('Kalimat penegas muncul',
            'justru ini yang bagus' in n['pesan'], n['pesan'][:60])
        cek('Tombol pintasan TERSEMBUNYI di normalitas',
            n['pintasanTersembunyi'] is True)

        # ── 3. GESER NORMALITAS: histogram berubah ──────────────────────
        print('\n── 3. Normalitas: geser kiri & kanan ──')
        for arah, nilai, harus in [('kanan', 100, 'positif'),
                                   ('kiri', -100, 'negatif')]:
            r = json.loads(tab.js(f"""(() => {{
              const s = document.getElementById('slider');
              s.value = {nilai};
              s.dispatchEvent(new Event('input', {{bubbles: true}}));
              return JSON.stringify({{
                batang: document.getElementById('grafik').querySelectorAll('rect').length,
                pita: document.getElementById('pita-hasil').textContent,
                pesan: document.getElementById('pesan-isi').innerText.slice(0, 100)
              }});
            }})()"""))
            time.sleep(0.3)
            cek(f'Geser {arah} ({nilai}) → histogram tetap tergambar',
                r['batang'] > 5, f"{r['batang']} batang")
            cek(f'Geser {arah} → pita berubah jadi "Jauh dari normal"',
                r['pita'] == 'Jauh dari normal', r['pita'])

        # ── 4. HETERO: PINTASAN MUNCUL + SLIDER BALIK 0…100 ─────────────
        print('\n── 4. Hetero: tombol pintasan & rentang slider ──')
        h = json.loads(tab.js("""(() => {
          const b = [...document.querySelectorAll('.kamus-tombol')]
                     .find(x => x.dataset.k === 'hetero');
          if (b) b.click();
          const s = document.getElementById('slider');
          return JSON.stringify({
            min: s.min, max: s.max, nilai: s.value,
            judul: document.getElementById('judul').textContent,
            pintasanTersembunyi:
              document.getElementById('pintasan-baris').hidden,
            sehatNyala: document.getElementById('pintasan-sehat').classList.contains('nyala'),
            pesan: document.getElementById('pesan-isi').innerText.slice(0, 90)
          });
        })()"""))
        time.sleep(0.4)
        cek('Judul panel = "Heteroskedastisitas"',
            h['judul'] == 'Heteroskedastisitas', h['judul'])
        cek('Slider min KEMBALI ke 0 (tidak rusak)', h['min'] == '0', h['min'])
        cek('Slider max KEMBALI ke 100 (tidak rusak)', h['max'] == '100', h['max'])
        cek('Tombol pintasan MUNCUL di hetero',
            h['pintasanTersembunyi'] is False)
        cek('Tombol "Contoh sehat" menyala saat nilai 0', h['sehatNyala'] is True)
        # ⚠️ KOREKSI UJI (20Sep26): Wulan semula menuntut nilai 0 di sini dan
        # menyalahkan aplikasi. SALAH — berkas ASLI sejak dulu memakai
        # `value="35"` (terbukti di cadangan_normalitas), jadi hetero memang
        # mulai di 35. Yang benar: uji harus menuntut 35, bukan 0.
        # Pelajaran: periksa perilaku ASLI dulu sebelum menuduh aplikasi rusak.
        cek('Nilai hetero kembali ke 35 (perilaku ASLI, bukan 0)',
            h['nilai'] == '35', h['nilai'])
        cek('Kalimat hetero di 35 = "mulai melebar" (bukan diklaim sehat)',
            'mulai melebar' in h['pesan'].lower(), h['pesan'][:70])

        # uji kalimat SEHAT dipisah: geser dulu ke 0 (keadaan sehat asli)
        hs = json.loads(tab.js("""(() => {
          document.getElementById('pintasan-sehat').click();
          return JSON.stringify({
            nilai: document.getElementById('slider').value,
            pesan: document.getElementById('pesan-isi').innerText.slice(0, 100)
          });
        })()"""))
        time.sleep(0.3)
        cek('Klik "Contoh sehat" → slider 0', hs['nilai'] == '0', hs['nilai'])
        cek('Kalimat "tidak ada corong — justru ini yang bagus" saat sehat',
            'tidak ada corong' in hs['pesan'].lower(), hs['pesan'][:80])

        # ── 5. KLIK TOMBOL SAKIT → slider lompat & gambar berubah ───────
        print('\n── 5. Klik tombol "Contoh sakit" ──')
        k = json.loads(tab.js("""(() => {
          document.getElementById('pintasan-sakit').click();
          const s = document.getElementById('slider');
          return JSON.stringify({
            nilai: s.value,
            titik: document.getElementById('grafik').querySelectorAll('circle').length,
            pita: document.getElementById('pita-hasil').textContent,
            sakitNyala: document.getElementById('pintasan-sakit').classList.contains('nyala'),
            sehatNyala: document.getElementById('pintasan-sehat').classList.contains('nyala'),
            pesan: document.getElementById('pesan-isi').innerText.slice(0, 100)
          });
        })()"""))
        time.sleep(0.4)
        cek('Slider lompat ke 100', k['nilai'] == '100', k['nilai'])
        cek('Grafik tergambar (>50 titik)', k['titik'] > 50, f"{k['titik']} titik")
        cek('Pita = "Bermasalah"', k['pita'] == 'Bermasalah', k['pita'])
        cek('Tombol "Contoh sakit" menyala', k['sakitNyala'] is True)
        cek('Tombol "Contoh sehat" TIDAK menyala', k['sehatNyala'] is False)
        cek('Kalimat ganti ke peringatan melebar',
            'bermasalah' in k['pesan'].lower(), k['pesan'][:70])

        # ── 6. ISTILAH LAMA TETAP SEHAT (jangan merusak yang sudah jalan) ─
        print('\n── 6. Istilah LAMA tetap utuh (uji tidak merusak) ──')
        lama = json.loads(tab.js("""(() => {
          const hasil = [];
          ['beta', 'pvalue', 'r2', 'vif', 'alpha'].forEach(k => {
            const b = [...document.querySelectorAll('.kamus-tombol')]
                       .find(x => x.dataset.k === k);
            if (!b) { hasil.push({k, ada: false}); return; }
            b.click();
            const s = document.getElementById('slider');
            hasil.push({k, ada: true, min: s.min, max: s.max,
                        pita: document.getElementById('pita-hasil').textContent,
                        pintasanTersembunyi:
                          document.getElementById('pintasan-baris').hidden});
          });
          return JSON.stringify(hasil);
        })()"""))
        time.sleep(0.5)
        for it in lama:
            cek(f"Istilah '{it['k']}' masih jalan", it.get('ada') is True)
            if it.get('ada'):
                cek(f"   slider '{it['k']}' = 0…100",
                    it['min'] == '0' and it['max'] == '100',
                    f"{it['min']}…{it['max']}")
                cek(f"   pita '{it['k']}' tidak kosong", bool(it['pita']), it['pita'])
                cek(f"   pintasan tersembunyi di '{it['k']}'",
                    it['pintasanTersembunyi'] is True)

        # ── 7. KARTU UJI t MASIH JALAN ──────────────────────────────────
        print('\n── 7. Kartu uji t tidak rusak ──')
        u = json.loads(tab.js("""(() => {
          const b = [...document.querySelectorAll('.kamus-tombol')]
                     .find(x => x.dataset.k === 'ujit');
          b.click();
          return JSON.stringify({
            kartuTampil: !document.getElementById('kartu-ujit').hidden,
            kotak: document.querySelectorAll('.ujit-pilih').length,
            barisTabel: document.querySelectorAll('.ujit-tabel tr').length
          });
        })()"""))
        time.sleep(0.5)
        cek('Kartu uji t TAMPIL saat diklik', u['kartuTampil'] is True)
        cek('Kotak hasil uji t = 5', u['kotak'] == 5, f"dapat {u['kotak']}")
        cek('Tabel sebab terisi', u['barisTabel'] > 3, f"{u['barisTabel']} baris")

        # ── 8. KODE TUMPAH (teks JS terlihat user) ──────────────────────
        print('\n── 8. Tidak ada kode bocor ke layar ──')
        bocor = json.loads(tab.js("""(() => {
          const t = document.body.innerText;
          const pola = ['function ', 'const ', 'document.getElementById',
                        '<strong>', '</div>', '${'];
          const ketemu = pola.filter(p => t.includes(p));
          return JSON.stringify(ketemu);
        })()"""))
        cek('Tidak ada kode JS/HTML bocor di teks halaman',
            len(bocor) == 0, str(bocor))

        # ── 9. MELUBER KELUAR LAYAR (lebar 390) ─────────────────────────
        print('\n── 9. Tidak meluber keluar layar (390px) ──')
        l = json.loads(tab.js("""(() => {
          return JSON.stringify({
            lebarHalaman: document.documentElement.scrollWidth,
            lebarLayar: window.innerWidth,
            meluber: [...document.querySelectorAll(
              '.pintasan-baris, .pintasan, .medan, .grafik, .papan')
            ].filter(e => e.getBoundingClientRect().right > window.innerWidth + 1)
             .map(e => e.className).slice(0, 5)
          });
        })()"""))
        cek('Halaman tidak bisa digeser ke samping',
            l['lebarHalaman'] <= l['lebarLayar'] + 1,
            f"{l['lebarHalaman']} ≤ {l['lebarLayar']}")
        cek('Tidak ada elemen meluber', len(l['meluber']) == 0, str(l['meluber']))

    finally:
        # ⚠️ JANGAN mematikan Chrome apa pun di sini. Chrome :9333 BUKAN milik
        # uji ini — ia dipakai bersama gerbang lain (uji_sub_regresi.py).
        # Yang kita lakukan cuma MENUTUP TAB yang kita buka (di Tab.tutup).
        if tab is not None:
            tab.tutup()
        # Server uji: matikan HANYA kalau KITA yang menyalakannya (srv != None).
        if srv is not None:
            srv.terminate()
            try:
                srv.wait(timeout=5)
            except Exception:
                srv.kill()

    print()
    print('=' * 74)
    print(f'  {LULUS} LULUS / {GAGAL} GAGAL')
    print('=' * 74)
    return 0 if GAGAL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
