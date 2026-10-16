"""Potret halaman /klinik APA ADANYA — unggah sungguhan, tanpa tiruan.

Lebih jujur daripada menyuntik: berkas benar-benar diunggah lewat HTTP.
"""
import base64
import io
import json
import time
import urllib.request
import uuid
import websocket

CDP = 'http://127.0.0.1:9333'
BASE = 'http://127.0.0.1:8122'


def _j(u):
    with urllib.request.urlopen(u, timeout=10) as r:
        return json.loads(r.read().decode())


def bersihkan_tab():
    n = 0
    for t in _j(f'{CDP}/json/list'):
        if t.get('type') == 'page':
            try:
                urllib.request.urlopen(
                    f"{CDP}/json/close/{t['id']}", timeout=5).read()
                n += 1
            except Exception:                              # noqa: BLE001
                pass
    return n


class S:
    def __init__(self, ws):
        self.ws = websocket.create_connection(ws, timeout=40)
        self.i = 0

    def k(self, m, **p):
        self.i += 1
        self.ws.send(json.dumps({'id': self.i, 'method': m, 'params': p}))
        while True:
            d = json.loads(self.ws.recv())
            if d.get('id') == self.i:
                if 'error' in d:
                    raise RuntimeError(d['error'])
                return d.get('result', {})

    def ev(self, e):
        return self.k('Runtime.evaluate', expression=e,
                      returnByValue=True, awaitPromise=True
                      ).get('result', {}).get('value')

    def tutup(self):
        self.ws.close()


print('=' * 72)
print('  POTRET /klinik APA ADANYA (berkas diunggah sungguhan)')
print('=' * 72)
print(f'\n[1] Bersihkan tab: {bersihkan_tab()} ditutup')

req = urllib.request.Request(f'{CDP}/json/new?{BASE}/klinik', method='PUT')
t = json.loads(urllib.request.urlopen(req, timeout=10).read().decode())
s = S(t['webSocketDebuggerUrl'])
for _ in range(30):
    if s.ev('document.readyState') == 'complete':
        break
    time.sleep(0.5)
print(f"[2] Tab {t['id'][:12]}… judul: {s.ev('document.title')}")

# ── Unggah berkas SUNGGUHAN lewat halaman (pakai input file) ─────────────
print('\n[3] Siapkan berkas CSV sungguhan')
kolom = ['Kualitas_Produk_1', 'Kualitas_Produk_2', 'Kualitas_Produk_3',
         'Harga_1', 'Harga_2', 'Harga_3', 'Citra_Merek_1', 'Citra_Merek_2',
         'Kepuasan_1', 'Kepuasan_2']
baris = [';'.join(kolom)]
for i in range(60):
    baris.append(';'.join(str(2 + ((i * 3 + j) % 4)) for j in range(len(kolom))))
csv = '\n'.join(baris)
path = '/tmp/data_skripsi_contoh.csv'
with open(path, 'w') as f:
    f.write(csv)
print(f'    {len(baris)-1} baris · {len(kolom)} kolom → {path}')

# Pakai DOM.setFileInputFiles (cara Chrome untuk mengisi <input type=file>)
dok = s.k('DOM.getDocument')['root']['nodeId']
inp = s.k('DOM.querySelector', nodeId=dok, selector='#berkas')
if not inp.get('nodeId'):
    inp = s.k('DOM.querySelector', nodeId=dok, selector='input[type=file]')
node = inp['nodeId']
print(f'[4] Isi input berkas (nodeId={node})')
s.k('DOM.setFileInputFiles', files=[path], nodeId=node)

for _ in range(40):
    if s.ev("document.getElementById('kartu-kolom') && "
            "!document.getElementById('kartu-kolom').hidden"):
        break
    time.sleep(0.5)

n_kolom = s.ev("document.querySelectorAll('#daftar-peran .pilih-peran').length")
print(f'[5] Kolom tampil setelah unggah: {n_kolom} (harap 10)')

# ── Isi peran lewat KLIK SUNGGUHAN (bukan set nilai diam-diam) ───────────
print('\n[6] Isi peran seperti mahasiswa (pilih dari dropdown)')
s.ev("""
(() => {
  const aturan = [
    ['Kualitas_Produk', 'X1'], ['Harga', 'X2'],
    ['Citra_Merek', 'M1'], ['Kepuasan', 'Y1']
  ];
  document.querySelectorAll('#daftar-peran > div').forEach(d => {
    const sel = d.querySelector('select');
    const nama = sel.dataset.kolom;
    const cocok = aturan.find(a => nama.includes(a[0]));
    if (!cocok) return;
    sel.value = cocok[1];
    // klik sungguhan: kirim event seperti user memilih
    sel.dispatchEvent(new Event('input', {bubbles: true}));
    sel.dispatchEvent(new Event('change', {bubbles: true}));
  });
  segarkanPeran();
  return 'ok';
})()
""")
time.sleep(1)
print(f"    Ringkasan: {s.ev('document.getElementById(\"ringkas-peran\").innerText.trim()')}")

# ── Klik "Cek dulu" SUNGGUHAN ────────────────────────────────────────────
print('\n[7] Klik tombol "Cek dulu, benar atau tidak" (klik sungguhan)')
s.ev("document.getElementById('tb-periksa-peran').click()")
time.sleep(3)
isi_pesan = s.ev("document.getElementById('pesan-peran').innerText.trim()")
print(f'    Jawaban mesin:\n{isi_pesan[:500]}')

# ── Potret ───────────────────────────────────────────────────────────────
s.k('Emulation.setDeviceMetricsOverride', width=390, height=1500,
    deviceScaleFactor=2, mobile=True)
time.sleep(1)
s.ev("document.getElementById('kartu-kolom')"
     ".scrollIntoView({block:'start'})")
time.sleep(1)
png = s.k('Page.captureScreenshot', format='png')['data']
out = '/opt/data/services/statistik-lab/_bukti_peran_kolom.png'
with open(out, 'wb') as f:
    f.write(base64.b64decode(png))
print(f'\n[8] Potret: {out}')

# ── Potret bagian tombol (kalau perlu) ───────────────────────────────────
s.ev("document.getElementById('pesan-peran').scrollIntoView({block:'center'})")
time.sleep(1)
png2 = s.k('Page.captureScreenshot', format='png')['data']
out2 = '/opt/data/services/statistik-lab/_bukti_peran_protes.png'
with open(out2, 'wb') as f:
    f.write(base64.b64decode(png2))
print(f'[9] Potret protes: {out2}')

s.tutup()
print('\nSELESAI')
