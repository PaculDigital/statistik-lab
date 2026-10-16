"""UJI PINTU di halaman SUNGGUHAN — bukti Langkah 3 keputusan 21Sep26.

Yang diperiksa (semua lewat halaman HIDUP, bukan berkas):
  1. /kuantitatif  → kartu Regresi: ① Parsial (Sederhana) · ② Berganda
     (Parsial + Simultan) — dan TIDAK ada kartu "Berganda-berantai".
  2. /buat-data    → kartu ② berantai TIDAK TAMPIL (walau ada di HTML),
     di semua jumlah X (2..8) — sebab aturCara() dulu memunculkannya.
  3. Gambar kartu ② punya jalur SIKU (jalur simultan), kartu ① TIDAK.
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

PORT, PORT_UJI = 9333, 8122
BASE = f'http://127.0.0.1:{PORT_UJI}'
DIR = Path(__file__).resolve().parent
PY = DIR / '.venv' / 'bin' / 'python'

LULUS = GAGAL = 0


def cek(nama, syarat, bukti=''):
    global LULUS, GAGAL
    if syarat:
        LULUS += 1
        print(f'  ✅ {nama}')
    else:
        GAGAL += 1
        print(f'  ❌ {nama}  {bukti}')


def server_hidup():
    try:
        return urllib.request.urlopen(
            f'http://127.0.0.1:{PORT_UJI}/health', timeout=3).status == 200
    except Exception:
        return False


def siapkan_server():
    if server_hidup():
        return True
    os.environ['PORT'] = str(PORT_UJI)
    subprocess.Popen([str(PY), '-m', 'uvicorn', 'app.main:app',
                      '--host', '127.0.0.1', '--port', str(PORT_UJI),
                      '--log-level', 'warning'],
                     cwd=str(DIR), stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL)
    for _ in range(60):
        if server_hidup():
            return True
        time.sleep(0.5)
    return False


class Tab:
    """Tab BARU yang benar-benar bersih.

    ⚠️ JEBAKAN TERUKUR 21Sep26: `Tab()` versi pertama memakai tab yang sudah
    ada → URL-nya masih /kuantitatif dari uji sebelumnya, jadi `Page.navigate`
    tampak tidak jalan dan selector mengembalikan [] (kartu kosong).
    FIX: buat tab BARU dengan URL about:blank, lalu PASTIKAN sudah di
    about:blank sebelum navigate. Buktikan lewat location.href.
    """

    def __init__(self):
        # ⚠️ AKAR TERUKUR 21Sep26 (jebakan "TAB YATIM CDP"):
        #    Dulu Wulan mengira `/json/new?about:blank` selalu membuat tab
        #    BARU. Terbukti TIDAK: kalau ada tab nyangkut, Chrome membalas
        #    dengan tab LAMA itu — dan di sesi ini tab nyangkut berisi
        #    https://statistik.bikinaja.id/kuantitatif (domain PRODUKSI).
        #    Akibatnya Page.navigate "tidak jalan" & selector balik [] —
        #    tampak seperti aplikasi rusak, padahal uji yang salah tab.
        #    ATURAN (sama dengan pelajaran "Tab Yatim" proyek ini):
        #    kosongkan tab dulu, JANGAN pkill Chrome.
        self._bersihkan_tab()
        t = json.loads(urllib.request.urlopen(urllib.request.Request(
            f'http://127.0.0.1:{PORT}/json/new?about:blank', method='PUT'),
            timeout=20).read())
        self.tab_id = t['id']
        self.ws = websocket.create_connection(t['webSocketDebuggerUrl'],
                                              timeout=90)
        self.n = 0

    @staticmethod
    def _bersihkan_tab():
        """Tutup semua tab page yang nyangkut (tanpa mematikan Chrome)."""
        try:
            d = json.load(urllib.request.urlopen(
                f'http://127.0.0.1:{PORT}/json/list', timeout=8))
            for t in d:
                if t.get('type') == 'page':
                    try:
                        urllib.request.urlopen(
                            f'http://127.0.0.1:{PORT}/json/close/{t["id"]}',
                            timeout=8).read()
                    except Exception:
                        pass
            time.sleep(0.5)
        except Exception:
            pass

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
        if 'exceptionDetails' in res:
            return {'__galat': str(res['exceptionDetails'])[:300]}
        return res.get('result', {}).get('value')

    def ke(self, url, tunggu=4.0):
        """Navigate + BUKTIKAN halaman benar-benar pindah (jangan asumsi)."""
        self.cmd('Page.navigate', url=url)
        time.sleep(tunggu)
        aktual = self.js('location.href')
        return str(aktual or '').rstrip('/').endswith(url.rstrip('/'))

    def tutup(self):
        try:
            urllib.request.urlopen(urllib.request.Request(
                f'http://127.0.0.1:{PORT}/json/close/{self.tab_id}'),
                timeout=10).read()
        except Exception:
            pass
        try:
            self.ws.close()
        except Exception:
            pass


def main() -> int:
    print('─' * 70)
    print(' UJI PINTU — KARTU REGRESI DI HALAMAN SUNGGUHAN')
    print('─' * 70)
    # Prasarana: Chrome mati = LEWAT (77), bukan GAGAL — mesin tidak salah.
    from prasarana_uji import pastikan_chrome
    kode_prasarana = pastikan_chrome(PORT)
    if kode_prasarana is not None:
        return kode_prasarana
    if not siapkan_server():
        print(f'  ❌ server uji :{PORT_UJI} tidak bisa dinyalakan')
        return 1

    tab = None
    try:
        tab = Tab()
        tab.cmd('Page.enable')
        tab.cmd('Runtime.enable')

        # ══ 1. /buat-data: kartu cara ══
        # ⚠️ AKAR TERUKUR 21Sep26 (jebakan ke-4 di sesi ini, dan ini CACAT UJI):
        #    Uji lama membuka `/buat-data` POLOS. Padahal halaman itu SENGAJA
        #    `location.replace('/kuantitatif')` bila URL tidak memuat `?model=`
        #    (keputusan Bos 19Sep26 opsi 1B: user TIDAK ditebak-tebak modelnya).
        #    Akibatnya tab selalu berakhir di /kuantitatif dan selector
        #    mengembalikan [] — tampak seperti aplikasi rusak, padahal
        #    PERILAKU SENGAJA. ATURAN: uji pintu LEWAT JALUR NYATA user,
        #    artinya pakai ?model= seperti tautan kartu di /kuantitatif.
        URL_PINTU = BASE + '/buat-data?model=sederhana'
        pindah = tab.ke(URL_PINTU)
        cek('navigasi ke /buat-data?model=sederhana benar-benar terjadi',
            pindah, f"url sekarang: {tab.js('location.href')}")

        kartu = tab.js("""(() => {
          const semua = Array.from(document.querySelectorAll('.pilih-cara'));
          const info = semua.map(k => ({
            cara: k.dataset.cara,
            judul: (k.querySelector('.cara-judul')||{}).textContent?.trim() || '',
            tampil: !!(k.offsetParent !== null) && k.style.display !== 'none'
          }));
          return {jumlah: semua.length, info: info,
                  berantaiTampil: info.filter(k => k.cara==='berantai' && k.tampil).length};
        })()""")
        if isinstance(kartu, dict) and kartu.get('__galat'):
            cek('halaman /buat-data terbuka', False, json.dumps(kartu)[:250])
        else:
            cek('halaman /buat-data terbuka', True)
            print(f"     kartu: {json.dumps(kartu.get('info'), ensure_ascii=False)}")
            cek('kartu cara ditemukan di halaman', kartu.get('jumlah', 0) >= 3,
                str(kartu.get('jumlah')))
            cek('kartu "berantai" TIDAK TAMPIL (X=3 default)',
                kartu.get('berantaiTampil') == 0, str(kartu.get('berantaiTampil')))
            judul = {k['cara']: k['judul'] for k in kartu.get('info', [])}
            cek('kartu ① judulnya memuat "Parsial"',
                'Parsial' in judul.get('sederhana', ''), str(judul))
            cek('kartu ② judulnya memuat "Simultan"',
                'Simultan' in judul.get('berganda', ''), str(judul))

        # ══ 2. kartu berantai tetap tersembunyi di SEMUA jumlah X ══
        # ⚠️ id slider yang benar = #x-slider (bukan #x) — diukur dari HTML.
        ada_slider = tab.js("!!document.getElementById('x-slider')")
        cek('slider jumlah X (#x-slider) ADA di halaman', ada_slider is True)
        for nx in (2, 5, 8):
            r = tab.js(f"""(() => {{
              const s = document.getElementById('x-slider');
              if (!s) return {{__galat:'#x-slider tidak ketemu'}};
              s.value = {nx};
              s.dispatchEvent(new Event('input', {{bubbles:true}}));
              s.dispatchEvent(new Event('change', {{bubbles:true}}));
              const k = document.getElementById('cara-berantai-kartu');
              const tampil = k && k.offsetParent !== null && k.style.display !== 'none';
              return {{nx: {nx}, tampil: !!tampil,
                        gaya: k ? k.style.display : null}};
            }})()""")
            cek(f'kartu "berantai" TETAP tersembunyi di X={nx}',
                r.get('tampil') is False, str(r))

        # ══ 3. /kuantitatif: kartu model Regresi ══
        pindah2 = tab.ke(BASE + '/kuantitatif')
        cek('navigasi ke /kuantitatif benar-benar terjadi', pindah2,
            f"url sekarang: {tab.js('location.href')}")
        # buka panel sub-regresi (fungsi bukaSub milik halaman)
        # ⚠️ AKAR TERUKUR 21Sep26: tanda tangan yang BENAR = bukaSub(ev, nama)
        #    — versi pertama uji memanggil bukaSub('regresi') sehingga `ev`
        #    menerima string dan `nama` undefined → Uncaught di baris 1021.
        #    ATURAN: GREP tanda tangan fungsi sebelum memanggilnya.
        peta = tab.js("""(() => {
          if (typeof bukaSub === 'function') { bukaSub(null, 'regresi'); }
          const kartu = Array.from(document.querySelectorAll('#sub-regresi .kartu-pilih'));
          return {jumlah: kartu.length,
                  panelTerbuka: !document.getElementById('sub-regresi')?.hidden,
                  judul: kartu.map(k => (k.querySelector('.kartu-judul')||{}).textContent?.trim()),
                  tautan: kartu.map(k => k.getAttribute('href')),
                  adaBerantai: kartu.some(k => /berantai/i.test(k.textContent)),
                  adaSiku: kartu.map(k => !!(k.querySelector('path.garis-siku') || k.querySelector('path.garis-rantai'))),
                  teks: kartu.map(k => (k.textContent||'').replace(/\\s+/g,' ').trim().slice(0,90))};
        })()""")
        if isinstance(peta, dict) and peta.get('__galat'):
            cek('panel sub-regresi tampil', False, json.dumps(peta)[:250])
        else:
            print(f"     judul: {peta.get('judul')}")
            print(f"     tautan: {peta.get('tautan')}")
            cek('panel sub-regresi terbuka', peta.get('jumlah', 0) >= 2,
                str(peta.get('jumlah')))
            cek('kartu ① ada & memuat "Parsial"',
                any('Parsial' in (j or '') for j in peta.get('judul', [])),
                str(peta.get('judul')))
            cek('kartu ② ada & memuat "Simultan"',
                any('Simultan' in (j or '') for j in peta.get('judul', [])),
                str(peta.get('judul')))
            cek('kartu "Berganda-berantai" SUDAH TIDAK ADA di /kuantitatif',
                peta.get('adaBerantai') is False, str(peta.get('teks')))
            cek('tidak ada tautan ke ?model=berantai',
                not any('berantai' in (t or '') for t in peta.get('tautan', [])),
                str(peta.get('tautan')))
            cek('kartu ② punya jalur SIKU (tanda simultan)',
                True in (peta.get('adaSiku') or []), str(peta.get('adaSiku')))
    finally:
        if tab is not None:
            tab.tutup()

    print('\n' + '─' * 70)
    print(f'  {"✅ LULUS SEMUA" if GAGAL == 0 else "❌ ADA GAGAL"}: '
          f'{LULUS} lulus / {GAGAL} gagal')
    print('─' * 70)
    return 0 if GAGAL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
