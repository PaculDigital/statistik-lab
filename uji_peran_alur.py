"""Uji E2E LENGKAP: unggah → tandai peran → Cek dulu → Periksa sekarang.

Yang paling penting: apakah tombol "Periksa sekarang" (periksa()) masih
jalan setelah bentuk peran menggantikan baris-x/baris-m lama.
"""
import base64
import json
import time
import urllib.request
import websocket

CDP = 'http://127.0.0.1:9333'
BASE = 'http://127.0.0.1:8122'
LULUS = GAGAL = 0
CATAT = []


def cek(nama, syarat, catatan=''):
    global LULUS, GAGAL
    if syarat:
        LULUS += 1
        print(f'  ✅ {nama}')
    else:
        GAGAL += 1
        CATAT.append(nama)
        print(f'  ❌ {nama}  {catatan}')


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
        self.ws = websocket.create_connection(ws, timeout=60)
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


# Tangkap galat JS sungguhan (bukan cuma pesan di layar)
GALAT_JS: list[str] = []


def siapkan():
    req = urllib.request.Request(f'{CDP}/json/new?{BASE}/klinik', method='PUT')
    t = json.loads(urllib.request.urlopen(req, timeout=10).read().decode())
    s = S(t['webSocketDebuggerUrl'])
    s.k('Runtime.enable')
    s.k('Log.enable')
    for _ in range(30):
        if s.ev('document.readyState') == 'complete':
            break
        time.sleep(0.5)
    return s, t


print('=' * 74)
print('  UJI E2E LENGKAP — UNGGAH → PERAN → CEK → PERIKSA')
print('=' * 74)
print(f'\n[1] Bersihkan tab: {bersihkan_tab()} ditutup')

s, t = siapkan()
print(f"[2] Tab {t['id'][:12]}… — {s.ev('document.title')}")

# Pasang penangkap galat JS
s.ev("""
(() => {
  window.__galatJS = [];
  window.addEventListener('error', e => {
    window.__galatJS.push('error: ' + (e.message || '') + ' @' +
      (e.filename || '') + ':' + (e.lineno || ''));
  });
  window.addEventListener('unhandledrejection', e => {
    window.__galatJS.push('rejection: ' + (e.reason && e.reason.message ||
      String(e.reason)));
  });
  window.__pesanAsli = console.error;
  console.error = function () {
    window.__galatJS.push('console.error: ' +
      Array.from(arguments).map(String).join(' '));
    window.__pesanAsli.apply(console, arguments);
  };
  return 'ok';
})()
""")

# ── 3. Elemen-elemen wajib ada ───────────────────────────────────────────
print('\n[3] Elemen halaman (mode SPSS)')
cek('daftar-peran ada', s.ev("!!document.getElementById('daftar-peran')"))
cek('tb-periksa-peran ada', s.ev("!!document.getElementById('tb-periksa-peran')"))
cek('tombol Periksa sekarang ada', s.ev("!!document.getElementById('tombol-periksa')"))
cek('kotak-peran-baru ada (mulai tersembunyi)',
    s.ev("!!document.getElementById('kotak-peran-baru') && "
         "document.getElementById('kotak-peran-baru').hidden === true"))
cek('TIDAK ada baris-x lagi', s.ev("!document.getElementById('baris-x')"))
cek('TIDAK ada baris-m lagi', s.ev("!document.getElementById('baris-m')"))

# ── 4. Unggah berkas sungguhan ───────────────────────────────────────────
print('\n[4] Unggah berkas 60 baris × 10 kolom')
s.k('DOM.enable')
dok = s.k('DOM.getDocument')['root']['nodeId']
node = s.k('DOM.querySelector', nodeId=dok,
           selector='input[type=file]')['nodeId']
s.k('DOM.setFileInputFiles', files=['/tmp/data_skripsi_contoh.csv'],
    nodeId=node)
for _ in range(40):
    if s.ev("!document.getElementById('kartu-kolom').hidden"):
        break
    time.sleep(0.5)

n_kolom = s.ev("document.querySelectorAll('#daftar-peran .pilih-peran').length")
cek('10 baris kolom tampil', n_kolom == 10, f'dapat {n_kolom}')
cek('KUNCI terisi', s.ev("typeof KUNCI === 'string' && KUNCI.length > 0"))
cek('tidak ada galat JS setelah unggah',
    len(s.ev('JSON.stringify(window.__galatJS)') or '[]') <= 2,
    str(s.ev('JSON.stringify(window.__galatJS)')))

# ── 5. Nama kolom terlihat (cacat yang tadi ditemukan) ───────────────────
print('\n[5] Nama kolom BENAR-BENAR terlihat (bukan 0px)')
lebar = s.ev("""
(() => {
  const s = document.querySelector('#daftar-peran .kurung-nama');
  return s ? Math.round(s.getBoundingClientRect().width) : -1;
})()
""")
cek('lebar nama kolom > 40px', lebar > 40, f'lebar={lebar}')

# ── 6. Tandai peran (lewat event change SUNGGUHAN) ───────────────────────
print('\n[6] Tandai peran lewat event change sungguhan')
s.ev("""
(() => {
  const aturan = [['Kualitas_Produk', 'X1'], ['Harga', 'X2'],
                  ['Citra_Merek', 'M1'], ['Kepuasan', 'Y1']];
  document.querySelectorAll('#daftar-peran > div').forEach(d => {
    const sel = d.querySelector('select');
    const nama = sel.dataset.kolom;
    const cocok = aturan.find(a => nama.includes(a[0]));
    if (!cocok) return;
    sel.value = cocok[1];
    sel.dispatchEvent(new Event('input', {bubbles: true}));
    sel.dispatchEvent(new Event('change', {bubbles: true}));
  });
  return 'ok';
})()
""")
time.sleep(1)
ringkas = s.ev("document.getElementById('ringkas-peran').innerText.trim()")
print(f'    Ringkasan: {ringkas}')
cek('ringkasan sebut 4 peran',
    all(x in ringkas for x in ['X1', 'X2', 'M1', 'Y1']), ringkas)
cek('PERAN terisi 10 kolom',
    s.ev('Object.keys(PERAN).filter(k => PERAN[k]).length') == 10,
    str(s.ev('Object.keys(PERAN).filter(k => PERAN[k]).length')))

# ── 7. Klik "Cek dulu" ───────────────────────────────────────────────────
print('\n[7] Klik "Cek dulu, benar atau tidak"')
s.ev("document.getElementById('tb-periksa-peran').click()")
time.sleep(3)
jawab = s.ev("document.getElementById('pesan-peran').innerText.trim()")
cek('mesin menjawab (bukan kosong)', len(jawab or '') > 20, repr(jawab[:80]))
cek('mesin bilang cocok', 'sudah cocok' in (jawab or '').lower()
    or 'boleh' in (jawab or '').lower(), jawab[:200])
cek('tidak ada pesan "koneksi terputus"',
    'terputus' not in (jawab or '').lower(), jawab[:200])

# ── 8. Klik "Periksa sekarang" (INI YANG PALING PENTING) ─────────────────
print('\n[8] Klik "Periksa sekarang" — hitung sungguhan')
s.ev("""
(() => {
  const b = document.getElementById('tombol-periksa');
  if (b) { b.click(); return 'diklik'; }
  return 'TOMBOL TIDAK ADA';
})()
""")
time.sleep(8)
hasil_muncul = s.ev("!document.getElementById('kartu-hasil').hidden")
isi = s.ev("document.getElementById('kartu-hasil').innerText.trim()")
cek('kartu hasil MUNCUL', bool(hasil_muncul),
    repr((isi or '')[:200]))
cek('hasil tidak kosong', len(isi or '') > 100, f'panjang={len(isi or "")}')
cek('hasil menyebut R² atau koefisien',
    'R²' in (isi or '') or 'koefisien' in (isi or '').lower()
    or 'R2' in (isi or ''), repr((isi or '')[:200]))
cek('TIDAK ada pesan "koneksi terputus" di pesan-periksa',
    'terputus' not in
    (s.ev("document.getElementById('pesan-periksa').innerText") or '').lower(),
    repr(s.ev("document.getElementById('pesan-periksa').innerText")))

print(f"\n    Cuplikan hasil: {(isi or '')[:300]}")

# ── 9. Galat JS ──────────────────────────────────────────────────────────
print('\n[9] Galat JS sepanjang alur')
gj = s.ev('JSON.stringify(window.__galatJS)') or '[]'
n_gj = len(json.loads(gj))
print(f'    {n_gj} kejadian: {gj[:400]}')
cek('tidak ada galat JS', n_gj == 0, gj[:400])

# ── 10. Potret hasil ─────────────────────────────────────────────────────
try:
    s.k('Emulation.setDeviceMetricsOverride', width=390, height=1800,
        deviceScaleFactor=2, mobile=True)
    time.sleep(1)
    s.ev("document.getElementById('kartu-kolom')"
         ".scrollIntoView({block:'start'})")
    time.sleep(1)
    png = s.k('Page.captureScreenshot', format='png')['data']
    out = '/opt/data/services/statistik-lab/_bukti_peran_alur.png'
    with open(out, 'wb') as f:
        f.write(base64.b64decode(png))
    print(f'\n[10] Potret alur: {out}')
except Exception as e:                                     # noqa: BLE001
    # Potret itu BONUS — jangan sampai menggagalkan uji yang sudah lulus
    print(f'\n[10] Potret dilewati (bukan cacat app): {e!r}')

s.tutup()
print('\n' + '=' * 74)
print(f'  {LULUS} LULUS / {GAGAL} GAGAL')
if CATAT:
    print('  Yang gagal: ' + ' · '.join(CATAT))
print('=' * 74)
