"""UJI PINTU PRODUKSI — RANTAI PANJANG (>2 perantara) sampai ke HASIL.

Latar: ACC Bos 21Sep26 — *"Rantai lebih 2 perantara belum"*.

CARA UJI: lewat PINTU PRODUKSI — unggah berkas .csv sungguhan ke rute HTTP,
tandai peran, minta bentuk 'berjenjang' dengan **3 perantara**, lalu periksa
apakah server benar-benar mengeluarkan 3 jalur tidak langsung (bukan 2).
Halaman juga harus menerima kunci `rantai_panjang` + `d_semua`/`b_semua`.
"""
import sys
import json
import urllib.request
import csv
import io
import numpy as np

sys.path.insert(0, '/opt/data/services/statistik-lab')
B = 'http://127.0.0.1:8122'
GAGAL = 0


def cek(n, s, b=''):
    global GAGAL
    print(f"  {'✅' if s else '❌'} {n}" + (f'   {b}' if b else ''))
    if not s:
        GAGAL += 1


def _http(p, kirim=None, body=None, tipe='application/json'):
    req = urllib.request.Request(
        B + p,
        data=(body if body is not None
              else (json.dumps(kirim).encode() if kirim is not None else None)),
        headers={'Content-Type': tipe})
    with urllib.request.urlopen(req, timeout=240) as r:
        return json.loads(r.read().decode())


def unggah(header, baris, nama='d.csv'):
    b = io.StringIO()
    w = csv.writer(b)
    w.writerow(header)
    w.writerows(baris)
    isi = b.getvalue().encode()
    batas = '----WULAN'
    body = (b'--' + batas.encode() + b'\r\n'
            b'Content-Disposition: form-data; name="berkas"; filename="'
            + nama.encode() + b'"\r\nContent-Type: text/csv\r\n\r\n'
            + isi + b'\r\n--' + batas.encode() + b'--\r\n')
    return _http('/api/diagnosis/unggah', body=body,
                 tipe='multipart/form-data; boundary=' + batas)


# ── Data: X → M1(0,60) → M2(0,55) → M3(0,50) → Y(0,45) ──
n = 300
rng = np.random.default_rng(11)
X = rng.normal(size=n)
M1 = 0.60 * X + rng.normal(scale=0.8, size=n)
M2 = 0.10 * X + 0.55 * M1 + rng.normal(scale=0.8, size=n)
M3 = 0.05 * X + 0.10 * M1 + 0.50 * M2 + rng.normal(scale=0.8, size=n)
Y = 0.03 * X + 0.05 * M1 + 0.08 * M2 + 0.45 * M3 + rng.normal(scale=0.8, size=n)

# 2 kolom per peran (seperti mahasiswa mengunggah item kuesioner)
baris = [[round(float(X[i]), 4), round(float(X[i]), 4),
          round(float(M1[i]), 4), round(float(M1[i]), 4),
          round(float(M2[i]), 4), round(float(M2[i]), 4),
          round(float(M3[i]), 4), round(float(M3[i]), 4),
          round(float(Y[i]), 4), round(float(Y[i]), 4)] for i in range(n)]

print('=' * 70)
print(' RANTAI 3 PERANTARA lewat PINTU PRODUKSI')
print('=' * 70)
up = unggah(['X1a', 'X1b', 'M1a', 'M1b', 'M2a', 'M2b',
             'M3a', 'M3b', 'Y1a', 'Y1b'], baris)
P = {'X1a': 'X1', 'X1b': 'X1',
     'M1a': 'M1', 'M1b': 'M1',
     'M2a': 'M2', 'M2b': 'M2',
     'M3a': 'M3', 'M3b': 'M3',
     'Y1a': 'Y1', 'Y1b': 'Y1'}
print('  kolom:', str([k['nama'] for k in up.get('kolom', [])])[:80])
jw = _http('/api/diagnosis/periksa',
           {'kunci': up.get('kunci'), 'mode': 'spss', 'peran': P,
            'missing': 'buang', 'bentuk_mediasi': 'berjenjang'})

k = jw.get('kaitan') or {}
cek('kunci "kaitan" ADA', bool(k.get('ada')), str(k.get('ada')))
cek('server TERIMA bentuk berjenjang',
    k.get('bentuk_mediasi') == 'berjenjang', str(k.get('bentuk_mediasi')))
med = (k.get('mediasi') or [{}])[0]
cek('hasil ditandai rantai_panjang', med.get('rantai_panjang') is True)
cek('jumlah_perantara = 3', med.get('jumlah_perantara') == 3,
    str(med.get('jumlah_perantara')))
cek('ADA 3 jalur tidak langsung (dulu cuma 2)',
    len(med.get('jalur') or []) == 3, f"→ {len(med.get('jalur') or [])}")
nama = [j.get('nama') for j in (med.get('jalur') or [])]
cek('jalur 3 = X1 → M1 → M2 → M3 → Y1',
    'X1 → M1 → M2 → M3 → Y1' in nama, str(nama))
cek('TIDAK ada lagi catatan "belum"', 'catatan' not in med,
    str(med.get('catatan'))[:60])
cek('d_semua berisi 2 langkah (M1→M2, M2→M3)',
    len(med.get('d_semua') or []) == 2, f"→ {len(med.get('d_semua') or [])}")
cek('b_semua berisi 3 jalur ke Y',
    len(med.get('b_semua') or []) == 3, f"→ {len(med.get('b_semua') or [])}")
cek('kalimat simpulan terisi', len(str(med.get('kalimat') or '')) > 40,
    str(med.get('kalimat'))[:70])
j3 = [j for j in (med.get('jalur') or []) if 'M2 → M3' in str(j.get('nama'))]
cek('jalur terpanjang SIGNIFIKAN',
    bool(j3) and j3[0].get('signifikan') is True,
    f"b={j3[0].get('b') if j3 else None}")

print()
print('=' * 70)
print(' 4 PERANTARA lewat PINTU PRODUKSI')
print('=' * 70)
rng2 = np.random.default_rng(22)
X4 = rng2.normal(size=n)
A = 0.60 * X4 + rng2.normal(scale=0.8, size=n)
Bv = 0.55 * A + rng2.normal(scale=0.8, size=n)
C = 0.50 * Bv + rng2.normal(scale=0.8, size=n)
D = 0.45 * C + rng2.normal(scale=0.8, size=n)
Y4 = 0.03 * X4 + 0.40 * D + rng2.normal(scale=0.8, size=n)
baris4 = []
for i in range(n):
    r = []
    for v in (X4[i], A[i], Bv[i], C[i], D[i], Y4[i]):
        r += [round(float(v), 4), round(float(v), 4)]
    baris4.append(r)
hdr4 = []
P4 = {}
for kode in ('X1', 'M1', 'M2', 'M3', 'M4', 'Y1'):
    hdr4 += [kode + 'a', kode + 'b']
    P4[kode + 'a'] = kode
    P4[kode + 'b'] = kode
up4 = unggah(hdr4, baris4)
jw4 = _http('/api/diagnosis/periksa',
            {'kunci': up4.get('kunci'), 'mode': 'spss', 'peran': P4,
             'missing': 'buang', 'bentuk_mediasi': 'berjenjang'})
k4 = jw4.get('kaitan') or {}
m4 = (k4.get('mediasi') or [{}])[0]
cek('4 perantara: kaitan ada', bool(k4.get('ada')), str(k4.get('ada')))
cek('4 perantara: ADA 4 jalur', len(m4.get('jalur') or []) == 4,
    f"→ {len(m4.get('jalur') or [])}")

print()
print('=' * 70)
if GAGAL:
    print(f' ❌ ADA GAGAL: {GAGAL}')
    sys.exit(1)
print(' ✅ LULUS SEMUA — rantai >2 perantara sampai ke HASIL')
sys.exit(0)
