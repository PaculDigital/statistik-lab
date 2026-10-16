"""Potret halaman /klinik dengan peran kolom terisi — via CDP.

Pelajaran lama: KOSONGKAN tab dulu (tab yatim = 'gerbang gantung 140 dtk').
Jangan pkill Chrome.
"""
import base64
import json
import sys
import urllib.request
import websocket

CDP = 'http://127.0.0.1:9333'


def _json(url):
    with urllib.request.urlopen(url, timeout=10) as r:
        return json.loads(r.read().decode())


def tab_baru(url):
    """Buka tab baru lewat /json/new (Chrome modern butuh PUT)."""
    req = urllib.request.Request(f'{CDP}/json/new?{url}', method='PUT')
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode())


def bersihkan_tab():
    """Tutup SEMUA tab halaman (bukan tab internal) — cegah tab yatim."""
    n = 0
    for t in _json(f'{CDP}/json/list'):
        if t.get('type') == 'page':
            try:
                urllib.request.urlopen(
                    f"{CDP}/json/close/{t['id']}", timeout=5).read()
                n += 1
            except Exception:                              # noqa: BLE001
                pass
    return n


class Sesi:
    def __init__(self, ws_url):
        self.ws = websocket.create_connection(ws_url, timeout=40)
        self.i = 0

    def kirim(self, method, **params):
        self.i += 1
        self.ws.send(json.dumps({'id': self.i, 'method': method,
                                 'params': params}))
        while True:
            d = json.loads(self.ws.recv())
            if d.get('id') == self.i:
                if 'error' in d:
                    raise RuntimeError(f'{method}: {d["error"]}')
                return d.get('result', {})

    def eval(self, expr):
        r = self.kirim('Runtime.evaluate', expression=expr,
                       returnByValue=True, awaitPromise=True)
        return r.get('result', {}).get('value')

    def tutup(self):
        self.ws.close()


print('=' * 72)
print('  POTRET HALAMAN /klinik — PERAN KOLOM')
print('=' * 72)

print(f'\n[1] Bersihkan tab yatim: {bersihkan_tab()} tab ditutup')

t = tab_baru('http://127.0.0.1:8122/klinik')
print(f"[2] Tab baru: {t['id'][:12]}…")
s = Sesi(t['webSocketDebuggerUrl'])

import time
for _ in range(30):
    if s.eval('document.readyState') == 'complete':
        break
    time.sleep(0.5)

judul = s.eval('document.title')
print(f'[3] Judul: {judul}')
print(f"    KOLOM awal: {s.eval('typeof KOLOM')} / "
      f"bangunDaftarPeran: {s.eval('typeof bangunDaftarPeran')}")

# ── Suntik kolom tiruan supaya halaman menampilkan daftar peran ──────────
print('\n[4] Suntik 9 kolom tiruan + bangun daftar peran')
s.eval("""
(() => {
  KOLOM = ['Kualitas_Produk_1','Kualitas_Produk_2','Kualitas_Produk_3',
           'Harga_1','Harga_2','Citra_Merek_1','Citra_Merek_2',
           'Kepuasan_1','Kepuasan_2'].map(n => ({nama: n}));
  document.getElementById('ringkas-berkas').hidden = false;
  document.getElementById('nama-berkas').textContent = 'data_skripsi.xlsx';
  document.getElementById('ukuran-berkas').textContent = '  ·  18 KB';
  document.getElementById('bentuk-berkas').textContent =
    '120 responden  ·  9 kolom';
  document.getElementById('kartu-kolom').hidden = false;
  PERAN = {}; PERAN_DIPAKAI = peranBawaan();
  bangunDaftarPeran(); segarkanPeran();
  return 'ok';
})()
""")

n_baris = s.eval("document.querySelectorAll('#daftar-peran .pilih-peran').length")
print(f'    Baris kolom tampil: {n_baris} (harap 9)')

# ── Isi peran seperti mahasiswa ──────────────────────────────────────────
print('\n[5] Isi peran (Kualitas→X1, Harga→X2, Citra→M1, Kepuasan→Y1)')
s.eval("""
(() => {
  const isi = {'Kualitas_Produk':'X1','Harga':'X2','Citra_Merek':'M1',
               'Kepuasan':'Y1'};
  document.querySelectorAll('#daftar-peran .pilih-peran').forEach(sel => {
    const kolom = sel.dataset.kolom;
    const akar = kolom.split('_').slice(0,2).join('_');
    let p = null;
    for (const k in isi) { if (kolom.includes(k)) { p = isi[k]; break; } }
    if (p) { sel.value = p; sel.dispatchEvent(new Event('change')); }
  });
  segarkanPeran();
  return document.getElementById('ringkas-peran').textContent;
})()
""")
ringkas = s.eval("document.getElementById('ringkas-peran').textContent.trim()")
print(f'    Ringkasan: {ringkas}')

# ── Tampilkan protes mesin (masalah + pertanyaan) ────────────────────────
print('\n[6] Tampilkan contoh protes mesin')
s.eval("""
(() => {
  tampilkanPeriksaPeran({
    boleh_lanjut: true,
    ringkas: 'penyebab (X): X1 (3 kolom) · X2 (2 kolom) | ' +
             'perantara (M): M1 (2 kolom) | hasil (Y): Y1 (2 kolom)',
    masalah: [],
    tanya: [
      {jenis:'satu_kolom', pesan:'X2 cuma punya 2 kolom. Biasanya satu ' +
        'variabel minimal 2-3 pertanyaan — kalau memang cuma 2, tidak apa-apa.'},
      {jenis:'bentuk_mediasi', pesan:'Ada 2 perantara (M1, M2). ' +
        'Keduanya keluar dari X (paralel), atau M1 dulu lalu M2 (berjenjang)?',
       pilihan:['paralel','berjenjang']}
    ]
  });
  return 'ok';
})()
""")

# ── Geometri + potret ────────────────────────────────────────────────────
geo = s.eval("""
(() => {
  const w = document.querySelector('#daftar-peran');
  const k = document.getElementById('kartu-kolom').getBoundingClientRect();
  return JSON.stringify({daftar: w ? w.getBoundingClientRect().height : 0,
                         kartu: [Math.round(k.width), Math.round(k.height)],
                         scroll: w ? w.scrollHeight : 0});
})()
""")
print(f'[7] Geometri: {geo}')

s.kirim('Emulation.setDeviceMetricsOverride', width=390, height=900,
        deviceScaleFactor=2, mobile=True)
time.sleep(1)
s.eval("document.getElementById('kartu-kolom')"
       ".scrollIntoView({block:'start'})")
time.sleep(1)

png = s.kirim('Page.captureScreenshot', format='png')['data']
out = '/opt/data/services/statistik-lab/_bukti_peran_kolom.png'
with open(out, 'wb') as f:
    f.write(base64.b64decode(png))
print(f'[8] Potret tersimpan: {out}')

s.tutup()
print('\nSELESAI')
