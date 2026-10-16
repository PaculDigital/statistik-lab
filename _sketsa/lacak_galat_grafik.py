"""Cari AKAR galat halaman: jalankan gambarHasil() dan tangkap galat PERSIS.

⚠️ ATURAN (pelajaran lama): `[object Object]` / pesan galat kabur = DIAGNOSA
BUTA. Tangkap `e.stack` supaya tahu BARIS mana yang meledak — jangan tebak.
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import urllib.request                                          # noqa: E402
import websocket                                               # noqa: E402

PORT, PORT_UJI = 9333, 8122
BASE = f'http://127.0.0.1:{PORT_UJI}'


def main():
    t = json.loads(urllib.request.urlopen(urllib.request.Request(
        f'http://127.0.0.1:{PORT}/json/new?about:blank', method='PUT'), timeout=20).read())
    ws = websocket.create_connection(t['webSocketDebuggerUrl'], timeout=60)
    _id = [0]

    def cmd(m, **p):
        _id[0] += 1
        ws.send(json.dumps({'id': _id[0], 'method': m, 'params': p}))
        while True:
            r = json.loads(ws.recv())
            if r.get('id') == _id[0]:
                return r

    def js(e):
        r = cmd('Runtime.evaluate', expression=e, returnByValue=True, awaitPromise=True)
        res = r.get('result', {})
        if res.get('exceptionDetails'):
            return {'GALAT': res['exceptionDetails'].get('text'),
                    'stack': (res['exceptionDetails'].get('stackTrace') or {}).get('callFrames', [])[:4],
                    'deskripsi': (res['exceptionDetails'].get('exception') or {}).get('description', '')[:600]}
        return res.get('result', {}).get('value')

    try:
        cmd('Page.enable'); cmd('Runtime.enable')
        cmd('Page.navigate', url=BASE + '/klinik')
        time.sleep(4)

        print('  ── 1. fungsi gambar ADA? ──')
        print('   ', js("({kotakGrafik: typeof kotakGrafik, svgPP: typeof svgPP, "
                       "svgHetero: typeof svgHetero, svgLinear: typeof svgLinear, "
                       "catatanTitik: typeof catatanTitik})"))

        print('  ── 2. unggah + periksa + gambarHasil, TANGKAP stack ──')
        out = js("""
        (async () => {
          try {
            const csv = `X1,X2,Y\\n` + Array.from({length:120}, (_,i) =>
              [(Math.sin(i)*1.3).toFixed(4), (Math.cos(i)*1.3).toFixed(4),
               (Math.sin(i)*0.6+Math.cos(i)*0.4+Math.sin(i*7)*0.9).toFixed(4)].join(',')
            ).join('\\n');
            const fd = new FormData();
            fd.append('berkas', new Blob([csv], {type:'text/csv'}), 'u.csv');
            const a = await fetch('/api/diagnosis/unggah', {method:'POST', body:fd});
            const da = await a.json();
            const b = await fetch('/api/diagnosis/periksa', {
              method:'POST', headers:{'Content-Type':'application/json'},
              body: JSON.stringify({kunci: da.kunci, mode:'spss', missing:'buang',
                                    kolom_x:['X1','X2'], kolom_y:'Y'})});
            const db = await b.json();
            if (!b.ok) return {tahap:'periksa', galat: JSON.stringify(db).slice(0,300)};
            try {
              gambarHasil(db);
            } catch (e) {
              return {tahap:'gambarHasil', galat: String(e), stack: (e.stack||'').split('\\n').slice(0,6)};
            }
            const w = document.getElementById('kartu-hasil');
            return {tahap:'selesai',
                    grafik: Array.from(w.querySelectorAll('[data-grafik]')).map(e=>e.getAttribute('data-grafik')),
                    kunci_db: typeof db.kunci, n_db: typeof db.n,
                    titik_ada: !!db.titik};
          } catch (e) { return {tahap:'luar', galat: String(e), stack: (e.stack||'').split('\\n').slice(0,6)}; }
        })()
        """)
        print(json.dumps(out, indent=2, ensure_ascii=False)[:1800])
    finally:
        try:
            ws.close()
        except Exception:
            pass
        try:
            urllib.request.urlopen(urllib.request.Request(
                f'http://127.0.0.1:{PORT}/json/close/{t["id"]}'), timeout=15).read()
        except Exception:
            pass


main()
