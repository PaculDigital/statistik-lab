"""UKUR: MEDIASI & MODERASI — sampai ke HASIL atau tidak?

Tujuan (Opsi A, ACC Bos 21Sep26): buktikan lewat PINTU PRODUKSI
(rute HTTP sungguhan), bukan fungsi internal (pelajaran K-09).

Yang diukur:
  1. Apakah server punya rute untuk mediasi/moderasi?
  2. Kalau mahasiswa tandai X1 + M1 + Y1 → apa yang MESIN keluarkan?
     - Apakah ada 'pengaruh tidak langsung' (a x b)?
     - Apakah M diperlakukan sebagai perantara, atau sebagai prediktor biasa?
  3. Moderasi: apakah ada 'interaksi' di jawaban?
"""
import sys, json, urllib.request
sys.path.insert(0, '/opt/data/services/statistik-lab')

BASE = 'http://127.0.0.1:8122'
KEPALA = '=' * 74


def kirim(path, payload):
    req = urllib.request.Request(
        BASE + path, data=json.dumps(payload).encode(),
        headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(r.read().decode())


print(KEPALA)
print(' 1) RUTE APA SAJA YANG ADA?')
print(KEPALA)
try:
    with urllib.request.urlopen(BASE + '/openapi.json', timeout=30) as r:
        spec = json.loads(r.read().decode())
    for p in sorted(spec.get('paths', {})):
        print('   ', p)
except Exception as e:
    print('   (gagal baca openapi: %s)' % type(e).__name__)

# ── Siapkan data: X1, M1, Y1 (masing-masing 3 kolom) ──────────────────────
print('\n' + KEPALA)
print(' 2) UNGGAH data mediasi (X1, M1, Y1) lewat berkas sungguhan')
print(KEPALA)
import csv, io
import numpy as np
rng = np.random.default_rng(3)
n = 200
X = rng.normal(size=n)
M = 0.55 * X + rng.normal(scale=0.8, size=n)          # a = 0,55
Y = 0.10 * X + 0.50 * M + rng.normal(scale=0.8, size=n)  # b = 0,50, c' = 0,10
buf = io.StringIO()
w = csv.writer(buf)
w.writerow(['X1a', 'X1b', 'X1c', 'M1a', 'M1b', 'M1c', 'Y1a', 'Y1b', 'Y1c'])
for i in range(n):
    def t(v):
        return int(np.clip(round(3 + v * 0.9), 1, 5))
    w.writerow([t(X[i]), t(X[i] + rng.normal(scale=.3)),
                t(X[i] + rng.normal(scale=.3)),
                t(M[i]), t(M[i] + rng.normal(scale=.3)),
                t(M[i] + rng.normal(scale=.3)),
                t(Y[i]), t(Y[i] + rng.normal(scale=.3)),
                t(Y[i] + rng.normal(scale=.3))])
isi = buf.getvalue().encode()

batas = '----WULAN'
body = (b'--' + batas.encode() + b'\r\n'
        b'Content-Disposition: form-data; name="berkas"; filename="med.csv"\r\n'
        b'Content-Type: text/csv\r\n\r\n' + isi + b'\r\n'
        b'--' + batas.encode() + b'--\r\n')
req = urllib.request.Request(
    BASE + '/api/diagnosis/unggah', data=body,
    headers={'Content-Type': 'multipart/form-data; boundary=' + batas})
with urllib.request.urlopen(req, timeout=120) as r:
    up = json.loads(r.read().decode())
kunci = up.get('kunci')
print('   kunci:', (kunci or '')[:12] + '…')
print('   jumlah kolom:', len(up.get('kolom') or []))

PERAN = {'X1a': 'X1', 'X1b': 'X1', 'X1c': 'X1',
         'M1a': 'M1', 'M1b': 'M1', 'M1c': 'M1',
         'Y1a': 'Y1', 'Y1b': 'Y1', 'Y1c': 'Y1'}

print('\n' + KEPALA)
print(' 3) PERIKSA PERAN (X1=3 kolom, M1=3, Y1=3)')
print(KEPALA)
pp = kirim('/api/diagnosis/periksa-peran', {'kunci': kunci, 'peran': PERAN})
print('   kelompok:', pp.get('kelompok'))
print('   masalah  :', pp.get('masalah'))
print('   tanya    :', pp.get('tanya'))

print('\n' + KEPALA)
print(' 4) HITUNG (rute /api/diagnosis/periksa) — APA YANG KELUAR?')
print(KEPALA)
jaw = kirim('/api/diagnosis/periksa',
            {'kunci': kunci, 'mode': 'spss', 'peran': PERAN, 'missing': 'buang'})
print('   KUNCI jawaban:', sorted(jaw.keys()))
print()
print('   prediktor yang dipakai mesin :', jaw.get('prediktor'))
print('   perantara (kolom_m)          :', jaw.get('perantara'))
print()
r2 = jaw.get('r2')
print('   R²       :', r2)
bersama = jaw.get('bersama') or []
print('   bersama  :')
for b in bersama:
    print('      ', {k: b.get(k) for k in ('nama', 'diminta', 'terbaca', 't', 'p')
                     if k in b})
print('   kunci koefisien:', sorted(bersama[0].keys()) if bersama else '-')
print()
# Cari jejak mediasi
teks = json.dumps(jaw).lower()
print('   ADA kata "tidak langsung"/indirect? :',
      ('tidak langsung' in teks) or ('indirect' in teks))
print('   ADA kata "sobel"?                    :', 'sobel' in teks)
print('   ADA kata "interaksi"/"moderasi"?     :',
      ('interaksi' in teks) or ('moderasi' in teks))
print('   ADA "a x b" / efek?                  :',
      ('efek' in teks) or ('a*b' in teks))
