"""UJI PINTU PRODUKSI: mediasi BERJENJANG + moderasi, pakai cara unggah yang TERBUKTI."""
import sys, json, urllib.request, csv, io
import numpy as np, pandas as pd
sys.path.insert(0, '/opt/data/services/statistik-lab')
B = 'http://127.0.0.1:8122'; GAGAL = 0
def cek(n, s, b=''):
    global GAGAL
    print(f"  {'✅' if s else '❌'} {n}" + (f'   {b}' if b else ''))
    if not s: GAGAL += 1
def _http(p, kirim=None, body=None, tipe='application/json'):
    req = urllib.request.Request(B+p, data=(body if body is not None
        else (json.dumps(kirim).encode() if kirim is not None else None)),
        headers={'Content-Type': tipe})
    with urllib.request.urlopen(req, timeout=240) as r:
        return json.loads(r.read().decode())
def unggah(header, baris, nama='d.csv'):
    b = io.StringIO(); w = csv.writer(b); w.writerow(header); w.writerows(baris)
    isi = b.getvalue().encode(); batas = '----WULAN'
    body = (b'--'+batas.encode()+b'\r\nContent-Disposition: form-data; '
            b'name="berkas"; filename="'+nama.encode()+b'"\r\n'
            b'Content-Type: text/csv\r\n\r\n' + isi + b'\r\n--'+batas.encode()+b'--\r\n')
    return _http('/api/diagnosis/unggah', body=body,
                 tipe='multipart/form-data; boundary='+batas)

rng = np.random.default_rng(9); n = 300
X = rng.normal(size=n); M1 = .6*X + rng.normal(scale=.8, size=n)
M2 = .15*X + .55*M1 + rng.normal(scale=.8, size=n)
Y = .05*X + .1*M1 + .5*M2 + rng.normal(scale=.8, size=n)
baris = [[round(float(v),4) for v in r] for r in zip(X,M1,M2,Y)]

print('='*70); print(' A. MEDIASI BERJENJANG lewat PINTU PRODUKSI'); print('='*70)
up = unggah(['X1a','X1b','M1a','M1b','M2a','M2b','Y1a','Y1b'],
            [[b[0],b[0],b[1],b[1],b[2],b[2],b[3],b[3]] for b in baris])
P = {'X1a':'X1','X1b':'X1','M1a':'M1','M1b':'M1','M2a':'M2','M2b':'M2',
     'Y1a':'Y1','Y1b':'Y1'}
print('  kolom:', str([k['nama'] for k in up.get('kolom',[])])[:70])
r = _http('/api/diagnosis/periksa', {'kunci': up.get('kunci'), 'mode': 'spss',
    'peran': P, 'missing': 'buang', 'bentuk_mediasi': 'berjenjang'})
k = r.get('kaitan') or {}
cek('kaitan ADA di jawaban server', bool(k.get('ada')), str(k.get('ada')))
cek('server TERIMA bentuk berjenjang dari halaman',
    k.get('bentuk_mediasi') == 'berjenjang', str(k.get('bentuk_mediasi')))
med = (k.get('mediasi') or [{}])[0]
cek('hasil pakai fungsi berjenjang', med.get('berjenjang') is True)
cek('ada 2 jalur tidak langsung', len(med.get('jalur') or []) == 2,
    str([j.get('nama') for j in (med.get('jalur') or [])]))
jr = (med.get('jalur') or [{},{}])[1]
cek('jalur rantai penuh SIGNIFIKAN', jr.get('signifikan') is True,
    f"b={jr.get('b')} lo={jr.get('lo')} hi={jr.get('hi')}")
cek('kalimat simpulan terisi', len(str(med.get('kalimat') or '')) > 40,
    str(med.get('kalimat'))[:70])

print('\n'+'='*70); print(' B. MODERASI lewat PINTU PRODUKSI'); print('='*70)
Xm = rng.normal(size=n); Z = rng.normal(size=n)
Ym = .5*Xm + .35*Xm*Z + rng.normal(scale=.8, size=n)
up2 = unggah(['X1a','X1b','Z1a','Z1b','Y1a','Y1b'],
             [[round(float(a),4),round(float(a),4),round(float(b),4),
               round(float(b),4),round(float(c),4),round(float(c),4)]
              for a,b,c in zip(Xm,Z,Ym)])
P2 = {'X1a':'X1','X1b':'X1','Z1a':'Z1','Z1b':'Z1','Y1a':'Y1','Y1b':'Y1'}
r2 = _http('/api/diagnosis/periksa', {'kunci': up2.get('kunci'), 'mode': 'spss',
    'peran': P2, 'missing': 'buang'})
k2 = r2.get('kaitan') or {}
cek('kaitan moderasi ADA', bool(k2.get('moderasi')), str(len(k2.get('moderasi') or [])))
mo = (k2.get('moderasi') or [{}])[0]
cek('Z tercatat sebagai penguat', mo.get('z') == 'Z1', str(mo.get('z')))
it = (mo.get('dengan_interaksi') or {}).get('interaksi') or {}
cek('interaksi X×Z signifikan',
    it.get('b') is not None and it.get('p') is not None and float(it.get('p')) < 0.05,
    f"b={it.get('b')} p={it.get('p')}")
cek('kalimat moderasi terisi', len(str(mo.get('kalimat') or '')) > 30,
    str(mo.get('kalimat'))[:60])

print('\n'+'='*70)
if GAGAL: print(f' ❌ ADA GAGAL: {GAGAL}'); sys.exit(1)
print(' ✅ LULUS SEMUA — berjenjang & moderasi sampai ke jawaban server')
sys.exit(0)
