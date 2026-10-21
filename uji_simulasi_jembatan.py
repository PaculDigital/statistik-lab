"""Uji pintu simulasi jembatan (Fase 3 sisa): kunci, bentuk, kalibrasi.

Jalan: JEMBATAN_KUNCI_LAYANAN=kunci-uji python uji_simulasi_jembatan.py
"""
import os, sys
sys.path.insert(0, '.')
os.environ.setdefault('JEMBATAN_KUNCI_LAYANAN', 'kunci-uji')
from fastapi.testclient import TestClient
from app.main import app

k = TestClient(app, raise_server_exceptions=False)
H = {'X-Kunci-Layanan': 'kunci-uji', 'Content-Type': 'application/json'}
gagal = []
def cek(nama, kondisi, info=''):
    print(('  ✓ ' if kondisi else '  ✗ GAGAL ') + nama + ('' if kondisi else f' → {info}'))
    if not kondisi: gagal.append(nama)

minta = {'model': 'mediasi', 'n': 50,
         'nama': {'x': 'Harga', 'm': 'Kepuasan', 'y': 'Keputusan'},
         'params': {'a': 0.55, 'b': 0.45, 'langsung': 0.0},
         'konstruk': [{'kode': 'X', 'nama_kolom': 'Harga', 'butir': 4},
                      {'kode': 'M', 'nama_kolom': 'Kepuasan', 'butir': 3},
                      {'kode': 'Y', 'nama_kolom': 'Keputusan', 'butir': 4}]}
r = k.post('/api/jembatan/simulasi', json=minta, headers=H)
j = r.json() if r.status_code == 200 else {}
cek('mediasi: kolom sesuai peta & jumlah butir persis',
    j.get('kolom') == ['Harga_1', 'Harga_2', 'Harga_3', 'Harga_4',
                       'Kepuasan_1', 'Kepuasan_2', 'Kepuasan_3',
                       'Keputusan_1', 'Keputusan_2', 'Keputusan_3', 'Keputusan_4'],
    f"{r.status_code} {str(j)[:150]}")
cek('50 baris, semua nilai Likert 1–5',
    len(j.get('baris', [])) == 50 and all(1 <= s <= 5 for b in j['baris'] for s in b))
r = k.post('/api/jembatan/simulasi', json=minta, headers={'Content-Type': 'application/json'})
cek('tanpa kunci → 401', r.status_code == 401, str(r.status_code))
r = k.post('/api/jembatan/simulasi', json={**minta, 'model': 'ngawur'}, headers=H)
cek('model tak dikenal → 400', r.status_code == 400, str(r.status_code))
# data simulasi harus bisa DIHITUNG pintu utama (kalibrasi terbukti jalan)
r2 = k.post('/api/jembatan/hitung', headers=H, json={
    'tahap': 'utama', 'mode': 'spss', 'bentuk_mediasi': 'lengkap',
    'peran': {c: ('X1' if c.startswith('Harga') else 'M1' if c.startswith('Kepuasan') else 'Y1')
              for c in j['kolom']},
    'baris': [{c: v for c, v in zip(j['kolom'], b)} for b in j['baris']]})
cek('data simulasi terhitung pintu utama (a kuat → mediasi terbaca)',
    r2.status_code == 200 and bool(r2.json().get('kaitan', {}).get('mediasi')),
    f"{r2.status_code} {r2.text[:150]}")
print()
print('❌ GAGAL: ' + ', '.join(gagal) if gagal else '✅ SEMUA LULUS — pintu simulasi jembatan')
sys.exit(1 if gagal else 0)
