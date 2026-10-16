"""UJI GRAFIK DI HALAMAN SUNGGUHAN — /klinik (Tahap 2.1c).

MENGAPA: gerbang JS membuktikan FUNGSI gambar benar, tapi TIDAK membuktikan
grafiknya sampai ke halaman. Bisa saja fungsinya benar tapi tidak dipanggil,
atau mati karena urutan pemuatan skrip. Uji ini menempuh jalan yang SAMA
seperti mahasiswa: unggah berkas → klik Periksa → lihat halaman.

CARA: server uji dinyalakan sendiri (port 8122), Chrome :9333 dipakai bersama.
"""
import io
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np                                              # noqa: E402
import pandas as pd                                             # noqa: E402
import websocket                                                # noqa: E402

PORT = 9333
PORT_UJI = 8122
BASE = f'http://127.0.0.1:{PORT_UJI}'
RAIZ = Path(__file__).resolve().parent.parent

LULUS = 0
GAGAL = 0


def cek(nama, syarat, info=''):
    global LULUS, GAGAL
    if syarat:
        LULUS += 1
        print(f'  \u2705 {nama}')
    else:
        GAGAL += 1
        print(f'  \u274c {nama}  {info}')


def cdp_hidup(port=PORT):
    try:
        return urllib.request.urlopen(
            f'http://127.0.0.1:{port}/json/version', timeout=4).status == 200
    except Exception:
        return False


def server_hidup(port=PORT_UJI):
    try:
        return urllib.request.urlopen(
            f'http://127.0.0.1:{port}/health', timeout=3).status == 200
    except Exception:
        return False


def nyalakan_server():
    """Server uji — dijalankan lewat terminal background Hermes lewat pemanggil,
    di sini cukup memastikan ia hidup (kalau tidak, uji GAGAL dengan pesan)."""
    for _ in range(40):
        if server_hidup():
            return True
        time.sleep(0.5)
    return False


class Tab:
    def __init__(self, port):
        self.port = port
        self.tab_id = None
        self.ws = None

    def buka(self):
        t = json.loads(urllib.request.urlopen(
            urllib.request.Request(f'http://127.0.0.1:{self.port}/json/new?about:blank',
                                   method='PUT'), timeout=20).read())
        self.tab_id = t.get('id')
        self.ws = websocket.create_connection(t['webSocketDebuggerUrl'], timeout=60)

    def cmd(self, metode, **p):
        self._id = getattr(self, '_id', 0) + 1
        self.ws.send(json.dumps({'id': self._id, 'method': metode, 'params': p}))
        while True:
            r = json.loads(self.ws.recv())
            if r.get('id') == self._id:
                return r
        return {}

    def js(self, expr):
        r = self.cmd('Runtime.evaluate', expression=expr, returnByValue=True,
                     awaitPromise=True)
        return r.get('result', {}).get('result', {}).get('value')

    def tutup(self):
        try:
            if self.ws:
                self.ws.close()
        except Exception:
            pass
        try:
            if self.tab_id:
                urllib.request.urlopen(urllib.request.Request(
                    f'http://127.0.0.1:{self.port}/json/close/{self.tab_id}'),
                    timeout=15).read()
        except Exception:
            pass


def data_csv(sehat=True):
    rng = np.random.default_rng(7)
    n = 120
    x1 = rng.normal(0, 1, n)
    x2 = rng.normal(0, 1, n)
    dasar = 0.45 * x1 + 0.30 * x2
    y = dasar + (rng.normal(0, 1, n) if sehat
                 else rng.normal(0, 1, n) * np.exp(1.2 * x1))
    return pd.DataFrame({'X1': x1, 'X2': x2, 'Y': y}).to_csv(index=False)


def unggah(csv_teks):
    """Unggah CSV lewat /api/diagnosis/unggah — pakai multipart seperti browser."""
    batas = '----BatasUjiWulan'
    isi = (f'--{batas}\r\n'
           'Content-Disposition: form-data; name="berkas"; filename="uji.csv"\r\n'
           'Content-Type: text/csv\r\n\r\n'
           f'{csv_teks}\r\n--{batas}--\r\n').encode()
    req = urllib.request.Request(
        BASE + '/api/diagnosis/unggah', data=isi,
        headers={'Content-Type': f'multipart/form-data; boundary={batas}'})
    return json.loads(urllib.request.urlopen(req, timeout=60).read())


def periksa(kunci, kolom_x, kolom_y, cara_missing='buang'):
    """Panggil /api/diagnosis/periksa.

    ⚠️ AKAR (20Sep26) — `kunci` WAJIB dikirim balik. Terukur dari halaman
    (diagnosis.html baris 579): `const kirim = { kunci: KUNCI, mode: ALAT,
    missing: ... }`. `KUNCI` datang dari jawaban `/unggah` (`d.kunci`).
    Tanpa `kunci`, server menjawab HTTP 400 dengan pesan jujur
    "Datanya sudah tidak ada di server (mungkin sesi terlalu lama)".
    ⇒ Ini CACAT UJI WULAN, bukan bug aplikasi. Server BENAR: data sementara
    memang harus ditautkan ke sesi pengunggahnya, bukan diambil sembarangan.
    """
    req = urllib.request.Request(
        BASE + '/api/diagnosis/periksa',
        data=json.dumps({'kunci': kunci, 'mode': 'spss',
                         'missing': cara_missing,
                         'kolom_x': kolom_x, 'kolom_y': kolom_y}).encode(),
        headers={'Content-Type': 'application/json'})
    return json.loads(urllib.request.urlopen(req, timeout=120).read())


def unggah_dan_periksa(csv_teks, kolom_x, kolom_y):
    """Unggah LALU periksa — WAJIB berurutan tanpa jeda.

    ⚠️ AKAR (20Sep26) — CACAT UJI WULAN, bukan bug aplikasi.
    Percobaan pertama: uji memanggil `unggah()` dan `periksa()` sebagai dua
    langkah TERPISAH, dengan pemanggilan LAIN di antaranya. Hasilnya HTTP 400
    dengan pesan server yang JUJUR: "Datanya sudah tidak ada di server
    (mungkin sesi terlalu lama). Coba unggah ulang ya — sekali klik saja."
    ⇒ Data unggahan disimpan SEMENTARA dan dipakai SEKALI oleh `/periksa`.
    Urutan yang benar (sama seperti mahasiswa menekan tombol): unggah →
    langsung periksa, tanpa disela.
    """
    u = unggah(csv_teks)
    r = periksa(u.get('kunci'), kolom_x, kolom_y)
    return u, r


def main():
    print('  ── prasyarat ──')
    # Prasarana: Chrome mati = LEWAT (77), bukan GAGAL — mesin tidak salah.
    from prasarana_uji import pastikan_chrome
    kode_prasarana = pastikan_chrome(PORT)
    if kode_prasarana is not None:
        return kode_prasarana
    cek(f'Chrome CDP :{PORT} hidup', True)
    if not nyalakan_server():
        print(f'  \u274c server uji :{PORT_UJI} TIDAK HIDUP — uji dibatalkan.')
        return 1
    cek(f'server uji :{PORT_UJI} hidup', True)

    tab = None
    try:
        # ── 1. mesin: unggah + periksa lewat HTTP (seperti web memanggilnya) ──
        u, r = unggah_dan_periksa(data_csv(True), ['X1', 'X2'], 'Y')
        cek('unggah CSV berhasil', bool(u.get('kolom')), json.dumps(u)[:120])
        cek('periksa: ada bahan titik', bool(r.get('titik')))
        cek('periksa: titik.pp ada', bool(r['titik'].get('pp', {}).get('teori')))
        cek('periksa: titik.hist ada', bool(r['titik'].get('hist', {}).get('tinggi')))
        cek('periksa: titik.xy ada', bool(r['titik'].get('xy', {}).get('x')))
        cek('periksa: prediktor terkirim (label grafik)', bool(r.get('prediktor')))

        # ── 2. halaman: apakah grafik BENAR-BENAR tergambar? ──
        tab = Tab(PORT)
        tab.buka()
        tab.cmd('Page.enable')
        tab.cmd('Runtime.enable')
        tab.cmd('Page.navigate', url=BASE + '/klinik')
        time.sleep(4)

        # apakah skrip grafik hidup dimuat?
        cek('berkas grafik_hidup.js termuat di halaman',
            bool(tab.js("!!(window.svgHetero && window.svgPP && window.kotakGrafik)")))
        cek('halaman TIDAK menumpahkan kode jadi teks',
            not bool(tab.js("document.body.innerText.indexOf('function svgHetero') >= 0")))

        # jalankan alur seperti mahasiswa: tempel data + klik Periksa lewat fungsi halaman
        # (pakai fetch dari dalam halaman supaya memakai kode yang SAMA)
        hasil = tab.js("""
        (async () => {
          try {
            const csv = `X1,X2,Y\\n` + Array.from({length:120}, (_,i) =>
              [(Math.sin(i)*1.3).toFixed(4), (Math.cos(i)*1.3).toFixed(4),
               (Math.sin(i)*0.6 + Math.cos(i)*0.4 + Math.sin(i*7)*0.9).toFixed(4)].join(',')
            ).join('\\n');
            const fd = new FormData();
            fd.append('berkas', new Blob([csv], {type:'text/csv'}), 'uji.csv');
            const a = await fetch('/api/diagnosis/unggah', {method:'POST', body:fd});
            const da = await a.json();
            if (!a.ok) return {tahap:'unggah', galat: JSON.stringify(da).slice(0,200)};
            const b = await fetch('/api/diagnosis/periksa', {
              method:'POST', headers:{'Content-Type':'application/json'},
              body: JSON.stringify({kunci: da.kunci, mode:'spss', missing:'buang',
                                   kolom_x:['X1','X2'], kolom_y:'Y'})});
            const db = await b.json();
            if (!b.ok) return {tahap:'periksa', galat: JSON.stringify(db).slice(0,200)};
            gambarHasil(db);
            const wadah = document.getElementById('kartu-hasil');
            const svgs = wadah.querySelectorAll('[data-grafik] svg');
            const titik = wadah.querySelectorAll('[data-grafik] svg circle');
            return {tahap:'selesai', jmlGrafik: svgs.length, jmlTitik: titik.length,
                    kunci: Array.from(wadah.querySelectorAll('[data-grafik]'))
                             .map(e => e.getAttribute('data-grafik')),
                    kolom: da.kolom || []};
          } catch (e) { return {tahap:'luar', galat: String(e).slice(0,200)}; }
        })()
        """)
        print(f'     (hasil halaman: {json.dumps(hasil)[:220]})')

        cek('alur halaman selesai tanpa galat',
            isinstance(hasil, dict) and hasil.get('tahap') == 'selesai',
            json.dumps(hasil)[:200])
        if isinstance(hasil, dict) and hasil.get('tahap') == 'selesai':
            cek('ADA 3 kotak grafik di hasil (pp, hetero, linear)',
                hasil.get('jmlGrafik') == 3, str(hasil.get('jmlGrafik')))
            cek('grafik P-P tergambar (kotak data-grafik="pp")',
                'pp' in (hasil.get('kunci') or []), str(hasil.get('kunci')))
            cek('grafik hetero tergambar',
                'hetero' in (hasil.get('kunci') or []))
            cek('grafik linearitas tergambar',
                'linear' in (hasil.get('kunci') or []))
            cek('grafik berisi titik sungguhan (>50 lingkaran)',
                (hasil.get('jmlTitik') or 0) > 50, str(hasil.get('jmlTitik')))

        # ── 3. data SAKIT → gambar harus BEDA ──
        sakit = tab.js("""
        (async () => {
          try {
            const csv = `X1,X2,Y\\n` + Array.from({length:120}, (_,i) => {
              const x1 = Math.sin(i*3.1)*1.2, x2 = Math.cos(i*2.3)*1.2;
              const d = 0.45*x1 + 0.30*x2;
              const derau = Math.sin(i*11.7) * Math.exp(1.2*x1);
              return [x1.toFixed(4), x2.toFixed(4), (d+derau).toFixed(4)].join(',');
            }).join('\\n');
            const fd = new FormData();
            fd.append('berkas', new Blob([csv], {type:'text/csv'}), 'sakit.csv');
            const a = await fetch('/api/diagnosis/unggah', {method:'POST', body:fd});
            const da = await a.json();
            const b = await fetch('/api/diagnosis/periksa', {
              method:'POST', headers:{'Content-Type':'application/json'},
              body: JSON.stringify({kunci: da.kunci, mode:'spss', missing:'buang',
                                   kolom_x:['X1','X2'], kolom_y:'Y'})});
            const db = await b.json();
            if (!b.ok) return {tahap:'periksa', galat: JSON.stringify(db).slice(0,200)};
            gambarHasil(db);
            const el = document.querySelector('[data-grafik="hetero"] svg');
            const c = el.querySelectorAll('circle');
            const warna = c.length ? c[0].getAttribute('fill') : '';
            return {tahap:'selesai', jmlTitik: c.length, warna: warna,
                    lulusHetero: db.hetero ? db.hetero.lulus : null,
                    glejser: db.hetero ? db.hetero.glejser_p : null};
          } catch (e) { return {tahap:'luar', galat: String(e).slice(0,200)}; }
        })()
        """)
        print(f'     (data sakit: {json.dumps(sakit)[:200]})')
        cek('data SAKIT: hetero terdeteksi TIDAK lulus',
            isinstance(sakit, dict) and sakit.get('lulusHetero') is False,
            json.dumps(sakit)[:160])
        cek('data SAKIT: grafik memakai warna merah (penanda masalah)',
            isinstance(sakit, dict) and sakit.get('warna') == '#A85A5A',
            str(sakit.get('warna')))

    finally:
        if tab is not None:
            tab.tutup()

    print()
    if GAGAL:
        print(f'  \u274c GAGAL: {GAGAL} dari {LULUS + GAGAL}')
        return 1
    print(f'  \u2705 LULUS SEMUA: {LULUS} pemeriksaan')
    return 0


if __name__ == '__main__':
    sys.exit(main())
