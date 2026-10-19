"""UJI TABEL ANOVA DI HALAMAN SUNGGUHAN (bukan cuma fungsi).

Bukti Langkah 2 keputusan 21Sep26: uji F harus BENAR-BENAR TERLIHAT mahasiswa
di halaman /buat-data, bukan hanya benar di dalam fungsi Python.

⚠️ Aturan proven: uji WAJIB menyiapkan servernya sendiri (uvicorn lokal :8122).
⚠️ Jangan buka lewat file:// (CSS/JS tidak termuat) — pakai halaman HIDUP.
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
DIR = Path(__file__).resolve().parent.parent
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
    subprocess.Popen(
        [str(PY), '-m', 'uvicorn', 'app.main:app',
         '--host', '127.0.0.1', '--port', str(PORT_UJI), '--log-level', 'warning'],
        cwd=str(DIR), env=dict(os.environ),
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(60):
        if server_hidup():
            return True
        time.sleep(0.5)
    return False


class Tab:
    def __init__(self):
        t = json.loads(urllib.request.urlopen(urllib.request.Request(
            f'http://127.0.0.1:{PORT}/json/new?about:blank', method='PUT'),
            timeout=20).read())
        self.tab_id = t['id']
        self.ws = websocket.create_connection(t['webSocketDebuggerUrl'],
                                              timeout=90)
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
        if 'exceptionDetails' in res:
            return {'__galat': str(res['exceptionDetails'])[:200]}
        return res.get('result', {}).get('value')

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
    print(' UJI TABEL ANOVA DI HALAMAN SUNGGUHAN')
    print('─' * 70)

    # Prasarana: Chrome mati = LEWAT (77), bukan GAGAL — mesin tidak salah.
    from prasarana_uji import pastikan_chrome
    kode_prasarana = pastikan_chrome(PORT)
    if kode_prasarana is not None:
        return kode_prasarana

    if not siapkan_server():
        print(f'  ❌ server uji :{PORT_UJI} tidak bisa dinyalakan — dibatalkan')
        return 1

    tab = None
    try:
        tab = Tab()
        tab.cmd('Page.enable')
        tab.cmd('Runtime.enable')

        # ── prasyarat: fungsi tabelAnova ADA di halaman ──
        tab.cmd('Page.navigate', url=BASE + '/buat-data?model=berganda')
        time.sleep(4)
        ada = tab.js("typeof tabelAnova")
        cek('fungsi tabelAnova() ada di halaman', ada == 'function', str(ada))

        # ── jalankan mesin lewat API, lalu render hasilnya di halaman ──
        hasil = tab.js(f"""(async () => {{
          const r = await fetch('/api/buat-data', {{
            method: 'POST',
            headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify({{n:200, x:3, beta:[0.3,0.25,0.2],
              skala:5, alpha:0.85, mode:'presisi', cara:'berganda',
              kunci:'uji-anova', nama_x:['Harga','Promosi','Layanan']}})
          }});
          const d = await r.json();
          if (d.galat || d.detail) return {{__galat: JSON.stringify(d).slice(0,300)}};
          return {{cara: d.cara, adaF: !!d.f, bisa: d.f && d.f.bisa,
                    F: d.f && d.f.F, p: d.f && d.f.p,
                    nTabel: d.f && d.f.tabel ? d.f.tabel.length : 0,
                    nPerX: (d.f_terpisah||[]).length,
                    kalimat: d.f && d.f.kalimat}};
        }})()""")
        if isinstance(hasil, dict) and hasil.get('__galat'):
            cek('API buat-data jalan', False, json.dumps(hasil)[:250])
        else:
            cek('API buat-data jalan', True)
            cek('server kirim blok uji F (d.f)', hasil.get('adaF') is True, str(hasil))
            cek('uji F bisa dihitung', hasil.get('bisa') is True, str(hasil))
            cek('tabel ANOVA 3 baris dari SERVER', hasil.get('nTabel') == 3,
                str(hasil.get('nTabel')))
            cek('f_terpisah 3 buah (per-X)', hasil.get('nPerX') == 3,
                str(hasil.get('nPerX')))
            print(f"     F={hasil.get('F')}  p={hasil.get('p')}")
            print(f"     {hasil.get('kalimat')}")

        # ── tabel sungguhan HARUS RENDER (bukan cuma data) ──
        # ⚠️ JEBAKAN TERUKUR 21Sep26: `innerText` TIDAK memuat teks <th>
        #    (header kolom) — versi pertama uji ini menuntut /SS/ & /MS/ pada
        #    innerText → GAGAL PALSU padahal tabelnya ADA & lengkap.
        #    ATURAN (sama seperti jebakan lama): JANGAN membaca satu properti
        #    lalu menyimpulkan; BACA strukturnya (th + td).
        render = tab.js(f"""(async () => {{
          const r = await fetch('/api/buat-data', {{
            method: 'POST',
            headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify({{n:200, x:3, beta:[0.3,0.25,0.2],
              skala:5, alpha:0.85, mode:'presisi', cara:'berganda',
              kunci:'uji-anova', nama_x:['Harga','Promosi','Layanan']}})
          }});
          const d = await r.json();
          tampilkanHasil(d);
          const kotak = document.getElementById('hasil');
          const semuaTabel = Array.from(kotak.querySelectorAll('table'));
          // cari tabel yang headernya = Sumber/SS/df/MS/F/p (tabel ANOVA)
          const anova = semuaTabel.find(t => {{
            const h = Array.from(t.querySelectorAll('th'))
                          .map(x => (x.innerText || '').trim().toLowerCase());
            return h.includes('sumber') && h.includes('ss')
                   && h.includes('df') && h.includes('ms');
          }});
          const isiAnova = anova ? anova.innerText : '';
          const judul = kotak.innerText || '';
          return {{
            adaTabelAnova: !!anova,
            headerAnova: anova ? Array.from(anova.querySelectorAll('th'))
                                  .map(x => x.innerText.trim()) : [],
            barisAnova: anova ? anova.querySelectorAll('tbody tr').length : 0,
            barisPertama: anova ? Array.from(
              anova.querySelectorAll('tbody tr')[0].querySelectorAll('td'))
              .map(c => c.innerText.trim()) : [],
            adaSumber: /Regresi/.test(isiAnova) && /Residu/.test(isiAnova)
                       && /Total/.test(isiAnova),
            adaJudulAnova: /ANOVA/i.test(judul) || /serentak/i.test(judul),
            adaParsial: /PARSIAL/i.test(judul),
            tumpah: judul.includes('<div') || judul.includes('</'),
            potongan: judul.slice(0, 300)
          }};
        }})()""")
        if isinstance(render, dict) and render.get('__galat'):
            cek('render hasil tanpa galat JS', False, json.dumps(render)[:250])
        else:
            cek('render hasil tanpa galat JS', True)
            cek('tabel ANOVA TAMPIL di halaman', render.get('adaTabelAnova') is True,
                str(render.get('potongan', ''))[:150])
            # ⚠️ Header dibandingkan TANPA beda huruf besar/kecil.
            #    Tabel di-render dengan CSS text-transform:uppercase, jadi DOM
            #    mengembalikan 'SUMBER'/'DF'/'P', bukan 'Sumber'/'df'/'p'.
            #    Asersi lama case-sensitive → gagal palsu di master 20757a2 juga.
            #    (Wulan, 19Okt26)
            _hdr = [str(h).strip().lower() for h in (render.get('headerAnova') or [])]
            cek('header ANOVA = Sumber · SS · df · MS · F · p',
                all(h in _hdr for h in ['sumber', 'ss', 'df', 'ms', 'f', 'p']),
                str(render.get('headerAnova')))
            cek('tabel ANOVA 3 baris', render.get('barisAnova') == 3,
                str(render.get('barisAnova')))
            cek('3 sumber tampil (Regresi/Residu/Total)',
                render.get('adaSumber') is True)
            cek('judul menyebut ANOVA / uji serentak',
                render.get('adaJudulAnova') is True)
            cek('kata PARSIAL tampil (kartu ② = parsial + simultan)',
                render.get('adaParsial') is True)
            cek('kode TIDAK tumpah jadi teks', render.get('tumpah') is False,
                str(render.get('potongan', ''))[:200])
            print(f"     header ANOVA : {render.get('headerAnova')}")
            print(f"     baris pertama: {render.get('barisPertama')}")

        # ── kartu ① sederhana (parsial) juga harus punya uji F per-X ──
        kartu1 = tab.js(f"""(async () => {{
          const r = await fetch('/api/buat-data', {{
            method: 'POST',
            headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify({{n:200, x:3, beta:[0.3,0.25,0.2],
              skala:5, alpha:0.85, mode:'presisi', cara:'sederhana',
              kunci:'uji-anova', nama_x:['Harga','Promosi','Layanan']}})
          }});
          const d = await r.json();
          return {{cara: d.cara, nPerX: (d.f_terpisah||[]).length,
                    bisa: (d.f_terpisah||[]).every(f => f.bisa)}};
        }})()""")
        cek('kartu ① (sederhana/parsial): uji F per-X ADA',
            kartu1.get('nPerX') == 3, str(kartu1))
        cek('kartu ① (sederhana/parsial): semua uji F bisa dihitung',
            kartu1.get('bisa') is True, str(kartu1))
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
